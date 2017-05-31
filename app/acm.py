
from manager import Manager

import boto3
import pprint

manager = Manager()

acm = boto3.client('acm')

@manager.command
def show_cert(domain):
    print pprint.PrettyPrinter().pprint(get_cert(domain))


def get_cert(domain):
    certs = acm.list_certificates()
    for cert in certs['CertificateSummaryList']:
        details = acm.describe_certificate(CertificateArn=cert['CertificateArn'])
        if cert['DomainName'] == domain:
            return details
        # Might be in the alternate names
        for alt in details['Certificate']['SubjectAlternativeNames']:
            if alt == domain:
                return details

    return None


@manager.command
def get_cert_arn(domain):
    cert = get_cert(domain)
    return cert['Certificate']['CertificateArn']


@manager.command
def request_cert(domain):
    alt_names = []
    validation = [{
        'DomainName': domain,
        'ValidationDomain': domain
    }]

    if not domain.startswith('www.'):
        alt_names.append('www.{}'.format(domain))
        validation.append({
            'DomainName': 'www.{}'.format(domain),
            'ValidationDomain': domain
        })

    cert = acm.request_certificate(
        DomainName=domain,
        SubjectAlternativeNames=alt_names,
        DomainValidationOptions=validation
    )
    return cert
