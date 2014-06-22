#!/bin/bash -x

exec 3>&1 # "save" stdout to fd 3
exec &>> /home/ec2-user/create.log

function error_exit() {
    echo "{\"Reason\": \"$1\"}" >&3 3>&- # echo reason to stdout (instead of log) and then close fd 3
    exit $2
}

if [ -z "${Event_ResourceProperties_TagName}" ]
then
    error_exit "TagName is required." 64
fi

if [ -z "${Event_ResourceProperties_TagValue}" ]
then
    error_exit "TagValue is required." 64
fi

if [ -z "${Event_ResourceProperties_VpcId}" ]
then
    SN=$(/home/ec2-user/findSubnet.py -N ${Event_ResourceProperties_TagName} -V ${Event_ResourceProperties_TagValue})
    SN_ret=$?
else
    SN=$(/home/ec2-user/findSubnet.py -P ${Event_ResourceProperties_VpcId} -N ${Event_ResourceProperties_TagName} -V ${Event_ResourceProperties_TagVersion})
    SN_ret=$?
fi

if [ $SN_ret -ne 0 ]
then
    error_exit "findSubnet.py failed." $SN_ret
else
    echo "{ \"PhysicalResourceId\" : \"FAKE-000000\", \"Data\" : $SN }" >&3 3>&-  # echo success to stdout
                                                                                  # (instead of log) and then close
                                                                                  # fd 3
    exit 0
fi