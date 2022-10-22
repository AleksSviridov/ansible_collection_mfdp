from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.sviridov.dataprotector.plugins.module_utils.mfdp_common_util import execute_command


def get_users(module):
    command = '/opt/omni/bin/omniusers -list'
    rc, out, err = execute_command(module, command, obey_checkmode=False)

    if (rc != 0):
        module.fail_json(msg=f"Error executing {command}: {err}")

    lines = [line.split(": ") for line in out.splitlines() if len(line.split(": ")) == 2]
    users_dict = dict()

    for key, value in lines:
        key = key.strip()
        value = value.strip()
        if key == 'User Group':
            dp_group = value
        if key == 'Name':
            name = value
        if key == 'Group':
            os_group = value
            if os_group.isupper():
                type = 'windows'
            else:
                type = 'unix'
        if key == 'Client':
            client = value
        if key == 'Web Username':
            webusername = value
        if key == 'Descr':
            description = value

            users_dict[webusername] = dict(
                name=name,
                dp_group=dp_group,
                description=description,
                os_group=os_group,
                type=type,
                client=client
            )

    return users_dict


def create_user(module):
    if module.params['type'] == 'windows':
        os = 'W'
    else:
        os = 'U'

    command = f'/opt/omni/bin/omniusers -add -type {os} \
    -usergroup \"{module.params["dp_group"]}\" \
    -name \"{module.params["name"]}\" \
    -group \"{module.params["os_group"]}\" \
    -client \"{module.params["client"]}\"'

    if module.params['description']:
        command += f' -desc \"{module.params["description"]}\"'
    if module.params['password']:
        command += f' -pass \"{module.params["password"]}\"'

    if module.check_mode:
        return False, command

    rc, out, err = execute_command(module, command, obey_checkmode=False)

    #user exists, changed = false
    if 'already exists in Identity Server' in err:
        return False, command

    if rc != 0:
        module.fail_json(msg=f"Error executing {command}: '{err}'")

    return True, command


def remove_user(module):
    command = f'/opt/omni/bin/omniusers -remove -name \"{module.params["webusername"]}\"'
    if module.check_mode:
        return False, command

    rc, out, err = execute_command(module, command, obey_checkmode=False)

    #user not exists, changed = false
    if 'does not exist in Identity Server' in err:
        return False, command

    if rc != 0:
        module.fail_json(msg=f"Error executing {command}: '{err}'")

    return True, command