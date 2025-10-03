
import boto3
import json

iam_client = boto3.client('iam')
external_aws_account_id = '987654321098' 

# 
trust_policy_violation = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": { "AWS": f"arn:aws:iam::{external_aws_account_id}:root" },
        "Action": "sts:AssumeRole"
        
    }]
}

try:
    response = iam_client.create_role(
        RoleName='VendorSaaSIntegrationRole_VIOLATION',
        AssumeRolePolicyDocument=json.dumps(trust_policy_violation),
        Description='Violating policy - allows cross-account access without ExternalId.'
    )
    print("Violating cross-account role created successfully:")
    print(f"Role ARN: {response['Role']['Arn']}")
except Exception as e:
    print(f"An error occurred (this may be expected if the role already exists): {e}")
