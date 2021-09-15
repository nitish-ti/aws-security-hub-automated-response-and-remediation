import boto3
from botocore.exceptions import ClientError
from time import sleep

ec2_client = boto3.client("ec2")
ec2 = boto3.resource("ec2")

def get_permissions(group_id):
    default_group = ec2_client.describe_security_groups(
        GroupIds=[group_id]).get("SecurityGroups")[0]
    return default_group, default_group.get("IpPermissions"), default_group.get("IpPermissionsEgress")


def handler(event, context):
    group_id = event.get("GroupId")
    default_group, ingress_permissions, egress_permissions = get_permissions(
        group_id)
    response = ec2_client.create_security_group(GroupName='default-replacement',
                                                     Description='Replacement for default security group', VpcId=default_group['VpcId'])
    new_security_group = ec2.SecurityGroup(response['GroupId'])
    new_security_group.authorize_ingress(ingress_permissions)
    new_security_group.authorize_egress(egress_permissions)
    return {"output": new_security_group.get('group_id')}
    
