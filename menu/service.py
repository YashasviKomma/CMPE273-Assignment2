import boto3 
from boto3 import dynamodb 

from boto3.session import Session
import uuid
import json


dynamodb_session = Session(aws_access_key_id='AKIAIZBYXWI4IHGGYTVQ',
          aws_secret_access_key='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',
          region_name='us-west-1')

dynamodb = dynamodb_session.resource('dynamodb')

table=dynamodb.Table('menu')

   
def handler(event, context):

   method=event['Method']
   if method=='POST':
       response = table.put_item(
       Item = {
            "menu_id" : event['menu_id'],
            "store_name" : event['store_name'],
            "selection" : event['selection'],
            "size" : event['size'],
            "price" : event['price'],
            "sequence" : event['sequence'],
            "store_hours" : event['store_hours']
       
                 })
       return "posted"
   elif method=='GET':
       response = table.get_item(
           Key={
               "menu_id":event['menu_id']
                }
             )
       return response['Item']

   elif method=="DELETE":
       table.delete_item(
           Key={"menu_id": event['menu_id']}
         )  
       return "deleted"  
   elif method=="PUT":
       menu_id = event['params']['menu_id']
       attributes = event['body'].keys()
       for k in attributes:
        if k!= 'menu_id':
            table.update_item(
                Key={
                'menu_id': menu_id
                },
                UpdateExpression= "set #n = :val",
                ExpressionAttributeNames = {"#n":k},
                ExpressionAttributeValues={ ':val' : event['body'][k] }
            )
       return "updated" 
   else:
       return "in else" 
