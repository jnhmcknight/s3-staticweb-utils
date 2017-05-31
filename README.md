
Setting up a static site to be hosted on S3 but you're confused on how to set everything up?

Here's an easy helper script to take care of it for you.

## Basic Usage:

- Clone the repo locally and go into it
- `virtualenv venv`
- `venv/bin/pip install -r requirements.txt`
- Set your AWS credentials, in one of the ways described in the AWS-Cli documentation
- If you don't already have an ACM certificate for the desired domain:
  - `venv/bin/python ./manage.py request_cert example.com`
  - Approve the emails that Amazon AWS will send before proceeding
- `venv/bin/python ./manage.py setup_static_hosting example.com`
- Finally, you need to setup the Route53 records to point to the new CloudFront distributions


## Full Usage Options:

```
usage: manage.py [<namespace>.]<command> [<args>]

positional arguments:
  command     the command to run

optional arguments:
  -h, --help  show this help message and exit

available commands:
  setup_static_hosting     Sets up full static hosting at root domain with www. redirecting to it.
  
  [acm]
    get_cert_arn           Gets a Certificate ARN for a domain
    request_cert           Requests an ACM certificate for a domain
    show_cert              Shows an ACM certificate for a domain
  
  [cf]
    setup_distro           Sets up a CloudFront Distribution for static S3 hosting
  
  [iam]
    check_acm              Checks if the current user has access to ACM
    check_buckets          Checks if the current user has access to S3
    check_distros          Checks if the current user has access to CloudFront
    check_iam              Checks if the current user has access to IAM
    check_route53          Checks if the current user has access to Route53
  
  [s3]
    setup_bucket           Sets up a bucket for static hosting
    setup_redirect         Sets up a specific page to redirect to another page
    setup_redirects        Sets up a bunch of redirects based on a list in a file
    upload_file_as         Uploads a file to an S3 bucket
```
