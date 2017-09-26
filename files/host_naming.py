#!/usr/bin/env python3

import argparse
import logging

import boto3

client = boto3.client('ec2')


def get_instances(filters):
    return client.describe_instances(Filters=filters)


def get_instance(instance_id):
    filters = [{'Name': 'instance-id', 'Values': [instance_id]}]
    instances = get_instances(filters)
    instances = [i for r in instances['Reservations'] for i in r['Instances'] if i['InstanceId'] == instance_id]
    if instances:
        return instances[0]


def get_tag(instance, tag):
    tags = instance['Tags']
    record = [t for t in tags if t['Key'] == tag]
    if record:
        return record[0]['Value']


def set_tag(instance_id, tag, value):
    client.create_tags(Resources=[instance_id], Tags=[{'Key': tag, 'Value': value}])


def main():
    parser = argparse.ArgumentParser(description='Host Naming')
    parser.add_argument('instance-id', help='EC2 instance id')
    parser.add_argument('group', help='Group to use for instance naming')
    parser.add_argument('-n', '--name-tag', help='Tag where name value should be set("Name" by default)', default='Name')
    parser.add_argument('-g', '--group-tag', help='Tag where group value is stored("Group" by default)', default='Group')
    args = parser.parse_args()


if __name__ == '__main__':
    main()
