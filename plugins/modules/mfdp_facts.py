# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Aleksandr Sviridov <alasviridov@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
module: user
version_added: "0.0.1"
short_description: Fetch Data Protector facts 
description:
    - Module that allows you to fetch MFDP facts
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.sviridov.dataprotector.plugins.module_utils.mfdp_users_util import get_users

def run_module():
    argument_spec = {
        'gather_subset': dict(default=['all'], type='list')
    }

    result = dict(
        changed=False,
        ansible_facts=dict(),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    if 'all' in module.params['gather_subset']:
        gather_all = True
    else:
        gather_all = False

    if gather_all or 'users' in module.params['gather_subset']:
        result['ansible_facts']['mfdp_users'] = get_users(module)

    module.exit_json(**result)


def main():
    run_module()