#!/usr/bin/env python3

import argparse
import logging
import time
import random

import boto3

client = boto3.client('ec2')
logger = logging.getLogger('host_naming')
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
logger.addHandler(handler)


def get_instances(filters):
    logger.debug('describe_instances filters: "{}"'.format(filters))
    response = client.describe_instances(Filters=filters)
    logger.debug('describe_instances response: "{}"'.format(response))
    return [i for r in response['Reservations'] for i in r['Instances']]


def get_instances_in_group(group_tag, group):
    filters = [{'Name': 'tag:{}'.format(group_tag), 'Values': [group]}]
    return get_instances(filters)


def get_group_instances_names(name_tag, group_instances):
    group_instances_names = [get_tag(i, name_tag) for i in group_instances]
    group_instances_names = [n for n in group_instances_names if n]
    return group_instances_names


def get_instance(instance_id):
    filters = [{'Name': 'instance-id', 'Values': [instance_id]}]
    instances = get_instances(filters)
    instances = [i for i in instances if i['InstanceId'] == instance_id]
    if instances:
        return instances[0]


def get_tag(instance, tag):
    tags = instance['Tags']
    record = [t for t in tags if t['Key'] == tag]
    if record:
        return record[0]['Value']


def set_tag(instance_id, tag, value):
    tags = [{'Key': tag, 'Value': value}]
    logger.debug('create_tags instance_id tags: "{}" "{}"'.format(
        instance_id, tags))
    response = client.create_tags(Resources=[instance_id], Tags=tags)
    logger.debug('create_tags response: "{}"'.format(response))


def set_instance_name(
    instance_id,
    group,
    name_tag,
    group_tag,
    name_overwrite,
    retries
):
    instance = get_instance(instance_id)
    if not instance:
        logger.critical('instance not found "{}"'.format(instance_id))
        exit(1)

    logger.debug('instance "{}"'.format(instance))

    if 'Tags' not in instance:
        logger.critical('instance tags not found "{}"'.format(instance_id))
        exit(1)

    name = get_tag(instance, name_tag)
    if name and not name_overwrite:
        logger.error('instance already has name "{}"'.format(name))
        exit(1)

    logger.info('instance name "{}"'.format(name))

    group = get_tag(instance, group_tag)
    if not group:
        logger.critical('instance has no group tag "{}"'.format(instance_id))
        exit(1)

    logger.info('instance group "{}"'.format(group))

    group_instances = get_instances_in_group(group_tag, group)
    group_instances_names = get_group_instances_names(
        name_tag, group_instances)

    logger.info('existing names in group "{}"'.format(group_instances_names))

    n = 0
    while retries > 0:
        n += 1
        name = '{}{}'.format(group, n)
        if name in group_instances_names:
            continue

        logger.info('trying name "{}"'.format(name))
        set_tag(instance_id, name_tag, name)

        # sleep 1-10 seconds before verify collisions in group
        # random time is used to prevent simultanious execution
        t = random.randint(1, 10)
        logger.debug('sleep for "{}"'.format(t))
        time.sleep(t)

        group_instances = get_instances_in_group(group_tag, group)
        group_instances_names = get_group_instances_names(
            name_tag, group_instances)

        if group_instances_names.count(name) > 1:
            logger.warning('name collision "{}"'.format(name))
        elif group_instances_names.count(name) == 1:
            logger.info('name successfully set "{}"'.format(name))
            break
        else:
            logger.error(
                'name not found in group after set "{}"'.format(name))

        retries -= 1
        continue


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
    parser.add_argument(
        '-r',
        '--retries',
        help='Max retries for setting new name',
        type=int,
        default=10)
    parser.add_argument('--overwrite', action='store_true', default=False)
    parser.add_argument('--verbose', action='store_true', default=False)
    parser.add_argument('--debug', action='store_true', default=False)
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    elif args.verbose:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    logger.debug('parse arguments "{}"'.format(args))
    set_instance_name(
        args.instanceId,
        args.group,
        args.nameTag,
        args.groupTag,
        args.overwrite,
        args.retries)


if __name__ == '__main__':
    main()
