import sys
import boto3

client = boto3.client('athena')

SOURCE_TABLE_NAME = 'de_abe_project_polygon_stocks_dec2024'
NEW_TABLE_NAME = 'de_abe_project_polygon_stocks_dec2024_pq'
NEW_TABLE_S3_BUCKET = 's3://de-abe-project-polygon-stocks-dec2024-pq/'
MY_DATABASE = 'de_stock_data_dec2024'
QUERY_RESULTS_S3_BUCKET = 's3://de-abe-project-polygon-stocks-query-result-dec2024'

# Refresh the table
queryStart = client.start_query_execution(
    QueryString = f"""
    CREATE TABLE {NEW_TABLE_NAME} WITH
    (external_location='{NEW_TABLE_S3_BUCKET}',
    format='PARQUET',
    write_compression='SNAPPY',
    partitioned_by = ARRAY['yr_mo_partition'])
    AS

    SELECT
        ticker
        ,close_val
        ,close_date
        ,SUBSTRING(close_date,1,7) AS yr_mo_partition
    FROM "{MY_DATABASE}"."{SOURCE_TABLE_NAME}"

    ;
    """,
    QueryExecutionContext = {
        'Database': f'{MY_DATABASE}'
    }, 
    ResultConfiguration = { 'OutputLocation': f'{QUERY_RESULTS_S3_BUCKET}'}
)

# list of responses
resp = ["FAILED", "SUCCEEDED", "CANCELLED"]

# get the response
response = client.get_query_execution(QueryExecutionId=queryStart["QueryExecutionId"])

# wait until query finishes
while response["QueryExecution"]["Status"]["State"] not in resp:
    response = client.get_query_execution(QueryExecutionId=queryStart["QueryExecutionId"])
    
# if it fails, exit and give the Athena error message in the logs
if response["QueryExecution"]["Status"]["State"] == 'FAILED':
    sys.exit(response["QueryExecution"]["Status"]["StateChangeReason"])
