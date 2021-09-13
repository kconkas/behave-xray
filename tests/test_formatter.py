import datetime as dt
from unittest.mock import MagicMock, patch

import pytest
from behave.model_core import Status

from behave_xray.formatter import XrayFormatter, ScenarioOutline, XrayCloudFormatter
from behave_xray.helper import (
    get_test_execution_key_from_tag,
    get_test_plan_key_from_tag,
    get_testcase_key_from_tag,
    get_overall_status
)


@pytest.mark.parametrize(
    'tag, jira_id',
    [("jira.test_plan('JIRA-10')", 'JIRA-10'),
     ("JIRA.TEST_PLAN('JIRA-10')", 'JIRA-10')]
)
def test_test_plan_tag_parser(tag, jira_id):
    assert get_test_plan_key_from_tag(tag) == jira_id


@pytest.mark.parametrize(
    'tag, jira_id',
    [("jira.testcase('JIRA-10')", 'JIRA-10'),
     ("JIRA.TESTCASE('JIRA-10')", 'JIRA-10'),
     ('jira.testcase("JIRA-10")', 'JIRA-10'),
     ('jira.testcaseJIRA-10', 'JIRA-10'),  # outline scenario
     ("allure.testcase('JIRA-10')", 'JIRA-10')]
)
def test_test_case_tag_parser(tag, jira_id):
    assert get_testcase_key_from_tag(tag) == jira_id


@pytest.mark.parametrize(
    'tag, jira_id',
    [("jira.test_execution('JIRA-10')", 'JIRA-10'),
     ("JIRA.TEST_EXECUTION('JIRA-10')", 'JIRA-10')]
)
def test_test_execution_tag_parser(tag, jira_id):
    assert get_test_execution_key_from_tag(tag) == jira_id


@pytest.mark.parametrize(
    'statuses, expected_status',
    [
        ([Status.failed, Status.passed, Status.untested], Status.failed),
        ([Status.failed, Status.passed, Status.passed], Status.failed),
        ([Status.failed, Status.untested, Status.untested], Status.failed),
        ([Status.failed, Status.untested, Status.executing], Status.failed),
        ([Status.untested, Status.untested, Status.untested], Status.untested),
        ([Status.untested, Status.untested, Status.executing], Status.executing),
        ([Status.passed, Status.passed, Status.untested], Status.passed),
        ([Status.passed, Status.passed, Status.executing], Status.executing),
        ([Status.passed, Status.passed, Status.passed], Status.passed),
        ([Status.passed, Status.passed, Status.undefined], Status.undefined),  # Error in test code
        ([], Status.untested)
    ]
)
def test_overall_status(statuses, expected_status):
    assert get_overall_status(statuses) == expected_status, f'Failed for {statuses}'


def test_xray_formatter_return_correct_dictionary():
    mock_stream = MagicMock()
    mock_config = MagicMock()
    testdt = dt.datetime(2021, 4, 23, 16, 30, 2, 0, tzinfo=dt.timezone.utc)
    with patch('datetime.datetime') as dt_mock:
        dt_mock.now.return_value = testdt
        formatter = XrayFormatter(mock_stream, mock_config)

        formatter.testcases = {
            'JIRA-1': ScenarioOutline('JIRA-1', statuses=[Status.passed]),
            'JIRA-2': ScenarioOutline('JIRA-2', statuses=[Status.passed])
        }
        formatter.collect_tests()
        expected_output = {
            'info': {
                'finishDate': '2021-04-23T16:30:02+0000',
                'startDate': '2021-04-23T16:30:02+0000'
            },
            'tests': [
                {
                    'comment': '',
                    'examples': [],
                    'status': 'PASS',
                    'testKey': 'JIRA-1'
                },
                {
                    'comment': '',
                    'examples': [],
                    'status': 'PASS',
                    'testKey': 'JIRA-2'
                }
            ]
        }

        assert formatter.test_execution.as_dict() == expected_output


def test_xray_formatter_returns_correct_dictionary():
    mock_stream = MagicMock()
    mock_config = MagicMock()
    testdt = dt.datetime(2021, 4, 23, 16, 30, 2, 0, tzinfo=dt.timezone.utc)
    with patch('datetime.datetime') as dt_mock:
        dt_mock.now.return_value = testdt
        formatter = XrayFormatter(mock_stream, mock_config)

        formatter.testcases = {
            'JIRA-1': ScenarioOutline('JIRA-1', statuses=[Status.passed]),
            'JIRA-2': ScenarioOutline('JIRA-2', statuses=[Status.passed])
        }
        formatter.collect_tests()
        expected_output = {
            'info': {
                'finishDate': '2021-04-23T16:30:02+0000',
                'startDate': '2021-04-23T16:30:02+0000'
            },
            'tests': [
                {
                    'comment': '',
                    'examples': [],
                    'status': 'PASS',
                    'testKey': 'JIRA-1'
                },
                {
                    'comment': '',
                    'examples': [],
                    'status': 'PASS',
                    'testKey': 'JIRA-2'
                }
            ]
        }

        assert formatter.test_execution.as_dict() == expected_output


def test_xray_formatter_returns_correct_dictionary_for_outline_scenario():
    mock_stream = MagicMock()
    mock_config = MagicMock()
    testdt = dt.datetime(2021, 4, 23, 16, 30, 2, 0, tzinfo=dt.timezone.utc)
    with patch('datetime.datetime') as dt_mock:
        dt_mock.now.return_value = testdt
        formatter = XrayFormatter(mock_stream, mock_config)

        formatter.testcases = {
            'JIRA-1': ScenarioOutline(
                'JIRA-1',
                statuses=[Status.passed, Status.passed],
                is_outline=True
            ),
            'JIRA-2': ScenarioOutline(
                'JIRA-2',
                statuses=[Status.passed, Status.failed],
                is_outline=True)
        }
        formatter.collect_tests()
        expected_output = {
            'info': {
                'finishDate': '2021-04-23T16:30:02+0000',
                'startDate': '2021-04-23T16:30:02+0000'
            },
            'tests': [
                {
                    'comment': '',
                    'examples': ['PASS', 'PASS'],
                    'status': 'PASS',
                    'testKey': 'JIRA-1'
                },
                {
                    'comment': '',
                    'examples': ['PASS', 'FAIL'],
                    'status': 'FAIL',
                    'testKey': 'JIRA-2'
                }
            ]
        }

        assert formatter.test_execution.as_dict() == expected_output


def test_xray_cloud_formatter_return_correct_dictionary():
    mock_stream = MagicMock()
    mock_config = MagicMock()
    testdt = dt.datetime(2021, 4, 23, 16, 30, 2, 0, tzinfo=dt.timezone.utc)
    with patch('datetime.datetime') as dt_mock:
        dt_mock.now.return_value = testdt
        formatter = XrayCloudFormatter(mock_stream, mock_config)

        formatter.testcases = {
            'JIRA-1': ScenarioOutline(
                'JIRA-1',
                statuses=[Status.passed, Status.passed],
                is_outline=True
            ),
            'JIRA-2': ScenarioOutline(
                'JIRA-2',
                statuses=[Status.passed, Status.failed],
                is_outline=True)
        }
        formatter.collect_tests()
        expected_output = {
            'info': {
                'finishDate': '2021-04-23T16:30:02+0000',
                'startDate': '2021-04-23T16:30:02+0000'
            },
            'tests': [
                {
                    'comment': '',
                    'examples': ['PASSED', 'PASSED'],
                    'status': 'PASSED',
                    'testKey': 'JIRA-1'
                },
                {
                    'comment': '',
                    'examples': ['PASSED', 'FAILED'],
                    'status': 'FAILED',
                    'testKey': 'JIRA-2'
                }
            ]
        }

        assert formatter.test_execution.as_dict() == expected_output
