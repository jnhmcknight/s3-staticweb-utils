
from manager import Manager

import boto3
import pprint

from copy import deepcopy

manager = Manager()

pp = pprint.PrettyPrinter()
iam = boto3.client('iam')

@manager.command
def check_iam(user):
    user = iam.list_attached_user_policies(UserName=user)
    pp.pprint(user)


@manager.command
def check_buckets():
    pp.pprint(boto3.client('s3').list_buckets())


@manager.command
def check_distros():
    pp.pprint(boto3.client('cloudfront').list_distributions())


@manager.command
def check_route53():
    pp.pprint(boto3.client('route53').list_hosted_zones())


@manager.command
def check_acm():
    pp.pprint(boto3.client('acm').list_certificates())
