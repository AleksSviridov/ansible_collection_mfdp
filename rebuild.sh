#!/bin/bash

cd /storage/cifs/dev/sviridov/dataprotector
ansible-galaxy collection build --force
ansible-galaxy collection install sviridov-dataprotector-1.0.0.tar.gz --force
ansible-playbook tests/integration/targets/mfdp_users/main.yml