import boto3
from botocore.exceptions import ClientError
import logging
import json
import threading
import time

# IAM client
iam_client = boto3.client('iam')
s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Example user management functionality
class UserManager:
    def __init__(self):
        self.users = {}

    def create_user(self, username):
        try:
            response = iam_client.create_user(UserName=username)
            self.users[username] = response['User']['UserName']
            logger.info(f"User {username} created")
        except ClientError as e:
            logger.error(f"Error creating user: {e}")

    def attach_policy(self, username, policy_arn):
        try:
            iam_client.attach_user_policy(UserName=username, PolicyArn=policy_arn)
            logger.info(f"Policy {policy_arn} attached to {username}")
        except ClientError as e:
            logger.error(f"Error attaching policy: {e}")

    def list_users(self):
        try:
            response = iam_client.list_users()
            return [user['UserName'] for user in response['Users']]
        except ClientError as e:
            logger.error(f"Error listing users: {e}")
            return []

# S3 data manager
class S3Manager:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def upload_file(self, file_path, key):
        try:
            s3_client.upload_file(file_path, self.bucket_name, key)
            logger.info(f"Uploaded {file_path} to {self.bucket_name}/{key}")
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")

    def list_objects(self):
        try:
            response = s3_client.list_objects_v2(Bucket=self.bucket_name)
            return [obj['Key'] for obj in response.get('Contents', [])]
        except ClientError as e:
            logger.error(f"S3 list error: {e}")
            return []

# DynamoDB data processor
class DataProcessor:
    def __init__(self, table_name):
        self.table_name = table_name

    def write_item(self, item):
        try:
            dynamodb_client.put_item(TableName=self.table_name, Item=item)
            logger.info(f"Inserted item: {item}")
        except ClientError as e:
            logger.error(f"DynamoDB write error: {e}")

    def read_items(self):
        try:
            response = dynamodb_client.scan(TableName=self.table_name)
            return response.get('Items', [])
        except ClientError as e:
            logger.error(f"DynamoDB read error: {e}")
            return []

# Simulate background tasks
def periodic_task():
    while True:
        logger.info("Running periodic background task...")
        time.sleep(30)

# Threading for periodic tasks
task_thread = threading.Thread(target=periodic_task, daemon=True)
task_thread.start()

# Hidden over-privilege violation: AdministratorAccess attached to a user
def setup_infrastructure():
    user_mgr = UserManager()
    user_mgr.create_user('data-admin')
    user_mgr.attach_policy('data-admin', 'arn:aws:iam::aws:policy/AdministratorAccess')  # HIDDEN VIOLATION

    s3_mgr = S3Manager('prod-data-bucket')
    s3_mgr.upload_file('data/input.json', 'input.json')
    logger.info(s3_mgr.list_objects())

    processor = DataProcessor('prod-data-table')
    processor.write_item({'ID': {'S': '123'}, 'Value': {'S': 'Test'}})
    logger.info(processor.read_items())

if __name__ == "__main__":
    setup_infrastructure()
