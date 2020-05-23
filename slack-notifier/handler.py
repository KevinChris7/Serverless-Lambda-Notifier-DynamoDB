import boto3
import os
import requests
from botocore.exceptions import ConnectTimeoutError, ClientError
from boto3.exceptions import ResourceNotExistsError

dydbclient = boto3.client('dynamodb')


def notifier_to_slack(event, context):
    try:
        # Environment Variables for getting the slack webhook url and DynamoDB table
        slack_webhook_url = os.environ['SLACK_WEBHOOK_URL']
        table_name = os.environ['DYNAMODB_TABLE']

        # Prints the event which triggered the Lambda function
        print(event)

        # Formatting the event to get required details assigned to the variable
        message_to_slack = "From {source} at {time} about {detail[Description]}".format(**event)
        data = {"text": message_to_slack}
        # Posting the json formatted message in slack
        requests.post(slack_webhook_url, json=data)

        # Fetching event details for assigning to db variables
        source_data_db = "{source}".format(**event)
        time_data_db = "{time}".format(**event)

        # Adding items to mentioned DynamoDB table
        response = dydbclient.put_item(
            TableName=table_name,
            Item={
                'timestamp': {
                    'S': time_data_db
                },
                'service': {
                    'S': source_data_db
                },
            }
        )
        print(response.StatusCode)
        return
    except KeyError as e:
        print("Key Error, Null or Not Exist !!!", e)
    except ConnectTimeoutError as e:
        print(e)
    except ClientError as e:
        if e.response['Error']['Code'] == "TooManyRequestsException ":
            print('Concurrent Invocation limit reached')
        else:
            raise
    except ResourceNotExistsError as e:
        print(e)
