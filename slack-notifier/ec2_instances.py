import boto3
import os
import stat
from botocore.exceptions import ClientError

ec2 = boto3.resource('ec2')
image_name = 'amzn2-ami-hvm-2.0.20200304.0-x86_64-gp2'


# Create a Key pair
def key_pair():
    key_name = 'python_automation_key'
    key_path = key_name + '.pem'
    try:
        key = ec2.create_key_pair(KeyName=key_name)
        key.key_material
        with open(key_path, 'w') as key_file:
            key_file.write(key.key_material)
        print('Key Pair created')
        
        os.chmod(key_path, stat.S_IRUSR | stat.S_IWUSR)
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidKeyPair.Duplicate':
            print('Error Occurred,Key Pair already exists')
        else:
            raise
    return


def get_ami_name():
    response = ec2.images.filter(
        Owners=['amazon'],
        Filters=[{'Name': 'name', 'Values': [image_name]}]
    )
    ami_name = list(response)
    print(ami_name)
    return ami_name


def web_instance():
    try:
        response = ec2.create_instances(
            ImageId='ami-03b5297d565ef30a6',
            InstanceType='t2.micro',
            MinCount=1,
            MaxCount=1,
            KeyName='kevin_dev',
            DryRun=False
        )
        print('Instance is created !!!!')
        instance_new = response[0]

        instance_new.wait_until_running()
        instance_new.reload()

        public_url = instance_new.public_dns_name
        print(public_url)

        ec2_sg = instance_new.security_groups[0]['GroupId']

        return instance_new, ec2_sg
    except ClientError as e:
        if e.response['Error']['Code'] == 'MissingParameter':
            print('Must parameter ImageId is not given')
        else:
            raise


def authorize_sg_in_http(instance_new, ec2_sg):
    response = ec2.SecurityGroup(instance_new.security_groups[0]['GroupId'])
    global sg_ingress_http
    try:
        sg_ingress_http = response.authorize_ingress(
            GroupId=ec2_sg,
            DryRun=False,
            IpPermissions=[
                {
                    'FromPort': 80,
                    'IpProtocol': 'tcp',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                        },
                    ],
                    'ToPort': 80

                }
            ],
        )
        print('1.Success')
        print(sg_ingress_http)
        return sg_ingress_http
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidPermission.Duplicate':
            print('HTTP Port access rule already exists')
        else:
            raise


def authorize_sg_in_ssh(instance_new, ec2_sg):
    response = ec2.SecurityGroup(instance_new.security_groups[0]['GroupId'])
    global sg_ingress_ssh
    try:
        sg_ingress_ssh = response.authorize_ingress(
            GroupId=ec2_sg,
            DryRun=False,
            IpPermissions=[
                {
                    'FromPort': 22,
                    'IpProtocol': 'tcp',
                    'IpRanges': [
                        {
                            'CidrIp': '182.65.98.194/32',
                        },
                    ],
                    'ToPort': 22

                }
            ],
        )
        print('2.Success')
        return sg_ingress_ssh
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidPermission.Duplicate':
            print('SSH Port access rule already exists')
        else:
            raise


#def main():
    #key_pair()
    #get_ami_name()

    #instance_new, ec2_sg = web_instance()
    #print('Web server created')
    #authorize_sg_in_http(instance_new, ec2_sg)
    #authorize_sg_in_ssh(instance_new, ec2_sg)
