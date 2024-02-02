from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from mysql.connector import connect, Error
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .forms import LoginForm
from .decorators import require_session


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            host = form.cleaned_data['host']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                db = connect(host=host, username=username, password=password)
            except:
                return HttpResponseRedirect(request.path_info)

            request.session['host'] = host
            request.session['username'] = username
            request.session['password'] = password

            return HttpResponseRedirect('/')

    form = LoginForm()
    return render(request, 'app/login.html', {'form': form})


@method_decorator(require_session, name="dispatch")
class MainPageView(View):
    def get(self, request):
        host = request.session.get('host')
        username = request.session.get('username')
        password = request.session.get('password')

        return render(request, 'app/main.html', {
            'Host': host,
            'Username': username,
            'Password': password
        })


@method_decorator(require_session, name="dispatch")
class GetDatabasesView(APIView):
    def get(self, request):
        try:
            db = connect(
                host=request.session['host'],
                username=request.session['username'],
                password=request.session['password']
            )
            cursor = db.cursor()

            # Execute query to get list of databases
            cursor.execute("SHOW DATABASES")

            # Fetch all databases
            databases = cursor.fetchall()

            # Close the cursor and connection
            cursor.close()
            db.close()

            # Serialize the data
            formatted_data = {
                'databases': [db[0] for db in databases],
                'host': request.session['host']
            }

            return Response(formatted_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(require_session, name="dispatch")
class GetTablesView(APIView):
    def get(self, request):
        database_name = request.query_params.get('database')

        try:
            connection = connect(
                host=request.session['host'],
                user=request.session['username'],
                password=request.session['password'],
                database=database_name
            )

            cursor = connection.cursor()

            cursor.execute("SHOW TABLES")

            # Fetch all tables
            tables = [table[0] for table in cursor.fetchall()]

            data = {
                'database': database_name,
                'tables': {}
            }

            for table in tables:
                # Information about each table
                table_info_query = f"SHOW TABLE STATUS LIKE '{table}'"
                cursor.execute(table_info_query)
                table_data = cursor.fetchone()

                # Extract relevant information
                rows_count = table_data[4]
                data_length = table_data[6]
                collation = table_data[14]

                # Add table information to the data dictionary
                data['tables'][table] = {
                    'rows': rows_count,
                    'size': data_length,
                    'collation': collation
                }

            # Close the cursor and connection
            cursor.close()
            connection.close()

            return Response(data, status=status.HTTP_200_OK)

        except Error as e:
            return Response({'error': f'Error fetching tables: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

