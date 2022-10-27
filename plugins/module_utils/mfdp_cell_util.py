from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.sviridov.dataprotector.plugins.module_utils.mfdp_common_util import execute_command
import re

def argument_validator(module):
    # TODO: Validate more module arguments
    error_message = []
    if module.params['client'] and not re.match(r'^\S+$', str(module.params['client'])):
        error_message.append('Client name should contain no spaces')
    return error_message