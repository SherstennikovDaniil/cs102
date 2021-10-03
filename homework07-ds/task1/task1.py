import typing as tp
from pprint import pprint

import psycopg2
import psycopg2.extras
from tabulate import tabulate

conn = psycopg2.connect("host=localhost port=5432 dbname=odscourse user=postgres password=secret")

cursor = conn.cursor()