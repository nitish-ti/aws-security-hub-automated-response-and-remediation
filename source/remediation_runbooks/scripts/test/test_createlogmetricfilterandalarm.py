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
import botocore.session
from botocore.stub import Stubber
from botocore.config import Config
import pytest

import CreateLogMetricFilterAndAlarm as logMetricAlarm
import unittest

my_session = boto3.session.Session()
my_region = my_session.region_name


def test_verify(mocker):

    event = {
        'FilterName': 'test_filter',
        'FilterPattern': 'test_pattern',
        'MetricName': 'test_metric',
        'MetricNamespace': 'test_metricnamespace',
        'MetricValue': 'test_metric_value',
        'AlarmName': 'test_alarm',
        'AlarmDesc': 'alarm_desc',
        'AlarmThreshold': 'alarm_threshold',
        'LogGroupName': 'test_log'
    }
    context = {}
    mocker.patch('CreateLogMetricFilterAndAlarm.put_metric_filter')
    mocker.patch('CreateLogMetricFilterAndAlarm.put_metric_alarm')
    metric_filter_spy = mocker.spy(logMetricAlarm, 'put_metric_filter')
    metric_alarm_spy = mocker.spy(logMetricAlarm, 'put_metric_alarm')
    logMetricAlarm.verify(event, context)
    metric_filter_spy.assert_called_once_with('test_log', 'test_filter', 'test_pattern', 'test_metric', 'test_metricnamespace', 'test_metric_value')
    metric_alarm_spy.assert_called_once_with('test_alarm', 'alarm_desc', 'alarm_threshold', 'test_metric', 'test_metricnamespace')


def test_put_metric_filter_pass(mocker):
    event = {
        'FilterName': 'test_filter',
        'FilterPattern': 'test_pattern',
        'MetricName': 'test_metric',
        'MetricNamespace': 'test_metricnamespace',
        'MetricValue': 'test_metric_value',
        'AlarmName': 'test_alarm',
        'AlarmDesc': 'alarm_desc',
        'AlarmThreshold': 'alarm_threshold',
        'LogGroupName': 'test_log'
    }

    BOTO_CONFIG = Config(
        retries={
            'mode': 'standard'
        },
        region_name=my_region
    )
    logs = botocore.session.get_session().create_client('logs', config=BOTO_CONFIG)
    logs_stubber = Stubber(logs)

    logs_stubber.add_response(
        'put_metric_filter',
        {},
        {
            'logGroupName': event['LogGroupName'],
            'filterName': event['FilterName'],
            'filterPattern': event['FilterPattern'],
            'metricTransformations': [
                {
                    'metricName': event['MetricName'],
                    'metricNamespace':event['MetricNamespace'],
                    'metricValue': str (event['MetricValue'])
                },
            ]
        }
    )
    logs_stubber.activate()
    mocker.patch('CreateLogMetricFilterAndAlarm.get_service_client', return_value = logs )
    logMetricAlarm.put_metric_filter(
        event['LogGroupName'], event['FilterName'], event['FilterPattern'],
        event['MetricName'], event['MetricNamespace'], event['MetricValue']
    )

    assert logs_stubber.assert_no_pending_responses() is None
    logs_stubber.deactivate()


def test_put_metric_filter_error(mocker):
    event = {
        'FilterName': 'test_filter',
        'FilterPattern': 'test_pattern',
        'MetricName': 'test_metric',
        'MetricNamespace': 'test_metricnamespace',
        'MetricValue': 'test_metric_value',
        'AlarmName': 'test_alarm',
        'AlarmDesc': 'alarm_desc',
        'AlarmThreshold': 'alarm_threshold',
        'LogGroupName': 'test_log'
    }

    BOTO_CONFIG = Config(
        retries={
            'mode': 'standard'
        },
        region_name=my_region
    )
    logs = botocore.session.get_session().create_client('logs', config=BOTO_CONFIG)
    logs_stubber = Stubber(logs)

    logs_stubber.add_client_error(
        'put_metric_filter',
        'CannotAddFilter'
    )

    logs_stubber.activate()
    mocker.patch('CreateLogMetricFilterAndAlarm.get_service_client', return_value=logs)
    with pytest.raises(SystemExit) as pytest_wrapped_exception:
        logMetricAlarm.put_metric_filter(
            event['LogGroupName'], event['FilterName'], event['FilterPattern'],
            event['MetricName'], event['MetricNamespace'], event['MetricValue']
        )
    assert pytest_wrapped_exception.type == SystemExit


def test_put_metric_alarm(mocker):
    event = {
        'FilterName': 'test_filter',
        'FilterPattern': 'test_pattern',
        'MetricName': 'test_metric',
        'MetricNamespace': 'test_metricnamespace',
        'MetricValue': 'test_metric_value',
        'AlarmName': 'test_alarm',
        'AlarmDesc': 'alarm_desc',
        'AlarmThreshold': 1,
        'LogGroupName': 'test_log'
    }

    BOTO_CONFIG = Config(
        retries={
            'mode': 'standard'
        },
        region_name=my_region
    )
    cloudwatch = botocore.session.get_session().create_client('cloudwatch', config=BOTO_CONFIG)
    cloudwatch_stubber = Stubber(cloudwatch)

    cloudwatch_stubber.add_response(
        'put_metric_alarm',
        {},
        {
            'AlarmName': event['AlarmName'],
            'AlarmDescription': event['AlarmDesc'],
            'ActionsEnabled': False,
            'MetricName': event['MetricName'],
            'Namespace': event['MetricNamespace'],
            'Statistic': 'Sum',
            'Period': 300,
            'Unit': 'Seconds',
            'EvaluationPeriods': 240,
            'Threshold': (event['AlarmThreshold']),
            'ComparisonOperator': 'GreaterThanOrEqualToThreshold'
        }
    )
    cloudwatch_stubber.activate()
    mocker.patch('CreateLogMetricFilterAndAlarm.get_service_client', return_value=cloudwatch)
    logMetricAlarm.put_metric_alarm(
        event['AlarmName'], event['AlarmDesc'], event['AlarmThreshold'],
        event['MetricName'], event['MetricNamespace']
    )
    assert cloudwatch_stubber.assert_no_pending_responses() is None
    cloudwatch_stubber.deactivate()


def test_put_metric_alarm_error(mocker):
    event = {
        'FilterName': 'test_filter',
        'FilterPattern': 'test_pattern',
        'MetricName': 'test_metric',
        'MetricNamespace': 'test_metricnamespace',
        'MetricValue': 'test_metric_value',
        'AlarmName': 'test_alarm',
        'AlarmDesc': 'alarm_desc',
        'AlarmThreshold': 1,
        'LogGroupName': 'test_log'
    }

    BOTO_CONFIG = Config(
        retries={
            'mode': 'standard'
        },
        region_name=my_region
    )
    cloudwatch = botocore.session.get_session().create_client('cloudwatch', config=BOTO_CONFIG)
    cloudwatch_stubber = Stubber(cloudwatch)

    cloudwatch_stubber.add_client_error(
        'put_metric_alarm',
        'CannotAddAlarm'
    )
    cloudwatch_stubber.activate()
    mocker.patch('CreateLogMetricFilterAndAlarm.get_service_client', return_value=cloudwatch)

    with pytest.raises(SystemExit) as pytest_wrapped_exception:
        logMetricAlarm.put_metric_alarm(
            event['AlarmName'], event['AlarmDesc'], event['AlarmThreshold'],
            event['MetricName'], event['MetricNamespace']
        )
    assert pytest_wrapped_exception.type == SystemExit
    cloudwatch_stubber.deactivate()
