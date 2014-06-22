SubnetFinder
============

SubnetFinder is a sample [CloudFormation Custom Resource] (http://docs.aws.amazon
.com/AWSCloudFormation/latest/UserGuide/crpg-walkthrough.html) environment.

This Custom Resource uses VPC's DescribeSubnet's API to list every subnets having a specific tag=value in a given
region and a given VPCid

Use this Custom Resource to avoid hard coding subnet ids inside your CFN templates.


Usage
-----

The ```cfn``` directory contains three CloudFormation templates:

- ```subnetfinder.template.json``` setup the complete infrastructure to implement the Custom Resource "SubnetFinder".
See
below for a list of resources it creates.

- ```subnetfinder_test.template.json``` is used for unit testing.

- ```subnetfinder_sample.template.json``` is a sample template that shows how to use the Custom Resource :

```
{
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "Create Infrastructure required to run finAMI Custom resource",

    "Resources": {
        "AMIFinderTest": {
            "Type": "Custom::AMIFinder",
            "Version": "1.0",
            "Properties": {
                "ServiceToken": "<insert SNS ARN here>",
                "Version": "2012"
            }
        }
    },
    "Outputs" : {
        "WindowAMIID" : {
            "Value" : { "Ref" : "AMIFinderTest" }
        }
    }
}
```

Other resources in the template can use ```{ "Ref" : "SubnetFinderTest" }``` to refer to the Subnet ID.  Typically,
you will referer to the Subnet from an ```EC2::Instance``` resource.

This template can not run "as is", you need to insert your Custom Resource's implementation SNS Topic ARN as
```ServiceToken``` value.

How does it work ?
------------------

The ```subnetfinder.template.json``` CFN template creates the environment to implement the custom resource :

- a SNS Topic - to be used by CFN to call the Custom Resource.  The SNS Topic ARN must be inserted in the
```subnetfinder_test.template.json``` and your other CFN templates using this Custom resource
- a SQS Queue subscribed to the topic
- a SQS Policy allowing SNS to post messages to the queue
- an IAM Role to allow an EC2 instance to read from the queue and to call DescribeImage EC2 API
- a Security Group allowing inbound SSH connections (debugging only - can be removed once everything is working)
- an EC2 Instance bootstrapped with [```cfn-resource-bridge```](https://github.com/aws/aws-cfn-resource-bridge) and
```findSubnet```, a custom python helper script

```cfn-resource-bridge``` will poll the queue, waiting for CloudFormation messages, and will call appropriate shell
scripts to respond to ```create```, ```update``` and ```delete``` requests.

In this example, ```update``` and ```delete``` shell scripts are empty.  Only ```create``` is implemented.  It uses ```findAMI``` to retrieve the correct AMI IDs.

TODO
----

- improve based on collected feedback
