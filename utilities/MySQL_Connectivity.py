import pymysql
import pandas as pd
def connectivity(db_name,db_host,db_username,db_password):
    """This utility function will setup connection between mysql and python:
    Args:
        db_name (str): database name
        db_host (str): database hostname
        db_username (str): database username
        db_password (str): database password
    Returns:
        dataframe: read 1 table from database
    """
    conn = pymysql.connect(
            host = db_host,
            port = int(3306),
            user = "root",
            password = db_password,
            db = db_name)

    Submissions =  pd.read_sql_query("Select * from Submissions",conn)

    conn.close()

    return Submissions
