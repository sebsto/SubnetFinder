SubnetFinder
============

SubnetFinder is a sample [CloudFormation Custom Resource] (http://docs.aws.amazon
.com/AWSCloudFormation/latest/UserGuide/crpg-walkthrough.html) environment.

This Custom Resource uses VPC's DescribeSubnet's API to list every subnets having a specific tag=value in a given
region and a given VPCid

Use this Custom Resource to avoid hard coding subnet ids inside your CFN templates.

How does it works ?
-------------------

As a user, you need just two step to start to use this custom CFN resource

- First run ```subnetfinder.template.json``` to setup the infrastructure to offer a custom CFN resource.
- Take note of the SNS Topic ARN in the output section of that stack
- Prepare your stack to use this custom resource (see ```subnetfinder_sample.template.json``` below for an example)
- Run your own CFN template.

Available templates
-------------------

The ```cfn``` directory contains three CloudFormation templates:

- ```subnetfinder.template.json``` setup the complete infrastructure to implement the Custom Resource "SubnetFinder".
See below for a list of resources it creates.

- ```subnetfinder_test.template.json``` is used for unit testing.

- ```subnetfinder_sample.template.json``` is a sample template that shows how to use the Custom Resource :

```
{
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "Call SubnetFinder Custom Resource and give Subnet id as output.  You need to change VpcId, ServiceToken",

    "Resources": {
        "SubnetFinder": {
            "Type": "Custom::SubnetFinder",
            "Version": "1.0",
            "Properties": {
                "ServiceToken": "<<insert your topic ARN here>>",
                "VpcId": "<<insert your VPC id>>",
                "TagName" : "<<insert the tag name you're searching for>>",
                "TagValue" : "<<insert the tag value you're searching for>>"
            }
        }
    },

    "Outputs" : {
        "ResourceId" : { "Value" : { "Ref" : "SubnetFinder" } },
        "Subnet1" : { "Value" : { "Fn::GetAtt": [ "SubnetFinder", "<<insert the AZ name of your subnet>>"  ] } },
        "Subnet2" : { "Value" : { "Fn::GetAtt": [ "SubnetFinder", "<<insert the AZ name of your subnet>>"  ] } }
    }
}
```

Other resources in the template can use ```{ "Fn::GetAtt": [ "SubnetFinder", "<<insert the AZ name of your subnet>>"  ] }``` to refer to the Subnet ID.  Typically,
you will referer to the Subnet from an ```EC2::Instance``` resource.

This template can not run "as is", you need to insert your Custom Resource's implementation SNS Topic ARN as
```ServiceToken``` value and define your search parameters.

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
```findSubnet.py```, a custom python helper script

```cfn-resource-bridge``` will poll the queue, waiting for CloudFormation messages, and will call appropriate shell
scripts to respond to ```create```, ```update``` and ```delete``` requests.

In this example, ```update``` and ```delete``` shell scripts are empty.  Only ```create``` is implemented.  It uses
```findSubnet.py``` to retrieve the correct Subnet IDs.

TODO
----

- should ```findSubnet.py``` return a list of subnet ids or just one ??
- improve based on collected feedback
