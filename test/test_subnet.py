__author__ = 'stormacq'

import unittest
import logging

from findSubnet import SubnetFinder


#TODO test tearup must create VPC and SUBNET instead of relying on my environment
class AMIFinderTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.basicConfig()
        cls.logger = logging.getLogger(__name__)
        cls.logger.setLevel(logging.INFO)
        cls.finder = SubnetFinder(cls.logger)

    def test_SubnetFinder_eu_west_1_PROD(self):
        subnets = self.finder.findSubnetInRegion('eu-west-1', 'env', 'prod')
        self.assertIsNotNone(subnets, 'Did not find subnets in eu-west-1 for env=prod')
        self.assertEqual(len(subnets), 2)

    def test_SubnetFinder_eu_west_1_TEST(self):
        subnets = self.finder.findSubnetInRegion('eu-west-1', 'env', 'test')
        self.assertIsNotNone(subnets, 'Did not find subnets in eu-west-1 for env=test')
        self.assertEqual(len(subnets), 1)

    def test_SubnetFinder_eu_west_1_UnknownTag(self):
        subnets = self.finder.findSubnetInRegion('eu-west-1', 'envXXX', 'test')
        self.assertIsNone(subnets, 'Did find subnets in eu-west-1 for envXXX=test')

    def test_SubnetFinder_Invalidregion(self):
        subnets = self.finder.findSubnetInRegion('eu-xxx-1', 'env', 'prod')
        self.assertIsNone(subnets, 'Found subnet in non existent region')

if __name__ == '__main__':
    unittest.main()