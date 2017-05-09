#!/usr/bin/env python

import argparse
import boto3
import os
import sys
import yaml
import uuid

client = boto3.client('s3')

meta_redirect_template = '''
<html>
<head>
  <meta http-equiv="refresh" content="0;url={}">
</head>
</html>
'''

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
            filehandle.write(meta_redirect_template.format(destination))

    except IOError:
        print 'Cannot write meta redirect file: {}'.format(meta_redirect_file)
        sys.exit(1)
    
    upload_file_as(bucket, meta_redirect_file, source, **kwargs)


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

            client.put_object(**kwargs)

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


parser = argparse.ArgumentParser()
parser.add_argument("bucket", help="Which bucket to put the redirect in", type=str)
parser.add_argument("redirects", help="The file with the list of redirects", type=str)
args = parser.parse_args()

redirects = load_redirects(args.redirects)
for source, destination in redirects.iteritems():
    setup_redirect(args.bucket, source, destination)

