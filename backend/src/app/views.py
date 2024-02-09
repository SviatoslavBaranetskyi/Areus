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


@method_decorator(require_session, name="dispatch")
class TableRowsView(APIView):
    def get(self, request):
        database_name = request.query_params.get('database')
        table_name = request.query_params.get('table')

        try:
            connection = get_database_connection(request)
            cursor = execute_query(connection, f"SELECT * FROM {database_name}.{table_name}")

            columns = [desc[0] for desc in cursor.description]
            rows = [list(row) for row in cursor.fetchall()]

            close_database_connection(connection, cursor)

            data = {
                'columns': columns,
                'rows': rows
            }

            return Response(data, status=status.HTTP_200_OK)

        except Error as e:
            return Response({'error': f'Error fetching rows: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        database_name = request.data.get('database')
        table_name = request.data.get('table')
        data = request.data.get('data')

        try:
            connection = get_database_connection(request)
            cursor = connection.cursor()

            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            insert_query = f"INSERT INTO {database_name}.{table_name} ({columns}) VALUES ({placeholders})"

            cursor.execute(insert_query, list(data.values()))

            connection.commit()
            cursor.close()

            close_database_connection(connection, cursor)

            return Response({'message': 'Row added successfully'}, status=status.HTTP_201_CREATED)

        except Error as e:
            return Response({'error': f'Error adding row: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        database_name = request.data.get('database')
        table_name = request.data.get('table')
        column = request.data.get('column')
        value = request.data.get('value')
        unique_column = request.data.get('unique_column')
        position = request.data.get('position')

        try:
            connection = get_database_connection(request)
            cursor = connection.cursor()

            cursor.execute(f"SHOW KEYS FROM {database_name}.{table_name} WHERE Key_name = 'PRIMARY'")
            primary_key_info = cursor.fetchone()

            if not primary_key_info:
                return Response({'error': 'You cannot edit data in this table because you dont have a unique column. '
                                          'Please set the primary key to a unique column'},
                                status=status.HTTP_400_BAD_REQUEST)

            primary_key_columns = primary_key_info[4].split(',')

            if unique_column not in primary_key_columns:
                return Response({'error': f'Unique column is not the primary key of the table. Use one of these: {primary_key_columns}'},
                                status=status.HTTP_400_BAD_REQUEST)

            update_query = f"UPDATE {database_name}.{table_name} SET {column} = %s WHERE {unique_column} = %s"

            cursor.execute(update_query, (value, position))

            connection.commit()
            cursor.close()

            close_database_connection(connection, cursor)

            return Response({'message': 'success'}, status=status.HTTP_200_OK)

        except Error as e:
            return Response({'error': f'Error updating row: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        database_name = request.data.get('database')
        table_name = request.data.get('table')
        unique_column = request.data.get('unique_column')
        position = request.data.get('position')

        try:
            connection = get_database_connection(request)
            cursor = connection.cursor()

            if not unique_column:
                return Response({'error': 'Unique column not specified'}, status=status.HTTP_400_BAD_REQUEST)

            delete_query = f"DELETE FROM {database_name}.{table_name} WHERE {unique_column} = %s"

            cursor.execute(delete_query, (position,))

            connection.commit()
            cursor.close()

            close_database_connection(connection, cursor)

            return Response({'message': 'Row deleted successfully'}, status=status.HTTP_200_OK)

        except Error as e:
            return Response({'error': f'Error deleting row: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
