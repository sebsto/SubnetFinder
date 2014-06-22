#!/usr/bin/python

import sys, argparse, logging
import requests
import boto.vpc, boto.ec2


__author__ = 'stormacq'
__version__ = 1.0

'''
Usage : findSubnet --region <region_name>
                   --tagName <name of the tag to search for>
                   --tagValue <value of the tag to search for>

Find a subnet in the given region, with the given tag Name=Value

Example : findSubnet --region eu-west-1 --tagName env --tagValue prod
'''

class SubnetFinder:

    def __init__(self, logger=None):

        self.logger = logger or logging.getLogger(self.__class__.__name__)

        #shared connection object - but do not cache it as it is region dependant
        self.conn = None

    def findSubnetInRegion(self, region, tagName, tagValue):
        '''
            Search for a Subnet in the specific region and
            the specific tag name and value
        '''

        if boto.ec2.get_region(region) is None:
            self.logger.error('Invalid region : %s' % region)
            return None

        self.conn = boto.vpc.connect_to_region(region)

        if self.conn is None:
            self.logger.error('Can not connect to AWS')
            return None

        subnetList = self.conn.get_all_subnets(filters={"tag:" + tagName : tagValue})
        self.logger.debug('Retrieved %d subnet' % len(subnetList))

        if len(subnetList) < 1:
            self.logger.warning('No subnet retrieved for region "%s" using filters %s=%s)' % (region, tagName,
                                tagValue))
            return None


        return subnetList

def main(finder, **kwargs):

    finder.logger.debug('Parameter tagName  = %s' % kwargs['tagname'])
    finder.logger.debug('Parameter tagValue = %s' % kwargs['tagvalue'])
    finder.logger.debug('Parameter region   = %s' % kwargs['region'])

    region = kwargs['region']
    if region is None:
        try:
            logger.warning('No region name given, trying to find one from EC2 instance meta data service')
            f = requests.get("http://169.254.169.254/latest/meta-data/placement/availability-zone/", timeout=1)
            region = f.text[:-1]
            logger.info('Using %s as region, provided by instance meta-data' % region)
        except requests.exceptions.Timeout:
            logger.error('Can not find region name (are you running this on EC2 ?). Abording.')
            sys.exit(-1)
        except:
            logger.error('Unknown error while trying to get region name. Abording.')
            sys.exit(-1)

    subnet = finder.findSubnetInRegion(region, kwargs['tagname'], kwargs['tagvalue'])
    if subnet is not None:
        print [s.id for s in subnet]
        sys.exit(0)
    else:
        sys.exit(-1)


if __name__ == '__main__':

    logging.basicConfig()
    logger = logging.getLogger('findSubnet')
    logger.setLevel(logging.DEBUG)
    finder = SubnetFinder(logger)

    if sys.version_info < (2, 7):
        logger.info('Using Python < 2.7')
        parser = argparse.ArgumentParser(description='Find a VPC Subnet with given tags')
        parser.add_argument('-v', '--version', action='version', version='%(prog)s v' +
        str(__version__))
    else:
        parser = argparse.ArgumentParser(description='Find a VPC Subnet with given tags', version='%(prog)s v' +
                                                                                            str(__version__))
    parser.add_argument('-r', '--region', type=str, help='Region name (default to local region when run on EC2)')
    parser.add_argument("-tn", "--tagname", type=str, help='Name of the Tag to search for', required=True)

    parser.add_argument('-tv', '--tagvalue', type=str, help='Value of the tag to search for')
    args = parser.parse_args()
    main(finder, **vars(args))
