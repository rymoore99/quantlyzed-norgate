import json
import urllib.request
from datetime import datetime
from datetime import date
from datetime import timedelta
import requests, os
from dotenv import load_dotenv, find_dotenv
import psycopg2
from psycopg2.extensions import AsIs
import psycopg2.extras


def get_local_cursor():
    url = '192.168.86.23:5432'
    local_pw = os.environ['PG_PW']

    dsn2 = f"postgresql://postgres:{local_pw}@{url}/quantlyzed"
    connection = psycopg2.connect(dsn2)
    connection.autocommit = True
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    return cursor


def insert_dict(t, table_name, cursor):
    columns = t.keys()
    cols_s = []
    for c in columns:
        cols_s.append(f'"{c}"')

    values = [t[column] for column in columns]

    insert_statement = f'insert into {table_name} (%s) values %s'

    sql = cursor.mogrify(insert_statement, (AsIs(','.join(cols_s)), tuple(values)))

    cursor.execute(sql)


def convert_nested_to_string(input_list):
    for i, element in enumerate(input_list):
        if isinstance(element, (list, dict)):
            input_list[i] = str(element)
    return input_list


def insert_dict(t, table_name, cursor):
    columns = t.keys()
    cols_s = []
    for c in columns:
        cols_s.append(f'"{c}"')

    values = [t[column] for column in columns]

    values = convert_nested_to_string(values)

    insert_statement = f'insert into {table_name} (%s) values %s'

    sql = cursor.mogrify(insert_statement, (AsIs(','.join(cols_s)), tuple(values)))

    cursor.execute(sql)

