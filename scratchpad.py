__author__ = 'stormacq'

# import boto.ec2
#
# conn = boto.ec2.connect_to_region('eu-west-1',aws_access_key_id='AKIAJYOOSDTEG7UFTOOQ',
#                                   aws_secret_access_key='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')
# reservations = conn.get_all_instances(filters={"tag:Name" : "SB", "tag:Project" : "B"})
# instances = [i for r in reservations for i in r.instances]
# print instances

# import pystache
# value='arn'
# with open ("cfn/subnetfinder_test.template.json", "r") as cfnTemplateFile:
#     testTemplateRaw=cfnTemplateFile.read()
# topicARN = {'topic_arn' : value }
# testTemplate = pystache.render(testTemplateRaw, topicARN)
#
# print '-'
# print testTemplateRaw
# print '-'
# print testTemplate

import boto.ec2
print boto.ec2.regions()

import boto.vpc
conn = boto.vpc.connect_to_region('eu-west-1')
subnets = conn.get_all_subnets(filters={"tag:env" : "test"})
print subnets