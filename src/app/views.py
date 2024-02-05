from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.base import TemplateView
from mysql.connector import connect, Error
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .forms import LoginForm
from .decorators import require_session
from .utils import get_database_connection, close_database_connection, execute_query


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


def logout(request):
    request.session.flush()
    return HttpResponseRedirect('/login')


@method_decorator(require_session, name="dispatch")
class MainPageView(TemplateView):
    template_name = 'app/main.html'


@method_decorator(require_session, name="dispatch")
class GetDatabasesView(APIView):
    def get(self, request):
        try:
            db = get_database_connection(request)
            cursor = execute_query(db, "SHOW DATABASES")
            databases = cursor.fetchall()
            close_database_connection(db, cursor)

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
        try:
            connection = get_database_connection(request)
            cursor = execute_query(connection, "SHOW TABLES")

            # Fetch all tables
            tables = [table[0] for table in cursor.fetchall()]

            data = {
                'database': request.query_params.get('database'),
                'tables': {}
            }

            for table in tables:
                table_data = execute_query(connection, f"SHOW TABLE STATUS LIKE '{table}'").fetchone()

                rows_count = table_data[4]
                data_length = table_data[6]
                collation = table_data[14]

                # Add table information to the data dictionary
                data['tables'][table] = {
                    'rows': rows_count,
                    'size': data_length,
                    'collation': collation
                }

            close_database_connection(connection, cursor)

            return Response(data, status=status.HTTP_200_OK)

        except Error as e:
            return Response({'error': f'Error fetching tables: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
