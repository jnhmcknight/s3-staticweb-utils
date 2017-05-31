
from manager import Manager

from app import base, iam, acm, cf, s3

manager = Manager()

if __name__ == '__main__':
    manager.merge(base.manager)
    manager.merge(iam.manager, namespace='iam')
    manager.merge(acm.manager, namespace='acm')
    manager.merge(cf.manager, namespace='cf')
    manager.merge(s3.manager, namespace='s3')
    manager.main()
