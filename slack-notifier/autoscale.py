import boto3
import ec2_instances

from botocore.exceptions import ClientError


asg = boto3.client('autoscaling')


def create_asg(asg_name, ec2_instance_id):
    try:
        response = asg.create_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            MinSize=1,
            MaxSize=2,
            DesiredCapacity=1,
            InstanceId=ec2_instance_id,
            DefaultCooldown=10
        )
        print('Auto Scaling group is created')
        return response
    except ClientError as e:
        if e.response['Error']['Code'] == 'AlreadyExists':
            print('A launch configuration already exists with the name')
        else:
            raise


def display_asg(asg_name):
    response = asg.describe_auto_scaling_groups(
            AutoScalingGroupNames=[asg_name]
        )
    print('Displayed Auto Scaling Groups')
    print(response)
    return response


def display_asg_policy(asg_name):
    try:
        response = asg.describe_policies(
            AutoScalingGroupName=asg_name,
        )
        print('Displayed Auto Scaling Policy')
        print(response)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ValidationError':
            print('Policy not exits or invalid policy name')
        else:
            raise


def execute_asg_policy(asg_name):
    try:
        response = asg.execute_policy(
            AutoScalingGroupName=asg_name,
            PolicyName='scaleOut',
            HonorCooldown=True
        )
        return response
    except ClientError as e:
        if e.response['Error']['Code'] == 'ValidationError':
            print('Trying to execute Policy not exits or invalid policy name')
        else:
            raise


def menu():
    print('===Menu===')
    print('1. Create Auto Scaling Group')
    print('2. Display Auto Scaling Group')
    print('3. Display Auto Scaling Policy')
    print('4. Execute Policy')
    print('0. Quit')
    return


def prepare_instances():
    try:
        ec2_instances.get_ami_name()
        instance_new, ec2_sg = ec2_instances.web_instance()
        print('Web server created')
        ec2_instances.authorize_sg_in_http(instance_new, ec2_sg)
        ec2_instances.authorize_sg_in_ssh(instance_new, ec2_sg)
        ec2_instance_id = instance_new
        return ec2_instance_id
    except ClientError as e:
        print(e)


def main():
    prepare_instances()
    print('1.Success')
    option = -1
    while option != 0:
        menu()
        try:
            option = int(input('Enter the Values: '))
            if option == 0:
                print('Quit')
                break
            elif option == 1:
                value1 = input('Enter the Name of Auto Scaling Group:')
                value2 = input('Enter the EC2 Instance Id:')
                create_asg(value1, value2)
            elif option == 2:
                value = input('Enter the Name of ASG to display')
                display_asg(value)
            elif option == 3:
                value = input('Enter the Name of ASG to display the Policy')
                display_asg_policy(value)
            elif option == 4:
                value = input('Enter the Name of ASG to execute policy')
                execute_asg_policy(value)
            else:
                print('Error Input !!!!')
        except ValueError as e:
            print('Value Error,Invalid Input', e)
    return


if __name__ == '__main__':
    main()
