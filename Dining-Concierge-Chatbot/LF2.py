import json
import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
import requests
import time
from requests_aws4auth import AWS4Auth

def lambda_handler(event, context):
    #def lambda_handler(event, context):
    # TODO implement
    print("******************")
    print(event)
    message_body = (event['Records'][0]["body"])
    print(message_body)
    message_body=message_body.replace("\'","\"")
    # print(message_body)
    res = json.loads(message_body)
    cusine=res['Cusine']
    print(cusine)
    # return {
        # 'statusCode': 200,
        # 'body': res
        
    # }
    
    credentials = boto3.Session().get_credentials()
    region = 'us-east-1'
    service = 'es'
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    host = 'vpc-chatbotassignment-domain-eezncavggazu4exrp23vrqn3z4.us-east-1.es.amazonaws.com'

    es = Elasticsearch(
    hosts = [{'host': host, 'port': 443}],
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection)
    sqs = boto3.resource('dynamodb')
    table_name=sqs.Table('yelp_restaurants')
    
    k = es.search(index="restaurantsny", doc_type="_doc", body={"query": {"match": {"cusine":cusine}}}, size=5)
    l = json.dumps(k)
    #print(k.type)
    id  = []
    ans = []
    for i in (k['hits']['hits']):
        print(i['_id'])
        response = table_name.get_item(
            Key={
                     'id': i['_id'],
                }
             )
        ans.append(response)
    print(ans)
    
    #l = {'id':'0CjK3esfpFcxIopebzjFxA'}
    #table_name=sqs.Table('yelp_restaurants')
    #response = table_name.get_item(Key={'id': '0dDCDQz7DrKkSvu9h2hcQw'})
    #print(responsem
    message ="Hello! Here are my "+str(res["Cusine"])+" restaurant suggestions for "+str(res["No_of_people"])+" people, for "+str(res["Date"])+":"+"\n"
    for i in range(0,3):
        response=ans[i]
        msg=str(i+1)+")"+str(response["Item"]["name"])+" located at "+str(response["Item"]["location"]["display_address"])
        message=message+msg+"\n"
    message=message+"Enjoy your meal!"
    print(message)
    #msg="hi"
    arn = "arn:aws:sns:us-east-1:775506362118:chatbotassignment_sns"
    client = boto3.client('sns' , 'us-east-1')
    status1 = client.publish(Message=message,MessageStructure='string',PhoneNumber = res["Phone_Number"])
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
