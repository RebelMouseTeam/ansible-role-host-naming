# Host Naming for EC2

Role set "incremental" tag:Name for instance based on tag:Group. For example, instance with tag:Group "docker" will be named "docker1", etc.


## Algorithm

1. gather all instances with specified tag:Group and their tags

2. generate new tag:Name which isn't taken

3. set new tag:Name

4. sleep for random number of seconds (1-10)

5. gather all instances with specified tag:Group and check collisions

5.1 if collisions occurred go to step 2.

5.2 if no collisions found then stop

This role should be applied after instance boot, because EC2 instance tags are unavailable while instance in `pending` state (generally 10-20 seconds after instance launch). This role can be executed locally, for example, using cloud-init via user data.

## Usage

```yaml
---
- hosts: localhost
  connection: local
  become: yes
  roles:
    - ansible-role-host-naming
```

## Vars

* `host_naming_name_tag` [default: `Name`]: which tag should be set.
* `host_naming_group_tag` [default: `Group`]: which tag should be used for new name generaton.
* `host_naming_retries` [default: `10`]: how many times script should try to set name in case of collision.
* `host_naming_overwrite` [default: `no`]: should existing name be overwritten.
* `host_naming_verbose` [default: `yes`]: informative logging.
* `host_naming_debug` [default: `no`]: debug logging.
* `host_naming_set_hostname` [default: `yes`]: set hostname on target instances.


## IAM

Following IAM policy should be attached to instance profile role.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:CreateTags",
                "ec2:DescribeTags",
                "ec2:DescribeInstances"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
```
