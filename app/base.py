
from manager import Manager

from . import s3, cf

manager = Manager()

@manager.command
def setup_static_hosting(domain):
    print 'Setting up bucket: {}'.format(domain)
    s3.setup_bucket(domain, index_doc='index.html', error_doc='404/index.html')
    print 'Setting up cloudfront for {}'.format(domain)
    cf.setup_distro(domain)

    if not domain.startswith('www.'):
        print 'Setting up bucket: www.{}'.format(domain)
        s3.setup_bucket('www.{}'.format(domain), redirect_domain=domain, redirect_proto='https')
        print 'Setting up cloudfront for www.{}'.format(domain)
        cf.setup_distro('www.{}'.format(domain))
