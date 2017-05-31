
from manager import Manager

import boto3
import uuid

from copy import deepcopy

manager = Manager()

cf = boto3.client('cloudfront')

DISTRO_CONFIG = {
    'Aliases': {
        'Quantity': 0,
        'Items': []
    },
    'CacheBehaviors': {
        'Quantity': 0
    },
    'Comment': '',
    'DefaultRootObject': 'index.html',
    'Origins': {
        'Quantity': 1,
        'Items': [
            {
                'Id': 'S3-{bucket}',
                'DomainName': '{bucket}.s3-website-us-east-1.amazonaws.com',
                'OriginPath': '',
                'CustomHeaders': {
                    'Quantity': 0
                },
                'CustomOriginConfig': {
                    'HTTPPort': 80,
                    'HTTPSPort': 443,
                    'OriginProtocolPolicy': 'http-only',
                    'OriginSslProtocols': {
                        'Quantity': 3,
                        'Items': [
                            'TLSv1',
                            'TLSv1.1',
                            'TLSv1.2'
                        ]
                    }
                }
            },
        ]
    },
    'DefaultCacheBehavior': {
        'TargetOriginId': 'S3-{bucket}',
        'ForwardedValues': {
            'Cookies': {
                'Forward': 'none',
            },
            'Headers': {
                'Quantity': 8,
                'Items': [
                    'Accept',
                    'CloudFront-Is-Desktop-Viewer',
                    'CloudFront-Is-Mobile-Viewer',
                    'CloudFront-Is-SmartTV-Viewer',
                    'CloudFront-Is-Tablet-Viewer',
                    'CloudFront-Viewer-Country',
                    'Host',
                    'Origin'
                ]
            },
            'QueryString': True,
            'QueryStringCacheKeys': {
                'Quantity': 1,
                'Items': [
                    'version'
                ]
            }
        },
        'TrustedSigners': {
            'Enabled': False,
            'Quantity': 0,
            'Items': []
        },
        'ViewerProtocolPolicy': 'redirect-to-https',
        'MinTTL': 0,
        'AllowedMethods': {
            'Quantity': 3,
            'Items': [
                'GET',
                'HEAD',
                'OPTIONS'
            ]
        }
    },
    'PriceClass': 'PriceClass_All',
    'Enabled': True,
    'ViewerCertificate': {
        'ACMCertificateArn': '{acm_certificate_arn}',
        'Certificate': '{acm_certificate_arn}',
        'CertificateSource': 'acm',
        'SSLSupportMethod': 'sni-only',
        'MinimumProtocolVersion': 'TLSv1'
    },
    'HttpVersion': 'http2',
    'IsIPV6Enabled': True
}


@manager.command
def setup_distro(domain):
    config = deepcopy(DISTRO_CONFIG)
    config['Aliases']['Items'].append(domain)
    config['Aliases']['Quantity'] = len(config['Aliases']['Items'])
    config['DefaultCacheBehavior']['TargetOriginId'] = config['DefaultCacheBehavior']['TargetOriginId'].format(bucket=domain)
    config['Origins']['Items'][0]['Id'] = config['Origins']['Items'][0]['Id'].format(bucket=domain)
    config['Origins']['Items'][0]['DomainName'] = config['Origins']['Items'][0]['DomainName'].format(bucket=domain)

    cert_arn = acm.get_cert_arn(domain)
    if cert_arn:
        config['ViewerCertificate']['ACMCertificateArn'] = cert_arn
        config['ViewerCertificate']['Certificate'] = cert_arn
    else:
        del(config['ViewerCertificate'])

    config['CallerReference'] = str(uuid.uuid4())
    distro = cf.create_distribution(DistributionConfig=config)
