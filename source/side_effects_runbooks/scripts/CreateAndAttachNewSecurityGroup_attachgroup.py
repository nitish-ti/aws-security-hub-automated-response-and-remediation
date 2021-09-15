import boto3
from botocore.exceptions import ClientError
from time import sleep

ec2_client = boto3.client("ec2")
ec2 = boto3.resource('ec2')

def handler(event, context):
    Ids = event['Resources']
    new_security_group_id = event['GroupId']
    instances = ec2.instances.filter(InstanceIds=Ids)
    for instance in instances:
        current_groups = instance.security_groups
        group_ids = [group['GroupId'] for group in current_groups]
        instance.modify_attribute(Groups=[*group_ids, new_security_group_id])
        
