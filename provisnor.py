import boto3
import logging

class AWSSecurityManager:
    def __init__(self, region_name='us-east-1'):
        self.ec2_client = boto3.client('ec2', region_name=region_name)
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO)

    def create_security_group(self, group_name, description, vpc_id):
        try:
            response = self.ec2_client.create_security_group(
                GroupName=group_name,
                Description=description,
                VpcId=vpc_id
            )
            group_id = response['GroupId']
            self.logger.info(f"Successfully created security group '{group_name}' with ID: {group_id}")
            return group_id
        except Exception as e:
            self.logger.error(f"Failed to create security group '{group_name}': {e}")
            return None

    def add_http_ingress_rule(self, group_id):
        try:
            self.ec2_client.authorize_security_group_ingress(
                GroupId=group_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 80,
                        'ToPort': 80,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }
                ]
            )
            self.logger.info(f"Added HTTP ingress rule to group {group_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add HTTP rule to group {group_id}: {e}")
            return False

    def configure_windows_management_access(self, group_id):
        self.logger.info(f"Configuring RDP access for group {group_id}")
        try:
            self.ec2_client.authorize_security_group_ingress(
                GroupId=group_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 3389,
                        'ToPort': 3389,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }
                ]
            )
            self.logger.info(f"Successfully configured management access for group {group_id}")
        except Exception as e:
            self.logger.error(f"Could not configure management access: {e}")
            raise

    def add_internal_app_rule(self, target_group_id, source_group_id):
        try:
            self.ec2_client.authorize_security_group_ingress(
                GroupId=target_group_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 8080,
                        'ToPort': 8080,
                        'UserIdGroupPairs': [{'GroupId': source_group_id}]
                    }
                ]
            )
            self.logger.info(f"Added internal app rule from {source_group_id} to {target_group_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add internal rule to {target_group_id}: {e}")
            return False

    def delete_security_group(self, group_id):
        try:
            self.ec2_client.delete_security_group(GroupId=group_id)
            self.logger.info(f"Successfully deleted security group {group_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete security group {group_id}: {e}")
            return False

if __name__ == '__main__':
    manager = AWSSecurityManager()
    vpc_id_for_testing = 'vpc-0123456789abcdef0'
    
    web_sg = manager.create_security_group('web-server-sg', 'For web servers', vpc_id_for_testing)
    if web_sg:
        manager.add_http_ingress_rule(web_sg)

    admin_sg = manager.create_security_group('admin-server-sg', 'For admin servers', vpc_id_for_testing)
    if admin_sg:
        try:
            manager.configure_windows_management_access(admin_sg)
        except Exception as e:
            pass 

    app_sg = manager.create_security_group('app-server-sg', 'For app servers', vpc_id_for_testing)
    if app_sg and web_sg:
        manager.add_internal_app_rule(target_group_id=app_sg, source_group_id=web_sg)

    if web_sg: manager.delete_security_group(web_sg)
    if admin_sg: manager.delete_security_group(admin_sg)
    if app_sg: manager.delete_security_group(app_sg)
