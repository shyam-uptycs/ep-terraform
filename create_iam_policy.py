import datetime
import json
import os
import pathlib
import argparse
from terraform_lib.utils import TerraformUtil
import requests
import threading
import re
#import hcl
    
ROOT_PATH = pathlib.Path(__file__).parent.resolve()


class ExternalIdGen:

    def __init__(self):
        self._external_id_lock = threading.Lock()

    def get_external_id(self):
        external_id = ""
        with self._external_id_lock:
            import uuid
            external_id = str(uuid.uuid4())
        return external_id

# def create_aws_integration_tf(aws_account_id, external_id):
#     url = 'https://raw.githubusercontent.com/uptycslabs/terraform-aws-iam-config/main/variables.tf'
#     tf_module_text = requests.get(url).text
#     aws_account_tf = open('{}/variables.tf'.format(args.component), 'w+')
#     aws_account_tf.write(tf_module_text)
#     aws_account_tf.close()

#     url = 'https://raw.githubusercontent.com/uptycslabs/terraform-aws-iam-config/main/README.md'
#     tf_module_text = requests.get(url).text
#     final_tf_module_text = 'module "iam-config"'+tf_module_text.split('module "iam-config"')[1].split('```')[0]
#     final_tf_module_text = re.sub('aws_account_id.+"1234567890"', 'aws_account_id  = "{}"'.format(aws_account_id), final_tf_module_text)   
#     final_tf_module_text = re.sub('external_id.+"f09cd4ae-76f1-4373-88da-de721312803d"', 
#         'external_id  = "{}"'.format(external_id), final_tf_module_text)
#     final_tf_module_text = """{}
# output "external_id" {{
#   value = var.external_id
# }}""".format(final_tf_module_text)
#     aws_account_tf = open('{}/aws_account.tf'.format(args.component), 'w+')
#     aws_account_tf.write(final_tf_module_text)
#     aws_account_tf.close()

# def aws_account_integration(tf_obj, args):
#     if 'apply' in args.action:
#         if args.aws_account_id:
#             aws_account_id = args.aws_account_id
#         else:
#             raise Exception('aws_account_id parameter is required for aws integration')
#         external_id = ExternalIdGen().get_external_id()
#         create_aws_integration_tf(aws_account_id=aws_account_id, external_id=external_id)
#         res1 = '{}'.format(tf_obj.init())
#         res1 = '{}\n{}'.format(res1, tf_obj.apply_with_vars(aws_account_id=aws_account_id, external_id=external_id))
#         return res1
#     elif 'destroy' in args.action:
#         external_id = '1234567890' # any dummy external id need to be passed
#         aws_account_id = '1234567890' # any dummy external id need to be passed
#         res1 = tf_obj.destroy_with_vars(aws_account_id=aws_account_id, external_id=external_id)
#         return res1

# def get_resource_with_name(resource):
#     rtype, rname=resource.split('=')
#     resourcestf = open('{}/resources.tf'.format(args.component), 'r')
#     res = hcl.load(resourcestf)
#     out = '{{ "resource": {{ "{}" : {{ "{}": {} }} }} }}'.format(rtype, rname, hcl.dumps(res['resource'][rtype][rname]))
#     return json.dumps(json.loads(out.encode()))

# def modify_resource_with_name(resource_json):
#     rdict = json.loads(resource_json)
#     resourcestf = open('{}/resources.tf'.format(args.component), 'r')
#     rdata = hcl.load(resourcestf)
#     rdata['resource'][rdict['type']][rdict['name']][rdict['attr']] = rdict['value']
#     out = '{{ "resource": {{ "{}" : {{ "{}": {} }} }} }}'.format(rdict['type'], rdict['name'], hcl.dumps(rdata['resource'][rdict['type']][rdict['name']]))
#     f = open('{}/resources_override.tf.json'.format(args.component), 'w')
#     f.write(out)
#     f.close()

    

# def process_aws_cloud_data(args):
#     t = TerraformUtil(args.component)
#     maintf = open('{}/main.tf'.format(args.component), 'w+')
#     maintf.write("""
#     provider "aws" {{
#         region     = "{}"
#         profile = "{}"
#     }}
#     """.format(args.region, args.profile))
#     maintf.close()

#     if 'aws_role_arn' in args.component and 'output' not in args.action:                
#         res1 = aws_account_integration(tf_obj=t, args=args)
#         return res1

#     if 'apply' in args.action:
#         res1 = '{}'.format(t.init())
#         res1 = '{}\n{}'.format(res1, t.apply())
#     elif 'destroy' in args.action:
#         res1 = '{}'.format(t.destroy())
#     return res1




input = json.load(open('policies.json', 'r'))


for k,p in input['Policies'].items():
    policy_name = p.get('name', 'policy_{}'.format(datetime.datetime.now()))
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
resource "aws_iam_policy" "policy" {
    name = "#name"
    path = "#path"
    description = "#desc"
    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [#statement]
    })
}
'''.replace('#name', policy_name).replace('#path', path).replace('#desc', description).replace('#statement', str(statement)).replace('\'', '"')


    print(policy_doc)