from __future__ import absolute_import, division, print_function
__metaclass__ = type

from shlex import split

def get_users(module):
    command = '/opt/omni/bin/omniusers -list'
    rc, out, err = module.run_command(split(command))

    if (rc != 0):
        module.fail_json(msg=f"Error executing {command}: {err}")

    lines = [line.split(": ") for line in out.splitlines() if len(line.split(": "))==2]
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

            users_dict[webusername]=dict(
                name=name,
                dp_groups=dp_group,
                description=description,
                os_group=os_group,
                type=type,
                client=client
            )

    return users_dict
