#!/usr/bin/python
###############################################################################
#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.         #
#                                                                             #
#  Licensed under the Apache License Version 2.0 (the "License"). You may not #
#  use this file except in compliance with the License. A copy of the License #
#  is located at                                                              #
#                                                                             #
#      http://www.apache.org/licenses/LICENSE-2.0/                            #
#                                                                             #
#  or in the "license" file accompanying this file. This file is distributed  #
#  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express #
#  or implied. See the License for the specific language governing permis-    #
#  sions and limitations under the License.                                   #
###############################################################################

import boto3
import logging
import os
from botocore.config import Config

boto_config = Config(
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)

log = logging.getLogger()
LOG_LEVEL = str(os.getenv('LogLevel', 'INFO'))
log.setLevel(LOG_LEVEL)


def get_service_client(service_name):
    """
    Returns the service client for given the service name
    :param service_name: name of the service
    :return: service client
    """
    log.debug("Getting the service client for service: {}".format(service_name))
    return boto3.client(service_name, config=boto_config)


def put_metric_filter(cw_log_group, filter_name, filter_pattern, metric_name, metric_namespace, metric_value):
    """
    Puts the metric filter on the CloudWatch log group with provided values
    :param cw_log_group: Name of the CloudWatch log group
    :param filter_name: Name of the filter
    :param filter_pattern: Pattern for the filter
    :param metric_name: Name of the metric
    :param metric_namespace: Namespace where metric is logged
    :param metric_value: Value to be logged for the metric
    """
    logs_client = get_service_client('logs')
    log.debug("Putting the metric filter with values: {}".format([
        cw_log_group, filter_name, filter_pattern, metric_name, metric_namespace, metric_value]))
    try:
        logs_client.put_metric_filter(
            logGroupName=cw_log_group,
            filterName=filter_name,
            filterPattern=filter_pattern,
            metricTransformations=[
                {
                    'metricName': metric_name,
                    'metricNamespace': metric_namespace,
                    'metricValue': str(metric_value)
                },
            ]
        )
    except Exception as e:
        exit("Exception occurred while putting metric filter: " + str(e))
    log.debug("Successfully added the metric filter.")


def put_metric_alarm(alarm_name, alarm_desc, alarm_threshold, metric_name, metric_namespace):
    """
    Puts the metric alarm for the metric name with provided values
    :param alarm_name: Name for the alarm
    :param alarm_desc: Description for the alarm
    :param alarm_threshold: Threshold value for the alarm
    :param metric_name: Name of the metric
    :param metric_namespace: Namespace where metric is logged
    """
    cw_client = get_service_client('cloudwatch')
    log.debug("Putting the metric alarm with values {}".format(
        [alarm_name, alarm_desc, alarm_threshold, metric_name, metric_namespace]))
    try:
        cw_client.put_metric_alarm(
            AlarmName=alarm_name,
            AlarmDescription=alarm_desc,
            ActionsEnabled=False,
            MetricName=metric_name,
            Namespace=metric_namespace,
            Statistic='Sum',
            Period=300,
            Unit='Seconds',
            EvaluationPeriods=240,
            Threshold=alarm_threshold,
            ComparisonOperator='GreaterThanOrEqualToThreshold'
        )
    except Exception as e:
        exit("Exception occurred while putting metric alarm: " + str(e))
    log.debug("Successfully added metric alarm.")


def verify(event, context):
    log.info("Begin handler")
    log.debug("====Print Event====")
    log.debug(event)

    filter_name = event['FilterName']
    filter_pattern = event['FilterPattern']
    metric_name = event['MetricName']
    metric_namespace = event['MetricNamespace']
    metric_value = event['MetricValue']
    alarm_name = event['AlarmName']
    alarm_desc = event['AlarmDesc']
    alarm_threshold = event['AlarmThreshold']
    cw_log_group = event['LogGroupName']

    put_metric_filter(cw_log_group, filter_name, filter_pattern, metric_name, metric_namespace, metric_value)
    put_metric_alarm(alarm_name, alarm_desc, alarm_threshold, metric_name, metric_namespace)
    return {
        "response": {
            "message": f'Created filter {event["FilterName"]} for metric {event["MetricName"]}, and alarm {event["AlarmName"]}',
            "status": "Success"
        }
    }
