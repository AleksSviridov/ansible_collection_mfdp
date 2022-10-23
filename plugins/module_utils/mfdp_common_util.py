from __future__ import absolute_import, division, print_function
__metaclass__ = type

from shlex import split


def is_mfdp_installed(module):
    cell_info_path = '/etc/opt/omni/server/cell/cell_info'
    return module.sha1(cell_info_path)


def execute_command(module, cmd, use_unsafe_shell=False, data=None, obey_checkmode=True):
    if module.check_mode and obey_checkmode:
        return (0, '', '')
    else:
        return module.run_command(split(cmd), use_unsafe_shell=use_unsafe_shell, data=data)