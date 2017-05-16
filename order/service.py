import boto3
import uuid
dynamodb = boto3.resource("dynamodb",region_name="us-west-1",
aws_access_key_id= "AKIAIZBYXWI4IHGGYTVQ",
aws_secret_access_key = "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")
import json
import datetime

print('Loading function')


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def handler(event, context):

    operation=event['httpMethod']
    if operation=='POST':
          table=dynamodb.Table('order')
    	  response = table.put_item(
          	Item={
         	   'menu_id':event['menu_id'],
            	   'order_id':event['order_id'],
            	   'customer_name':event['customer_name'],
            	   'customer_email':event['customer_email'],
            	   'order_status': 'processing',
            	   "order": {  }
          	 })
    	  table=dynamodb.Table('menu')     
    	  response=table.get_item(
        	Key={
            	  'menu_id':event['menu_id']
        	})
          if(response['Item']['sequence'][0]=='selection'):    
               result=""
               result+="Hi "+event['customer_name']
               result+=", please choose one of these selection:"
               val=1
               for i in response['Item']['selection']:
                   result+=(" "+str(val)+". "+str(i)+",")
                   val+=1
               result=result[:-1]
          else: 
               result=""
               result+="Hi "+event['customer_name']
               result+="Which size do you want?"
               val=1
               for i in response['Item']['size']:
                  result+=(" "+str(val)+". "+str(i)+",")
                  val+=1
               result=result[:-1]    
          return {"Message": result}
    elif (operation=='PUT'):
          table=dynamodb.Table('order')
          response = table.get_item(
       		 Key={
              		'order_id':event['order_id'],
          		})
          ordermap=  response['Item']['order']
    	  table=dynamodb.Table('menu')
          menu_details=table.get_item(
       		Key={
                   'menu_id':response['Item']['menu_id'] 
         	})
          if (menu_details['Item']['sequence'][0]=='selection'):
               if 'selection' not in ordermap:
            	result=""
                input_number=int(event['input'])
                result+="Which size do you want?"
                val=1
                for i in menu_details['Item']['size']:
                  result+=(" "+str(val)+". "+str(i)+",")
                  val+=1
                result=result[:-1] 
                if((input_number-1)<(len(menu_details['Item']['selection']))):
                    order_selection={"selection":menu_details['Item']['selection'][input_number-1]}
                else:
                    return "Please select from available options."
                table=dynamodb.Table('order')
                res=table.update_item(
                   Key={
                        'order_id':event['order_id']
                       },
                       UpdateExpression= "SET #n= :val1",
                       ExpressionAttributeNames = {"#n":"order"},
                       ExpressionAttributeValues={':val1': order_selection})
                return {"Message":result}
               elif 'size' not in ordermap:
            	input_number=int(event['input']) 
                if((input_number-1)<(len(menu_details['Item']['size']))):
            	   order_size=menu_details['Item']['size'][input_number-1]
                else:
                   return "Please select from available options."
            	update_map={}
            	update_map['selection']=response['Item']['order']['selection']
            	update_map['size']=order_size
            	order_price=menu_details['Item']['price'][input_number-1]
            	update_map['costs']=order_price
            	update_map['order_time']=str(datetime.datetime.now().strftime('%m-%d-%Y@%H:%M:%S'))
            	table=dynamodb.Table('order')
                res=table.update_item(
                Key={
                    'order_id':event['order_id']
                    },
                UpdateExpression= "SET order_status= :val1,#n= :val2",
                ExpressionAttributeNames = {"#n":"order"},
                ExpressionAttributeValues={":val1": "processing",':val2':update_map})
                result=""
                result+="Your order costs $"+order_price+". We will email you when the order is ready. Thank you!"
                return {"Message":result} 
               else:
            	return "Please select from the available options."
          elif (menu_details['Item']['sequence'][0]=='size'):
               if 'size' not in ordermap:
            	   result="" 
                   result+='please choose one of these selection:'
                   val=1
            	   for i in menu_details['Item']['selection']:
                      result+=(" "+str(val)+". "+str(i)+",")
                      val+=1
                   result=result[:-1]
            	   input_number=int(event['input']) 
                   if((input_number-1)<(len(menu_details['Item']['size']))):
                         order_size=menu_details['Item']['size'][input_number-1]
                   else:
                         return "Please select from the available options."
                   update_map={}
                   #update_map['selection']=response['Item']['order']['selection']
                   update_map['size']=order_size
                   order_price=menu_details['Item']['price'][input_number-1]
                   update_map['costs']=order_price
                   update_map['order_time']=datetime.datetime.now().strftime('%m-%d-%Y@%H:%M:%S')
                   table=dynamodb.Table('order')
                   res=table.update_item(
                	Key={
                    		'order_id':event['order_id']
                    	},
                	UpdateExpression= "SET order_status= :val1,#n= :val2",
                	ExpressionAttributeNames = {"#n":"order"},
                	ExpressionAttributeValues={":val1": "processing",':val2':update_map})
                   return {"Message":result}  
               elif 'selection' not in ordermap:
                   input_number=int(event['input'])
                   if((input_number-1)<(len(menu_details['Item']['selection']))):
            	       order_selection={"selection":menu_details['Item']['selection'][input_number-1]}
                   else:
                       return "Please select from the available options."
            	   order_selection['size']=response['Item']['order']['size']
            	   order_selection['costs']=response['Item']['order']['costs']
            	   order_selection['order_time']=response['Item']['order']['order_time']
            	   table=dynamodb.Table('order')
                   res=table.update_item(
                	Key={
                          'order_id':event['order_id']
                        },
                        UpdateExpression= "SET #n= :val1",
                	ExpressionAttributeNames = {"#n":"order"},
                	ExpressionAttributeValues={':val1': order_selection})
                   result=""
            	   result+="Your order costs $"+order_selection['costs']+'. We will email you when the order is ready. Thank you!'
                   return {"Message":result} 
               else: 
            	   return "Please select from the available options."   
    elif (operation=='GET'):
         table=dynamodb.Table('order')
         try:
             response=table.get_item(
      	  		Key={
                        'order_id':event['order_id']
             })
             return response['Item'] 
         except KeyError:return "400"
         
    else:
        return respond(ValueError('Unsupported method'))
   
