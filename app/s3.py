
from manager import Manager

import boto3
import json
import os
import sys
import yaml
import uuid
import pprint

from copy import deepcopy

manager = Manager()

pp = pprint.PrettyPrinter()
s3 = boto3.client('s3')

META_REDIRECT_TEMPLATE = '''
<html>
<head>
  <meta http-equiv="refresh" content="0;url={}">
</head>
</html>
'''

BUCKET_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AddPerm",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::{bucket}/*"
        }
    ]
}

BUCKET_CORS = {
    'CORSRules': [{
        'AllowedOrigins': [
            '*'
        ],
        'AllowedMethods': [
            'GET'
        ],
        'AllowedHeaders': [
            'Authorization',
            'Option'
        ],
        'MaxAgeSeconds': 3000
    }]
}

@manager.command
def check_index(bucket_name):
    obj = {
        'Bucket': bucket_name,
        'Key': 'index.html'
    }
    obj = s3.get_object(**obj)
    pp.pprint(s3.get_object_acl(**obj))


@manager.command
def check_bucket(bucket_name):
    bucket = boto3.resource('s3').Bucket(bucket_name)
    cors = bucket.Cors()
    cors.load()
    pp.pprint(cors.cors_rules)

    policy = bucket.Policy()
    policy.load()
    pp.pprint(policy.policy)

    website = bucket.Website()
    website.load()
    pp.pprint(website)


@manager.command
def setup_bucket(bucket_name, redirect_domain=None, redirect_proto=None, index_doc=None, error_doc=None):
    bucket = boto3.resource('s3').Bucket(bucket_name)
    bucket.create(ACL='public-read')
    bucket.Cors().put(CORSConfiguration=BUCKET_CORS)
    policy = deepcopy(BUCKET_POLICY)
    policy['Statement'][0]['Resource'] = policy['Statement'][0]['Resource'].format(bucket=bucket_name)
    bucket.Policy().put(Policy=json.dumps(policy))

    config = {}

    if redirect_domain:
        config.update({
            'RedirectAllRequestsTo': {
                'HostName': redirect_domain
            }
        })
        if redirect_proto:
            config['RedirectAllRequestsTo'].update({
                'Protocol': redirect_proto
            })

    if index_doc:
        config.update({
            'IndexDocument': {
                'Suffix': index_doc
            }
        })

    if error_doc:
        config.update({
            'ErrorDocument': {
                'Key': error_doc
            }
        })

    bucket.Website().put(WebsiteConfiguration=config)


@manager.command
def setup_redirects(bucket, redirects_file):
    redirects = load_redirects(redirects_file)
    for source, destination in redirects.iteritems():
        setup_redirect(bucket, source, destination)


@manager.command
def setup_redirect(bucket, source, destination):
    if not source or not destination:
        print 'Cannot setup a redirect without a source and destination!'
        sys.exit(1)

    print 'Setting redirect for {} to {}'.format(source, destination)
    kwargs = {
        'WebsiteRedirectLocation': destination
    }

    meta_redirect_file = '/tmp/{}.html'.format(uuid.uuid4())
    try:
        with open(meta_redirect_file, 'w') as filehandle:
            filehandle.write(META_REDIRECT_TEMPLATE.format(destination))

    except IOError:
        print 'Cannot write meta redirect file: {}'.format(meta_redirect_file)
        sys.exit(1)
    
    upload_file_as(bucket, meta_redirect_file, source, **kwargs)


@manager.command
def upload_file_as(bucket, filename, keyname, **kwargs):
    if not bucket or not filename:
        print 'You must specify both a bucket and a file to upload'
        sys.exit(1)

    if not keyname:
        keyname = os.path.basename(filename)

    if 'ACL' not in kwargs:
        kwargs['ACL'] = 'public-read'

    try:
        with open(filename, 'r') as filehandle:

            kwargs['Bucket'] = bucket
            kwargs['Body'] = filehandle
            kwargs['Key'] = keyname

            s3.put_object(**kwargs)

    except IOError:
        print 'Cannot upload file. It does not exist or was not readable: {}'.format(filename)
        sys.exit(1)


def load_redirects(filename):
    redirects = {}

    try:
        with open(filename, 'r') as filehandle:
            redirects = yaml.load(filehandle)

    except IOError:
        print 'Redirect list does not exist: {}'.format(filename)
        sys.exit(1)

    return redirects
