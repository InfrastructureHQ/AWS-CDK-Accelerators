import sys
import os
import boto3
import json
import datetime
import time

from aws_lambda_powertools import Logger

#logger
logger = Logger(service="Event Info")


# initialize redshift-data client in boto3
redshift_client = boto3.client("redshift-data")

def call_data_api(redshift_client, redshift_database, redshift_user, redshift_cluster_id, sql_statement):
    
    try:
        # execute the input SQL statement
        call_api_response = redshift_client.execute_statement(Database=redshift_database, DbUser=redshift_user
                                                        ,Sql=sql_statement, ClusterIdentifier=redshift_cluster_id)
        
        query_id = call_api_response["Id"]
        done = False
        while not done:
            time.sleep(1)
            status = status_check(redshift_client, query_id)
            print('Status+++++++++++',status)
            if status in ("STARTED", "FAILED", "FINISHED"):
                response = redshift_client.get_statement_result(Id=query_id)
                print('Response==========',response["Records"])
                break
        return query_id
    
    except Exception as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("exp:--", ex)
        print("line_number----", exc_tb.tb_lineno)

def status_check(redshift_client, query_id):
    
    try:
        desc = redshift_client.describe_statement(Id=query_id)
        status = desc["Status"]
        if status == "FAILED":
            raise Exception('SQL query failed:' + query_id + ": " + desc["Error"])
        return status.strip('"')
        
    except Exception as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("exp:--", ex)
        print("line_number----", exc_tb.tb_lineno)    

def lambda_handler(event, context):
    
    
    try:
        redshift_cluster_id = 'clinicaltrialsiqredshiftclusterafd94c8d-s68xt4hqqscm'
        redshift_database = 'clinicaltrialsiq'
        redshift_user = 'redshift-user'
        
        # sql report query to be submitted
        sql_statement = "select * from information_schema.sql_packages limit 10"
        api_response = call_data_api(redshift_client, redshift_database, redshift_user, redshift_cluster_id, sql_statement)
        
    except Exception as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("exp:--", ex)
        print("line_number----", exc_tb.tb_lineno)
