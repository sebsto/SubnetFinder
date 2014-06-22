__author__ = 'stormacq'

import unittest
import logging
import datetime, time
import boto.cloudformation

from findSubnet import SubnetFinder

REGION = 'eu-west-1'

def setupVPC(logger, tagName, tagValue1, tagValue2):
    #create a VPC and 3 subnets for the purpose of this test
    # read template
    with open ("cfn/network.template.json", "r") as cfnTemplateFile:
        data=cfnTemplateFile.read()

    # connect to the appropriate region
    conn = boto.cloudformation.connect_to_region(REGION)

    # create the stack
    now = datetime.datetime.today().strftime('%Y%m%d-%H%M%S')
    stackID = conn.create_stack(stack_name='SubnetFinderUnitTest-' + now, template_body=data,
                                parameters=[('TagName',tagName), ('TagValue1',tagValue1), ('TagValue2',tagValue2)])

    stack = conn.describe_stacks(stackID)[0]
    #print vars(stack)
    logger.debug('Waiting for Unit Test Network Stack to be created')
    while stack.stack_status == 'CREATE_IN_PROGRESS':
        logger.debug('.')
        time.sleep(10)
        stack = conn.describe_stacks(stackID)[0]

    logger.debug('Unit Test Network stack created, status = %s' % stack.stack_status)
    return stack

def cleanupVPC(logger, stack):
    logger.debug('Deleting the Unit Test Network stack')
    conn = boto.cloudformation.connect_to_region(REGION)
    conn.delete_stack(stack.stack_id)

#TODO test tearup must create VPC and SUBNET instead of relying on my environment
class AMIFinderTest(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        import os,binascii

        logging.basicConfig()
        cls.logger = logging.getLogger(__name__)
        cls.logger.setLevel(logging.INFO)
        cls.finder = SubnetFinder(cls.logger)

        cls.TAG_NAME   = binascii.b2a_hex(os.urandom(3))
        cls.TAG_VALUE1 = binascii.b2a_hex(os.urandom(3))
        cls.TAG_VALUE2 = binascii.b2a_hex(os.urandom(3))

        logging.info('Creating temporary VPC for the execution of the test')
        cls.STACK = setupVPC(cls.logger, cls.TAG_NAME, cls.TAG_VALUE1, cls.TAG_VALUE2)
        cls.VPC_ID = cls.STACK.outputs[0].value



    @classmethod
    def tearDownClass(cls):
        logging.info('Deleting temporary VPC')
        cleanupVPC(cls.logger, cls.STACK)

    def test_SubnetFinder_VALUE1(self):
        subnets = self.finder.findSubnetInRegion(REGION, self.__class__.TAG_NAME, self.__class__.TAG_VALUE1)
        self.assertIsNotNone(subnets, 'Did not find subnets in %s for %s=%s' % (REGION, self.__class__.TAG_NAME,
                                                                                self.__class__.TAG_VALUE1))
        self.assertEqual(len(subnets), 1, '%s=%s must return one subnet' % (self.__class__.TAG_NAME,
                                                                            self.__class__.TAG_VALUE1))

    def test_SubnetFinder_VALUE2(self):
        subnets = self.finder.findSubnetInRegion(REGION, self.__class__.TAG_NAME, self.__class__.TAG_VALUE2)
        self.assertIsNotNone(subnets, 'Did not find subnets in %s for %s=%s' % (REGION, self.__class__.TAG_NAME,
                                                                                self.__class__.TAG_VALUE2))
        self.assertEqual(len(subnets), 2, '%s=%s must return two subnets' % (self.__class__.TAG_NAME,
                                                                          self.__class__.TAG_VALUE1))

    def test_SubnetFinder_UnknownTag(self):
        subnets = self.finder.findSubnetInRegion(REGION, 'xxx', self.__class__.TAG_VALUE2)
        self.assertIsNone(subnets, 'Did find subnets in %s for %s=%s' % (REGION, 'xxx',
                                                                               self.__class__.TAG_VALUE2))

    def test_SubnetFinder_Invalidregion(self):
        subnets = self.finder.findSubnetInRegion("xxx", self.__class__.TAG_NAME, self.__class__.TAG_VALUE2)
        self.assertIsNone(subnets, 'Found subnet in non existent region')

if __name__ == '__main__':
    unittest.main()