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
    webusername:
        description:
            - Web Username (name|group|client) of the user to create, remove or modify. 
            - B(At least one of name and webusername are required.)
            - B(If both are set, the webusername parameter will be used.)
        type: str
        required: false
    dp_group:
        description:
            - Required when creating an user C(state=present)
            - Data Protector user group for user created.
        type: str
        required: false
    description:
        description:
            - Specifies the description for the added user.
        type: str
    os_group:
        description:
            - A group (on Unix systems) or a domain (on Windows systems) that the specified user belongs to. 
            - To grant or revoke access of the user from any group or domain of the specified clients, specify the group or domain name as asterisk (*) .
            - * corresponds to <Any> in the Data Protector GUI.
        type: str
        required: true
    state:
        description:
            - Whether the account should exist or not, taking action if the state is different from what is stated.
        type: str
        choices: [ absent, present ]
        default: present
    client:
        description:
            - Specifies the name of the client system from where the specified user has access to the Cell Manager. 
            - Better use the fully qualified domain name (FQDN)
            - To grant or revoke access for the specified user to the Cell Manager from any Data Protector client system,  specify the client name as asterisk (*).
            - * corresponds to <Any> in the Data Protector GUI.
        type: str
        required: true
    password:
        description:
            - Specifies the password for the added user.
        type: str
        required: false

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
    
- name: The same providing webusername only:
  mfdp_users:
    webusername: "win_user|domain1|client.company.com"
    dp_group: admin
    description: "My test user"
    password: OMNIomni11_
    
- name: Remove the created user
  mfdp_users:
    name: win_user
    os_group: domain1
    client: client.company.com
    state: absent
    
- name: Remove that user providing webusername only:
  mfdp_users:
    webusername: "win_user|domain1|client.company.com"
    state: absent
'''

RETURN = r'''
    webusername:
      description: User account full name.
      returned: always
      type: str
      sample: win_user|domain1|client.company.com
    command:
      description: CLI command executed.
      returned: if changed
      type: str
      sample: omniusers -add -type W -usergroup admin -name win_user -group DOMAIN1 -client client.company.com
'''

from ansible.module_utils.basic import AnsibleModule
import ansible_collections.sviridov.dataprotector.plugins.module_utils.mfdp_users_util as mfdp_users_util
from ansible_collections.sviridov.dataprotector.plugins.module_utils.mfdp_common_util import is_mfdp_installed


def run_module(module):
    if module.params['webusername']:
        module.params['webusername'] = module.params['webusername'].lower()
        module.params['name'], module.params['os_group'], module.params['client'] = module.params['webusername'].split('|')
    else:
        module.params["name"] = module.params["name"].lower()
        module.params["os_group"] = module.params["os_group"].lower()
        module.params["client"] = module.params["client"].lower()
        module.params['webusername'] = f'{module.params["name"]}|{module.params["os_group"]}|{module.params["client"]}'

    # TODO: Check if Any (*) is allowed in the cell global config

    result = dict(
        changed=False,
        command='',
        webusername=module.params['webusername']
    )

    if not is_mfdp_installed(module):
        module.fail_json(msg='Data Protector Cell Server not found', **result)

    #Create
    if module.params['state'] == 'present':
        result['changed'], result['command'] = mfdp_users_util.create_user(module)
    #Remove
    if module.params['state'] == 'absent':
        result['changed'], result['command'] = mfdp_users_util.remove_user(module)

    # show diff only if execute_command called
    if result['changed']:
        result['diff'] = {"prepared": f'Command executed: {result["command"]}'}

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