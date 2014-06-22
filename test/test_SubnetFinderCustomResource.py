__author__ = 'stormacq'

import os, binascii
import unittest, logging
import datetime, time
import pystache
import boto.cloudformation

class SubnetFinderCustomResourceTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.basicConfig()
        cls.logger = logging.getLogger(__name__)
        cls.logger.setLevel(logging.INFO)

    def setupVPC(self, region, tagName, tagValue1, tagValue2):
        #create a VPC and 3 subnets for the purpose of this test
        # read template
        with open ("cfn/network.template.json", "r") as cfnTemplateFile:
            data=cfnTemplateFile.read()

        # connect to the appropriate region
        conn = boto.cloudformation.connect_to_region(region)

        # create the stack
        now = datetime.datetime.today().strftime('%Y%m%d-%H%M%S')
        stackID = conn.create_stack(stack_name='SubnetFinderUnitTest-VPC-' + now, template_body=data,
                                    parameters=[('TagName',tagName), ('TagValue1',tagValue1), ('TagValue2',tagValue2)])

        stack = conn.describe_stacks(stackID)[0]
        #print vars(stack)
        self.logger.debug('Waiting for Unit Test Network Stack to be created')
        while stack.stack_status == 'CREATE_IN_PROGRESS':
            self.logger.debug('.')
            time.sleep(10)
            stack = conn.describe_stacks(stackID)[0]

        self.logger.debug('Unit Test Network stack created, status = %s' % stack.stack_status)
        return stack

    def cleanupVPC(self, region, stackVPC):
        self.logger.debug('Deleting the Unit Test Network stack')
        conn = boto.cloudformation.connect_to_region(region)
        conn.delete_stack(stackVPC.stack_id)

    def createCustomResource(self, region):
        # read template
        with open ("cfn/subnetfinder.template.json", "r") as cfnTemplateFile:
            data=cfnTemplateFile.read()

        # connect to the appropriate region
        conn = boto.cloudformation.connect_to_region(region)

        # create the stack
        now = datetime.datetime.today().strftime('%Y%m%d-%H%M%S')
        stackID = conn.create_stack(stack_name='SubnetFinderUnitTest-CustomResource-' + now, template_body=data)
        stack = conn.describe_stacks(stackID)[0]
        #print vars(stack)
        self.logger.debug('Waiting for Custom Resource Stack to be created')
        while stack.stack_status == 'CREATE_IN_PROGRESS':
            self.logger.debug('.')
            time.sleep(10)
            stack = conn.describe_stacks(stackID)[0]

        self.logger.debug('Custom Resource Stack created, status = %s' % stack.stack_status)
        return stack

    def deleteStack(self, region, stackID):
        self.logger.debug('Deleting the Custom Resource stack')
        conn = boto.cloudformation.connect_to_region(region)
        conn.delete_stack(stackID)

    def doTest(self, region, azName):
        stack     = None
        stackTest = None
        stackVPC  = None

        try:
            TAG_NAME   = binascii.b2a_hex(os.urandom(3))
            TAG_VALUE1 = binascii.b2a_hex(os.urandom(3))
            TAG_VALUE2 = binascii.b2a_hex(os.urandom(3))

            # create test VPC
            stackVPC = self.setupVPC(region,TAG_NAME, TAG_VALUE1, TAG_VALUE2)

            # create custom resource stack
            stack = self.createCustomResource(region)

            # retrieve topic ARN in output
            with open ("cfn/subnetfinder_test.template.json", "r") as cfnTemplateFile:
                testTemplateRaw=cfnTemplateFile.read()
            context = {'topic_arn' :  stack.outputs[0].value,
                       'vpc_id' : stackVPC.outputs[0].value,
                       'tag_name' : TAG_NAME,
                       'tag_value' : TAG_VALUE1,
                       'az_name' : azName}
            testTemplate = pystache.render(testTemplateRaw, context)

            # launch sample template stack
            conn = boto.cloudformation.connect_to_region(region)
            now = datetime.datetime.today().strftime('%Y%m%d-%H%M%S')
            stackID = conn.create_stack(stack_name='SubnetFinderUnitTest-CRCLient-' + now,
                                        template_body=testTemplate)
            stackTest = conn.describe_stacks(stackID)[0]
            #print vars(stackTest)
            self.logger.debug('Waiting for Test Stack to be created')
            while stackTest.stack_status == 'CREATE_IN_PROGRESS':
                self.logger.debug('.')
                time.sleep(10)
                stackTest = conn.describe_stacks(stackID)[0]
            self.logger.debug('Test Stack created, status = %s' % stackTest.stack_status)

        except:
            import sys
            e = sys.exc_info()[0]
            self.logger.error('Exception while creating CFN Stacks : %s' % e)

        finally:
            # delete custom resource stack
            if stackTest is not None:
                self.deleteStack(region, stackTest.stack_id)
                time.sleep(10)
            if stack is not None:
                self.deleteStack(region, stack.stack_id)
            if stackVPC is not None:
                self.deleteStack(region, stackVPC.stack_id)

        return stackTest

    def test_eu_west_1(self):
        region = 'eu-west-1'
        azName = 'eu-west-1a'
        stack = self.doTest(region, azName)
        self.assertFindSubnet(stack)

    def test_us_east_1(self):
        region = 'us-east-1'
        azName = 'us-east-1a'
        stack = self.doTest(region, azName)
        self.assertFindSubnet(stack)

    def test_us_west_1(self):
        region = 'us-west-1'
        azName = 'us-west-1a'
        stack = self.doTest(region, azName)
        self.assertFindSubnet(stack)

    def test_us_west_2(self):
        region = 'us-west-2'
        azName = 'us-west-2a'
        stack = self.doTest(region, azName)
        self.assertFindSubnet(stack)

    def test_sa_east_1(self):
        region = 'sa-east-1'
        azName = 'sa-east-1a'
        stack = self.doTest(region, azName)
        self.assertFindSubnet(stack)

    def test_ap_southeast_1(self):
        region = 'ap-southeast-1'
        azName = 'ap-southeast-1a'
        stack = self.doTest(region, azName)
        self.assertFindSubnet(stack)

    def test_ap_southeast_2(self):
        region = 'ap-southeast-2'
        azName = 'ap-southeast-2a'
        stack = self.doTest(region, azName)
        self.assertFindSubnet(stack)

    def test_ap_northeast_1(self):
        region = 'ap-northeast-1'
        azName = 'ap-northeast-1a'
        stack = self.doTest(region, azName)
        self.assertFindSubnet(stack)

    def assertFindSubnet(self, stack):
        self.assertEqual(len(stack.outputs), 2, "Test Stack outputs len is not 2")
        self.assertRegexpMatches( stack.outputs[0].value, '^FAKE-.*$',"Test Stack does not return an FAKE- id")
        self.assertRegexpMatches( stack.outputs[1].value, '^subnet-.*$',"Test Stack does not return an subnet- id")

if __name__ == '__main__':
    #todo migrate to nose or equivalent to run these tests in parallel
    unittest.main()