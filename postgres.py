import os
import psycopg2

pg_host  = os.getenv('PG_HOST')
pg_port  = int(os.getenv('PG_PORT'))
pg_db    = os.getenv('PG_DB')
pg_user  = os.getenv('PG_USER')
pg_pass  = os.getenv('PG_PASSWORD')

def pg_sync():
    return psycopg2.connect(database=pg_db, user=pg_user,
            password=pg_pass, host=pg_host, port=pg_port)