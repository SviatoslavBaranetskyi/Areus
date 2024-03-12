from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.base import TemplateView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from mysql.connector import connect, Error
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .forms import LoginForm
from .decorators import require_session
from .utils import get_database_connection, close_database_connection, execute_query


class LoginView(APIView):
    @swagger_auto_schema(
        operation_description="Get login form",
        responses={
            status.HTTP_200_OK: openapi.Response(description="Login form HTML"),
        }
    )
    def get(self, request):
        form = LoginForm()
        return render(request, 'app/login.html', {'form': form})

    @swagger_auto_schema(
        operation_description="User Login",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['host', 'username', 'password'],
            properties={
                'host': openapi.Schema(type=openapi.TYPE_STRING, description="Database host"),
                'username': openapi.Schema(type=openapi.TYPE_STRING, description="Database username"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description="Database password")
            }
        ),
        responses={
            status.HTTP_302_FOUND: "Redirect to home page",
            status.HTTP_400_BAD_REQUEST: "Bad request"
        }
    )
    def post(self, request):
        form = LoginForm(request.data)
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
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


def logout(request):
    request.session.flush()
    return HttpResponseRedirect('/login')


@method_decorator(require_session, name="dispatch")
class MainPageView(TemplateView):
    template_name = 'app/main.html'


@method_decorator(require_session, name="dispatch")
class DatabasesView(APIView):

    @swagger_auto_schema(
        operation_description="Retrieve list of databases",
        responses={status.HTTP_200_OK: openapi.Schema(type=openapi.TYPE_OBJECT)},
    )
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

    @swagger_auto_schema(
        operation_description="Create a new database",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['database'],
            properties={
                'database': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the database to create")
            }
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Schema(type=openapi.TYPE_OBJECT),
            status.HTTP_400_BAD_REQUEST: "Bad request"
        }
    )
    def post(self, request):
        database_name = request.data.get('database')

        try:
            connection = get_database_connection(request)
            cursor = connection.cursor()

            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")

            if not cursor.fetchone():
                return Response({'error': 'Database already exists'}, status=status.HTTP_400_BAD_REQUEST)

            close_database_connection(connection, cursor)

            return Response({'message': 'Database created successfully'}, status=status.HTTP_201_CREATED)

        except Error as e:
            return Response({'error': f'Error creating database: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Delete a database",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['database'],
            properties={
                'database': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the database to delete")
            }
        ),
        responses={
            status.HTTP_200_OK: openapi.Schema(type=openapi.TYPE_OBJECT),
            status.HTTP_400_BAD_REQUEST: "Bad request"
        }
    )
    def delete(self, request):
        database_name = request.data.get('database')

        try:
            connection = get_database_connection(request)
            cursor = connection.cursor()

            cursor.execute(f"DROP DATABASE IF EXISTS {database_name}")

            close_database_connection(connection, cursor)

            return Response({'message': 'Database deleted successfully'}, status=status.HTTP_200_OK)

        except Error as e:
            return Response({'error': f'Error deleting database: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(require_session, name="dispatch")
class TablesView(APIView):

    @swagger_auto_schema(
        operation_description="Retrieve list of tables",
        manual_parameters=[
            openapi.Parameter(
                'database', openapi.IN_QUERY, description="Name of the database to retrieve tables from",
                type=openapi.TYPE_STRING
            )
        ],
        responses={status.HTTP_200_OK: openapi.Schema(type=openapi.TYPE_OBJECT)},
    )
    def get(self, request):
        try:
            connection = get_database_connection(request)
            cursor = execute_query(connection, "SHOW TABLES")

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

                data['tables'][table] = {
                    'rows': rows_count,
                    'size': data_length,
                    'collation': collation
                }

            close_database_connection(connection, cursor)

            return Response(data, status=status.HTTP_200_OK)

        except Error as e:
            return Response({'error': f'Error fetching tables: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new table",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['database', 'table', 'fields'],
            properties={
                'database': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the database"),
                'table': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the table to create"),
                'fields': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'name': openapi.Schema(type=openapi.TYPE_STRING, description="Field name"),
                            'data_type': openapi.Schema(type=openapi.TYPE_STRING, description="Field data type"),
                            'allow_null': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Whether field allows null values"),
                            'primary_key': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Whether field is primary key"),
                        }
                    )
                )
            }
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Schema(type=openapi.TYPE_OBJECT),
            status.HTTP_400_BAD_REQUEST: "Bad request"
        }
    )
    def post(self, request):
        database_name = request.data.get('database')
        table_name = request.data.get('table')
        fields = request.data.get('fields')  # List of fields that the user enters through the form

        try:
            connection = get_database_connection(request)
            cursor = connection.cursor()

            create_table_query = f"CREATE TABLE IF NOT EXISTS {database_name}.{table_name} ("

            for field in fields:
                field_name = field.get('name')
                data_type = field.get('data_type')
                allow_null = field.get('allow_null', True)
                primary_key = field.get('primary_key', False)

                create_table_query += f"{field_name} {data_type}"

                if not allow_null:
                    create_table_query += " NOT NULL"

                if primary_key:
                    create_table_query += " PRIMARY KEY"

                create_table_query += ","

            # Removing the last comma and ending the SQL query
            create_table_query = create_table_query.rstrip(",")
            create_table_query += ");"

            cursor.execute(create_table_query)

            close_database_connection(connection, cursor)

            return Response({'message': 'Table created successfully'}, status=status.HTTP_201_CREATED)

        except Error as e:
            return Response({'error': f'Error creating table: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Delete a table",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['database', 'table'],
            properties={
                'database': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the database"),
                'table': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the table to delete")
            }
        ),
        responses={
            status.HTTP_200_OK: openapi.Schema(type=openapi.TYPE_OBJECT),
            status.HTTP_400_BAD_REQUEST: "Bad request"
        }
    )
    def delete(self, request):
        database_name = request.data.get('database')
        table_name = request.data.get('table')

        try:
            connection = get_database_connection(request)
            cursor = connection.cursor()

            cursor.execute(f"DROP TABLE IF EXISTS {database_name}.{table_name}")

            close_database_connection(connection, cursor)

            return Response({'message': 'Table deleted successfully'}, status=status.HTTP_200_OK)

        except Error as e:
            return Response({'error': f'Error deleting table: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(require_session, name="dispatch")
class TableRowsView(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve rows from a table",
        manual_parameters=[
            openapi.Parameter(
                'database', openapi.IN_QUERY, description="Name of the database", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'table', openapi.IN_QUERY, description="Name of the table", type=openapi.TYPE_STRING
            )
        ],
        responses={status.HTTP_200_OK: openapi.Schema(type=openapi.TYPE_OBJECT)},
    )
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

    @swagger_auto_schema(
        operation_description="Add a new row to a table",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['database', 'table', 'data'],
            properties={
                'database': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the database"),
                'table': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the table"),
                'data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'column1': openapi.Schema(type=openapi.TYPE_STRING),
                        'column2': openapi.Schema(type=openapi.TYPE_STRING),
                        '...': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                )
            }
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Schema(type=openapi.TYPE_OBJECT),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error"
        }
    )
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

            close_database_connection(connection, cursor)

            return Response({'message': 'Row added successfully'}, status=status.HTTP_201_CREATED)

        except Error as e:
            return Response({'error': f'Error adding row: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update a row in a table",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['database', 'table', 'column', 'value', 'unique_column', 'position'],
            properties={
                'database': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the database"),
                'table': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the table"),
                'column': openapi.Schema(type=openapi.TYPE_STRING, description="Column to update"),
                'value': openapi.Schema(type=openapi.TYPE_STRING, description="New value for the column"),
                'unique_column': openapi.Schema(type=openapi.TYPE_STRING, description="Unique column identifier"),
                'position': openapi.Schema(type=openapi.TYPE_STRING, description="Position of the row to update")
            }
        ),
        responses={
            status.HTTP_200_OK: openapi.Schema(type=openapi.TYPE_OBJECT),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error"
        }
    )
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
                return Response({'error': 'To edit data in this table please set the primary key to a unique column'},
                                status=status.HTTP_400_BAD_REQUEST)

            primary_key_columns = primary_key_info[4].split(',')

            if unique_column not in primary_key_columns:
                return Response({'error': f'Unique column is not the primary key of the table. '
                                          f'Use one of these: {primary_key_columns}'},
                                status=status.HTTP_400_BAD_REQUEST)

            update_query = f"UPDATE {database_name}.{table_name} SET {column} = %s WHERE {unique_column} = %s"

            cursor.execute(update_query, (value, position))

            close_database_connection(connection, cursor)

            return Response({'message': 'success'}, status=status.HTTP_200_OK)

        except Error as e:
            return Response({'error': f'Error updating row: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Delete a row from a table",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['database', 'table', 'unique_column', 'position'],
            properties={
                'database': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the database"),
                'table': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the table"),
                'unique_column': openapi.Schema(type=openapi.TYPE_STRING, description="Unique column identifier"),
                'position': openapi.Schema(type=openapi.TYPE_STRING, description="Position of the row to delete")
            }
        ),
        responses={
            status.HTTP_200_OK: openapi.Schema(type=openapi.TYPE_OBJECT),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error"
        }
    )
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

            close_database_connection(connection, cursor)

            return Response({'message': 'Row deleted successfully'}, status=status.HTTP_200_OK)

        except Error as e:
            return Response({'error': f'Error deleting row: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserView(APIView):
    @swagger_auto_schema(
        operation_description="Get all users",
        responses={200: "List of users", 500: "Internal Server Error"}
    )
    def get(self, request):
        try:
            connection = get_database_connection(request)
            cursor = execute_query(connection, "SELECT User, Host FROM mysql.user")
            users_data = cursor.fetchall()
            users = []

            for user_data in users_data:
                user = {'user': user_data[0], 'host': user_data[1]}
                grants_cursor = execute_query(connection, f"SHOW GRANTS FOR '{user_data[0]}'@'{user_data[1]}'")
                grants = [grant[0] for grant in grants_cursor.fetchall()]
                user['grants'] = grants
                users.append(user)

            close_database_connection(connection, cursor)

            return Response(users, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description='Create a new User',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['host', 'username', 'password', 'privileges', 'databases', 'tables'],
            properties={
                'host': openapi.Schema(type=openapi.TYPE_STRING),
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'privileges': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING))
                ),
                'databases': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING))
                ),
                'tables': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING))
                ),
            },
        ),
        responses={200: 'User created successfully', 500: 'Error creating user'},
    )
    def post(self, request):
        try:
            host = request.data.get('host')
            username = request.data.get('username')
            password = request.data.get('password')
            privileges = request.data.get('privileges')
            databases = request.data.get('databases')
            tables = request.data.get('tables')

            connection = get_database_connection(request)
            cursor = connection.cursor()

            create_user_query = f"CREATE USER '{username}'@'{host}' IDENTIFIED BY '{password}'"
            cursor.execute(create_user_query)

            for i in range(len(databases)):
                database = databases[i][0]
                db_identifier = "*" if database == "All" else database

                for j in range(len(tables[i])):
                    table = tables[i][j]
                    table_identifier = "*" if table == "All" else table

                    privileges_str = "ALL PRIVILEGES" if privileges == "All" else ", ".join(privileges[i])

                    grant_query = f"GRANT {privileges_str} ON {db_identifier}.{table_identifier} TO '{username}'@'{host}' WITH GRANT OPTION"
                    cursor.execute(grant_query)

            close_database_connection(connection, cursor)

            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': f'Error creating user: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description='Delete a user',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['host', 'username'],
            properties={
                'host': openapi.Schema(type=openapi.TYPE_STRING),
                'username': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={200: "User deleted successfully", 500: "Internal Server Error"}
    )
    def delete(self, request):
        host = request.data.get('host')
        username = request.data.get('username')

        try:
            connection = get_database_connection(request)
            cursor = connection.cursor()
            cursor.execute(f"DROP USER '{username}'@'{host}'")

            close_database_connection(connection, cursor)

            return Response({'message': 'User deleted successfully'}, status=status.HTTP_200_OK)

        except Error as e:
            return Response({'error': f'Error deleting user: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
