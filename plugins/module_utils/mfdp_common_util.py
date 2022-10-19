from __future__ import absolute_import, division, print_function
__metaclass__ = type


def is_mfdp_installed(module):
    cell_info_path = '/etc/opt/omni/server/cell/cell_info'
    return module.sha1(cell_info_path)