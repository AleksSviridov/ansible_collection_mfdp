# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Aleksandr Sviridov <alasviridov@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

#TODO: Required one of name+osgroup+client or webusername
DOCUMENTATION = r'''
module: user
version_added: "0.0.1"
short_description: Manage Data Protector user accounts
description:
    - The Data Protector user management functionality provides a security layer that prevents systems and data from being accessed by unauthorized personnel.
options:
    name:
        description:
            - Name of the user to create, remove or modify.
        type: str
        required: true
        aliases: [ user ]
    dp_groups:
        description:
            - List of groups Data Protector user groups user will be added to.
        type: list
        elements: str
        required: true
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
    type:
        description:
            - Specifies the user type: a Unix user (unix) or a Windows user (windows).
        type: str
        choices: [ unix, windows ]
        default: unix
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
        support: none
    platform:
        platforms: posix
author:
- Aleksandr Sviridov (@sviridov)
'''

EXAMPLES = r'''
- name: Add a Windows user from the domain to the Data Protector admin user group and allow access only from the client 
  mfdp_users:
    name: win_user
    dp_groups: 
      - admin
    os_group: domain1
    client: client.company.com
    type: windows
    
- name: Remove the created user
  mfdp_users:
    name: win_user
    os_group: domain1
    client: client.company.com
    state: absent
'''

RETURN = r'''
    name:
      description: User account basic name.
      returned: always
      type: str
      sample: win_user
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
from ansible_collections.sviridov.dataprotector.plugins.module_utils.mfdp_users_util import get_users
from ansible_collections.sviridov.dataprotector.plugins.module_utils.mfdp_common_util import is_mfdp_installed


def run_module(module):
    params = module.params
    params['webusername'] = f'{params["name"]}|{params["os_group"]}|{params["client"]}'.replace('|*','|\*')
    result = dict(
        changed=False,
        original_message='',
        message='',
        user = params['name'],
        state = params['state'],
        webusername = params['webusername']
    )

    if not is_mfdp_installed(module):
        module.fail_json(msg='Data Protector Cell Server not found', **result)

    user_exists = (params['webusername'] in get_users(module))
    module.log('Testt')
    #Удалить
    if params['state'] == 'absent' and user_exists:
        if module.check_mode:
            module.exit_json(**result)
        result['changed'] = True
    #Создать
    if params['state'] == 'present' and not user_exists:
        if module.check_mode:
            module.exit_json(**result)
        result['changed'] = True
    #Уже удалено
    if params['state'] == 'absent' and not user_exists:
        result['changed'] = False
    #Уже создано
    if params['state'] == 'present' and user_exists:
        result['changed'] = False

    return result


def main():

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True, aliases=['user']),
            dp_groups=dict(type='list', elements='str', required=True),
            description=dict(type='str'),
            os_group=dict(type='str', required=True),
            type=dict(type='str', choices=['unix', 'windows'], default='unix'),
            state=dict(type='str', choices=['absent', 'present'], default='present'),
            client=dict(type='str', required=True),
            password=dict(type='str', required=False)
        ),
        supports_check_mode=True
    )

    results = run_module(module)
    module.exit_json(**results)


if __name__ == '__main__':
    main()