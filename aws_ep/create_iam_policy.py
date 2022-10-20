import datetime
from itertools import count
import json
# import os
import pathlib
# import argparse
# from terraform_lib.utils import TerraformUtil
# import requests
import threading
# import re
#import hcl
    
ROOT_PATH = pathlib.Path(__file__).parent.resolve()
policy_names = []

class ExternalIdGen:

    def __init__(self):
        self._external_id_lock = threading.Lock()

    def get_external_id(self):
        external_id = ""
        with self._external_id_lock:
            import uuid
            external_id = str(uuid.uuid4())
        return external_id


######################
## Create policies ###
######################


with open('aws_ep/policies.json', 'r') as p:
    input = json.load(p)

resources_fp = open('aws_ep/resources.tf', 'w')


waitt = '''
resource "time_sleep" "wait_2_seconds" {
  create_duration = "2s"
}

'''
resources_fp.writelines(waitt)


counter = 1
for k,p in input['Policies'].items():
    # t = datetime.datetime.now().strftime('%Y-%m-%d')
    # policy_name = p.get('name')
    policy_name = k
    policy_names.append(policy_name)
    
    path = p.get('path', '/')
    description = p.get('description', '{} description'.format(policy_name))
    statement = {
        "Effect": p['Effect'],
    }
    if p.get('Action', None):
        statement['Action'] = p['Action']
    if p.get('NotAction', None):
        statement['NotAction'] = p['NotAction']
    if p.get('Resource', None):
        statement['Resource'] = p['Resource']
    if p.get('NotResource', None):
        statement['NotResource'] = p['NotResource']
    if p.get('Condition', None):
        statement['Condition'] = p['Condition']
    if p.get('Principal', None):
        statement['Principal'] = p['Principal']
    if p.get('NotPrincipal', None):
        statement['NotPrincipal'] = p['NotPrincipal']

    # policy1 = aws.iam.Policy(
    #     name=policyName,
    #     path=path,
    #     description=description,
    #     policy=json.dumps({
    #         "Version": "2012-10-17",
    #         "Statement": [statement],
    #     })

    # )

    # name = policy_name
    # path = path
    # description = {}
    # policy = {
    #     "Version": "2012-10-17",
    #     "Statement": statement
    # }


    policy_doc = \
'''
resource "aws_iam_policy" "#name" {
    name = "#name"
    path = "#path"
    description = "#desc"
    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [#statement]
    })
    depends_on = [time_sleep.wait_2_seconds]
}
'''.replace('#count', str(counter)).replace('#name', policy_name).replace('#path', path).\
replace('#desc', description).replace('#statement', str(statement)).replace('\'', '"')
    counter += 1

    print(policy_doc)

    resources_fp.writelines(policy_doc)

resources_fp.close()



#############################################
## Create role and role policy attachment ###
#############################################


resources_fp = open('aws_ep/resources.tf', 'a')
counter = 0
for i in range(len(policy_names)):
    for j in range(i+1,len(policy_names)):
        counter += 1
        role_name = 'EpRole{}'.format(counter)
        pb = policy_names[j]
        tag = ''
        role_stat = '''{
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }'''

        role_doc = '''
resource "aws_iam_role" "iam_#name" {
    name = "#name"
    permissions_boundary = aws_iam_policy.#pname.arn
    assume_role_policy = jsonencode({
        "Version": "2012-10-17",
        "Statement": [#statement]
    })
    tags = {
        Name = "#tag"
    }
    depends_on = [time_sleep.wait_2_seconds]
}
'''.replace('#name', role_name).replace('#pname', policy_names[j]).\
    replace('#tag', tag).replace('#statement', str(role_stat)).replace('\'', '"')


        role_attachment = '''
resource "aws_iam_role_policy_attachment" "iam_attach_#name" {
    role = "#name"
    policy_arn = aws_iam_policy.#pname.arn
    depends_on = [aws_iam_role.iam_#name]
}
'''.replace('#name', role_name).replace('#pname', policy_names[i])

        print(role_doc)
        print(role_attachment)
        resources_fp.writelines(role_doc)
        resources_fp.writelines(role_attachment)

resources_fp.close()
