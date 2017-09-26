# Host Naming for EC2

Role set "incremental" tag:Name for instance based on tag:Group. For example, instance with tag:Group "docker" will be named "docker1", etc.

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
* `host_naming_overwrite` [default: `no`]: should existing name be overwritten or not.
* `host_naming_verbose` [default: `yes`]: informative logging.
* `host_naming_debug` [default: `no`]: debug logging.


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
                "ec2:DescribeInstances"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
```
