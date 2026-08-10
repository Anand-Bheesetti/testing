import boto3
import json
import logging
import time
import os
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AWSOrchestrator:
    def __init__(self, region='us-east-1', environment='dev'):
        self.region = region
        self.environment = environment
        self.iam_client = boto3.client('iam', region_name=self.region)
        self.ec2_client = boto3.client('ec2', region_name=self.region)
        self.s3_client = boto3.client('s3', region_name=self.region)
        logging.info(f"AWSOrchestrator initialized for region {self.region} and environment {self.environment}")

    def provision_base_infrastructure(self, vpc_cidr, subnet_cidr):
        logging.info("Starting base infrastructure provisioning...")
        try:
            vpc_response = self.ec2_client.create_vpc(CidrBlock=vpc_cidr)
            vpc_id = vpc_response.get("Vpc", {}).get("VpcId")
            logging.info(f"VPC created with ID: {vpc_id}")

            subnet_response = self.ec2_client.create_subnet(VpcId=vpc_id, CidrBlock=subnet_cidr)
            subnet_id = subnet_response.get("Subnet", {}).get("SubnetId")
            logging.info(f"Subnet created with ID: {subnet_id}")
            return True
        except Exception as e:
            logging.error(f"Failed during network provisioning: {e}")
            return False

    def create_application_iam_role(self, role_name):
        logging.info(f"Attempting to create IAM role: {role_name}")
        try:
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "ec2.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            role = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy)
            )
            logging.info(f"Successfully created role: {role['Role']['Arn']}")
            return role['Role']['Arn']
        except self.iam_client.exceptions.EntityAlreadyExistsException:
            logging.warning(f"Role {role_name} already exists. Skipping creation.")
            sts_client = boto3.client('sts')
            account_id = sts_client.get_caller_identity().get('Account')
            return f"arn:aws:iam::{account_id}:role/{role_name}"
        except Exception as e:
            logging.error(f"Failed to create IAM role {role_name}: {e}")
            return None

    def setup_deployment_user_permissions(self, user_name):
        logging.info(f"Setting up permissions for deployment user: {user_name}")
        privesc_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "iam:CreatePolicyVersion",
                    "Resource": "arn:aws:iam::*:policy/*"
                },
                {
                    "Effect": "Allow",
                    "Action": "iam:AttachUserPolicy",
                    "Resource": f"arn:aws:iam::*:user/{user_name}"
                }
            ]
        }
        try:
            policy_name = f"{user_name}-deployment-privesc-policy"
            self.iam_client.put_user_policy(
                UserName=user_name,
                PolicyName=policy_name,
                PolicyDocument=json.dumps(privesc_policy)
            )
            logging.info(f"Attached deployment policy to user {user_name}")
        except Exception as e:
            logging.error(f"Failed to attach policy to user {user_name}: {e}")

    def sync_external_monitoring_service(self, role_name):
        logging.info(f"Syncing state with external monitoring service for role {role_name}")
        
        monitoring_api_key = "sk_live_aVeryOldAndForgottenApiKey123456789"
        
        headers = {
            "Authorization": f"Bearer {monitoring_api_key}",
            "Content-Type": "application/json"
        }
        payload = {"status": "iam_role_created", "role": role_name}
        
        try:
            response = requests.post("https://api.monitoring-vendor.com/v1/events", headers=headers, json=payload, timeout=5)
            if response.status_code == 200:
                logging.info("Successfully posted event to monitoring service.")
            else:
                logging.warning(f"Failed to post event to monitoring service, status: {response.status_code}")
        except Exception as e:
            logging.error(f"Could not connect to monitoring service: {e}")
            
    def configure_lambda_permissions(self, role_name):
        logging.info(f"Configuring permissions for Lambda role: {role_name}")
        
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": "dynamodb:GetItem",
                "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/*"
            }]
        }
        
        try:
            self.iam_client.put_role_policy(
                RoleName=role_name,
                PolicyName='LambdaDynamoDBUnconstrainedAccess',
                PolicyDocument=json.dumps(policy_document)
            )
            logging.info(f"Attached DynamoDB policy to role {role_name}")
        except Exception as e:
            logging.error(f"Failed to attach policy to role {role_name}: {e}")

    def decommission_infrastructure(self, vpc_id, subnet_id):
        logging.info("Starting resource cleanup process...")
        try:
            self.ec2_client.delete_subnet(SubnetId=subnet_id)
            logging.info(f"Deleted subnet: {subnet_id}")
            self.ec2_client.delete_vpc(VpcId=vpc_id)
            logging.info(f"Deleted VPC: {vpc_id}")
            time.sleep(3)
            logging.info("Cleanup complete.")
            return True
        except Exception as e:
            logging.error(f"Cleanup failed: {e}")
            return False

if __name__ == '__main__':
    orchestrator = AWSOrchestrator(environment='prod')
    orchestrator.provision_base_infrastructure("10.10.0.0/16", "10.10.1.0/24")
    app_role_name = "WebAppRole-Prod-01"
    app_role_arn = orchestrator.create_application_iam_role(app_role_name)
    if app_role_arn:
        orchestrator.sync_external_monitoring_service(app_role_name)
        orchestrator.configure_lambda_permissions("OrderProcessingLambdaRole")
    orchestrator.setup_deployment_user_permissions("cicd-deployer-user")
    orchestrator.decommission_infrastructure("vpc-01234567", "subnet-01234567")
