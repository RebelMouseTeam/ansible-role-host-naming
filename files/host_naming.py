#!/usr/bin/env python3

import argparse
import logging

import boto3

client = boto3.client('ec2')
logger = logging.getLogger('host_naming')
formatter = logging.Formatter('%(levelname)s %(asctime)s: %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.WARNING)


def get_instances(filters):
    return client.describe_instances(Filters=filters)


def get_instance(instance_id):
    filters = [{'Name': 'instance-id', 'Values': [instance_id]}]
    instances = get_instances(filters)
    instances = [
        i for r in instances['Reservations']
        for i in r['Instances'] if i['InstanceId'] == instance_id]
    if instances:
        return instances[0]


def get_tag(instance, tag):
    tags = instance['Tags']
    record = [t for t in tags if t['Key'] == tag]
    if record:
        return record[0]['Value']


def set_tag(instance_id, tag, value):
    tags = [{'Key': tag, 'Value': value}]
    client.create_tags(Resources=[instance_id], Tags=tags)


def set_instance_name(instance_id, group, name_tag, group_tag):
    pass


def main():
    parser = argparse.ArgumentParser(description='Host Naming')
    parser.add_argument('instanceId', help='EC2 instance id')
    parser.add_argument('group', help='Group to use for instance naming')
    parser.add_argument(
        '-n',
        '--nameTag',
        help='Tag where name value should be set("Name" by default)',
        default='Name')
    parser.add_argument(
        '-g',
        '--groupTag',
        help='Tag where group value is stored("Group" by default)',
        default='Group')
    parser.add_argument('--verbose', action='store_true', default=False)
    parser.add_argument('--debug', action='store_true', default=False)
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.INFO)

    if args.debug:
        logger.setLevel(logging.DEBUG)

    logger.debug('parse arguments {}'.format(args))
    set_instance_name(args.instanceId, args.group, args.nameTag, args.groupTag)


if __name__ == '__main__':
    main()
