import boto3
import pandas as pd
import json

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    sns = boto3.client('sns')
    
    try:
        # Get the uploaded file details
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        file_key = event['Records'][0]['s3']['object']['key']
        
        # Read the JSON file into a pandas DataFrame
        obj = s3.get_object(Bucket=bucket_name, Key=file_key)
        df = pd.read_json(obj['Body'])
        
        # Filter records where status is "delivered"
        filtered_df = df[df['status'] == 'delivered']
        
        # Write the filtered DataFrame to a new JSON file in the target bucket
        target_bucket = 'doordash-target-zne'
        target_file_key = f"{file_key.split('.')[0]}-filtered.json"
        target_file_content = filtered_df.to_json(orient='records')
        s3.put_object(Bucket=target_bucket, Key=target_file_key, Body=target_file_content)
        
        # Publish success message to SNS
        sns.publish(
            TopicArn='arn:aws:sns:us-east-1:654654312422:DoordashProcessingNotifications',
            Subject='Delivery Data Processing Success',
            Message='Delivery data processing completed successfully.'
            )
        
        return {
            'statusCode': 200,
            'body': json.dumps('Delivery data processing completed successfully.')
        }
       
    except Exception as e:
        # Publish failure message to SNS
        sns.publish(
            TopicArn='arn:aws:sns:us-east-1:654654312422:DoordashProcessingNotifications',
            Subject='Delivery Data Processing Failure',
            Message=f'Delivery data processing failed: {str(e)}'
        )
        raise e
