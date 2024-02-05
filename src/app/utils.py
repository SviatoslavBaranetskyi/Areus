from mysql.connector import connect


def get_database_connection(request):
    return connect(
        host=request.session['host'],
        user=request.session['username'],
        password=request.session['password'],
        database=request.query_params.get('database')
    )


def close_database_connection(connection, cursor):
    cursor.close()
    connection.close()


def execute_query(connection, query):
    cursor = connection.cursor()
    cursor.execute(query)
    return cursor
