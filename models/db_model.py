import mysql.connector
from mysql.connector import Error

def connect(setting):

    try:
        connection = mysql.connector.connect(**setting)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    return None


def execute_the_query_with_names(connection, sql_query):

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            values = cursor.fetchall()
            column_names = [column[0] for column in cursor.description]
            return [column_names, values]
    except Error as e:
        print(f"Error while executing the query: {e}")
        return None


def execute_the_query(connection, sql_query):

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            return cursor.fetchall()
    except Error as e:
        print(f"Error while executing the query: {e}")
        return None


def close_connection(connection):

    try:
        if connection.is_connected():
            connection.close()
            print("MySQL connection is closed")
    except Error as e:
        print(f"Error while closing the connection: {e}")
