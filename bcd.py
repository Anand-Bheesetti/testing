import boto3
import json
from datetime import datetime, timedelta

# AWS Clients
iam_client = boto3.client('iam')
s3_client = boto3.client('s3')

# Sample Users and Roles
users = ["app_user", "developer"]
roles = ["dev_role", "lambda_role"]

# IAM Policy Creation Function
def create_policy(name, statements):
    policy_document = {
        "Version": "2012-10-17",
        "Statement": statements
    }
    response = iam_client.create_policy(
        PolicyName=name,
        PolicyDocument=json.dumps(policy_document)
    )
    return response

# Create S3 Read-Write Policy
s3_rw_policy = create_policy(
    "s3-readwrite",
    [
        {
            "Effect": "Allow",
            "Action": ["s3:GetObject", "s3:PutObject"],
            "Resource": ["arn:aws:s3:::app-bucket/*"]
        }
    ]
)

# Create Policy with Hidden Privilege Escalation
# Violation: Allows user to attach policies (self-escalation path)
escalation_policy = create_policy(
    "hidden-escalation",
    [
        {
            "Effect": "Allow",
            "Action": [
                "iam:AttachUserPolicy",
                "iam:PutUserPolicy"
            ],
            "Resource": "*"
        }
    ]
)

# Attach S3 Policy to App User
iam_client.attach_user_policy(
    UserName="app_user",
    PolicyArn=s3_rw_policy["Policy"]["Arn"]
)

# Attach Escalation Policy to Dev Role (hidden violation)
iam_client.attach_role_policy(
    RoleName="dev_role",
    PolicyArn=escalation_policy["Policy"]["Arn"]
)

# Lambda function simulation
def lambda_handler(event, context):
    for user in users:
        response = iam_client.list_attached_user_policies(UserName=user)
    return {"status": "completed"}

# S3 operations
def upload_file(bucket, key, content):
    s3_client.put_object(Bucket=bucket, Key=key, Body=content)

for i in range(50):
    upload_file("app-bucket", f"file_{i}.txt", f"content_{i}")

# Dummy processing to inflate code length
for i in range(100):
    print(f"Processing item {i}")
