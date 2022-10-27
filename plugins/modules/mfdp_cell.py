# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Aleksandr Sviridov <alasviridov@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
module: mfdp_user
version_added: "0.0.1"
short_description: Manage Data Protector user accounts
description:
    - The Data Protector user management functionality provides a security layer that prevents systems and data from being accessed by unauthorized personnel.
options:
    name:
        description:
            - Name of the user to create, remove or modify. 
            - B(At least one of name and webusername are required.)
            - B(If both are set, the webusername parameter will be used.)
        type: str
        required: false
        aliases: [ user ]
attributes:
    check_mode:
        support: full
    diff_mode:
        support: full
    platform:
        platforms: posix
notes:
  - User name\os group\client cannot be updated using this module because the update operation is not idempotent.
  - If you want to update this parameters, you have to remove and than create it again.
  - User type (Unix\Windows) is not used by DP internally and is not stored. Hence, user type is always Unix. 
  - User name, group, client are forced for lowercase
author:
  - Aleksandr Sviridov (@sviridov)
'''


EXAMPLES = r'''
- name: Add or update a user from the domain to the Data Protector admin user group and allow access only from the client
  mfdp_users:
    name: win_user
    dp_group: admin
    os_group: domain1
    client: client.company.com
    description: "My test user"
'''

RETURN = r'''
    webusername:
      description: User account full name.
      returned: always
      type: str
      sample: win_user|domain1|client.company.com
'''


from ansible.module_utils.basic import AnsibleModule
import ansible_collections.sviridov.dataprotector.plugins.module_utils.mfdp_cell_util as mfdp_cell_util

def run_module(module):

    result = dict(
        changed=False,
        command='',
        webusername=module.params['webusername']
    )

    return result


def main():

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=False, aliases=['user']),
            webusername=dict(type='str', required=False),
            dp_group=dict(type='str', required=False),
            description=dict(type='str'),
            os_group=dict(type='str', required=False),
            state=dict(type='str', choices=['absent', 'present'], default='present'),
            client=dict(type='str', required=False),
            password=dict(type='str', required=False, no_log=True)
        ),
        required_together=[('name', 'os_group', 'client')],
        required_if=[('state', 'present', ['dp_group'])],
        required_one_of=[['name', 'webusername']],
        supports_check_mode=True
    )

    argument_validation_errors = mfdp_users_util.argument_validator(module)
    if argument_validation_errors:
        module.fail_json(msg=f"Incorrect arguments: {' '.join(argument_validation_errors)}'")

    results = run_module(module)
    module.exit_json(**results)


if __name__ == '__main__':
    main()