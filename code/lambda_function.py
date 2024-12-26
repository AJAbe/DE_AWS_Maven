import json
import boto3
import urllib3
import datetime
from botocore.exceptions import ClientError
import json
from datetime import date

# REPLACE WITH YOUR DATA FIREHOSE NAME
FIREHOSE_NAME = 'PUT-S3-NcWgS'

def get_secret():

    secret_name = "polygon_stock_abe"
    region_name = "us-east-1"
    

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e
        
    ret_secret = json.loads(get_secret_value_response['SecretString'])[secret_name]

    return ret_secret

def lambda_handler(event, context):
    
    
    http = urllib3.PoolManager()
    
    url= "https://api.polygon.io/v2/aggs/ticker/META/range/1/day/2024-06-01/2024-12-15?adjusted=true&sort=asc&apiKey=" + get_secret()
    url_google= "https://api.polygon.io/v2/aggs/ticker/GOOG/range/1/day/2024-06-01/2024-12-15?adjusted=true&sort=asc&apiKey=" + get_secret()
    #print(url)
    
    # run for Facebook first
    
    r = http.request("GET", url)
    
    # turn it into a dictionary
    
    r_dict = json.loads(r.data.decode(encoding='utf-8', errors='strict'))
    
    #ticker=r_dict['ticker']

    close_val_dict = {}
    
    records_to_push = []
    format = '%Y-%m-%d'
    
    for temp in r_dict['results']:
    
    # handle null values
    # if we don't, the crawler may get confused
        close_val_dict['ticker']=r_dict['ticker']
        close_val_dict['close_val']=float(temp['c'])
        close_val_dict['close_date']=datetime.datetime.fromtimestamp(temp['t']/1000).strftime('%Y-%m-%d')
        
    
        msg = str(close_val_dict) + '\n'
        records_to_push.append({'Data': msg})
    
    # inserting null rows for capturing via Glue
    
    # next Google
    
    r = http.request("GET", url_google)
    
    # turn it into a dictionary
    
    r_dict = json.loads(r.data.decode(encoding='utf-8', errors='strict'))
    
    
    for temp in r_dict['results']:
    
    # handle null values
    # if we don't, the crawler may get confused
        close_val_dict['ticker']=r_dict['ticker']
        close_val_dict['close_val']=float(temp['c'])
        close_val_dict['close_date']=datetime.datetime.fromtimestamp(temp['t']/1000).strftime('%Y-%m-%d')
        
    
        msg = str(close_val_dict) + '\n'
        records_to_push.append({'Data': msg})
    
    
    fh = boto3.client('firehose')
    
    reply = fh.put_record_batch(
        DeliveryStreamName=FIREHOSE_NAME,
        Records = records_to_push
    )

    return reply