import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth 
import time
import io
import base64

def lambda_handler(event, context):
    # print(event)
    
    bucket=event['Records'][0]['s3']['bucket']['name']
    photo=event['Records'][0]['s3']['object']['key']
    # print(bucket,photo)
    
    s3_client = boto3.client('s3')
    
    response = s3_client.get_object(Bucket=bucket, Key=photo)

    img = response['Body'].read()
    myObj = [base64.b64encode(img)]
    return_json = str(myObj[0]) 
    return_json = return_json.replace("b'","")          # replace this 'b'' is must to get absoulate image.
    image = return_json.replace("'","")
    print(image)
    
    client=boto3.client('rekognition')
    res = client.detect_labels(
    Image={'Bytes':img},
    MaxLabels=25,
    MinConfidence=80
    )
    
    labels=res['Labels']
    custom_labels=[]
    timeStamp=time.time()
    for label in labels:
        custom_labels.append(label['Name'])
        
    # print(custom_labels)
    
    host="search-photosnew-tffirm2thjh6btphreva77wjhu.us-east-1.es.amazonaws.com"
    region='us-east-1'
    
    credentials=boto3.Session().get_credentials()
    auth=AWSV4SignerAuth(credentials, region)
    print('\nauth')
    print(auth)
    
    osClient = OpenSearch(
        hosts=[{'host': host, 'port':443}],
        use_ssl=True,
        http_auth=auth,
        verify_certs=True,
        connection_class=RequestsHttpConnection)
        
    index_body = {
              'objectKey':photo,
              'bucket':bucket,
              'createdTimeStamp':timeStamp,
              'labels':custom_labels
        }
    temp=osClient.index(index='photos', body=index_body)
    print(temp)
    
    return {
            'status': 'True',
            'statusCode': 200,
            'encoded_image':image          # returning base64 of your image which in s3 bucket.
    }
