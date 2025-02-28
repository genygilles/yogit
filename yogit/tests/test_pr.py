from datetime import datetime

from unittest.mock import patch
import responses
import pytest
from click.testing import CliRunner

from yogit.yogit import cli
from yogit.yogit.errors import ExitCode
from yogit.api.client import GITHUB_API_URL_V4
from yogit.tests.mocks.mock_settings import mock_settings


def _add_graphql_response(json):
    responses.add(responses.POST, GITHUB_API_URL_V4, json=json, status=200)


@pytest.fixture
def runner():
    return CliRunner()


@pytest.mark.usefixtures("mock_settings")
@responses.activate
def test_empty_pr_list(runner):
    _add_graphql_response({"data": {"viewer": {"pullRequests": {"edges": []}}}})
    result = runner.invoke(cli.main, ["pr", "list"])
    assert result.exit_code == ExitCode.NO_ERROR.value
    assert result.output == ("CREATED    URL    TITLE\n" "---------  -----  -------\n")


@pytest.mark.usefixtures("mock_settings")
@responses.activate
@patch("yogit.utils.dateutils._utcnow", return_value=datetime(2019, 7, 12, 1, 15, 59, 666))
def test_pr_list_ok(mock_utc_now, runner):
    _add_graphql_response(
        {
            "data": {
                "viewer": {
                    "pullRequests": {
                        "edges": [
                            {"node": {"createdAt": "2019-05-27T18:00:01Z", "url": "https://xyz", "title": "title9"}},
                            {"node": {"createdAt": "2019-05-28T08:00:01Z", "url": "https://abc", "title": "title8"}},
                            {"node": {"createdAt": "2019-07-02T19:00:59Z", "url": "https://xyz", "title": "title7"}},
                            {"node": {"createdAt": "2019-07-02T18:00:30Z", "url": "https://abc", "title": "title6"}},
                            {"node": {"createdAt": "2019-07-11T19:00:30Z", "url": "https://xyz", "title": "title5"}},
                            {"node": {"createdAt": "2019-07-11T19:00:30Z", "url": "https://efg", "title": "title4"}},
                            {"node": {"createdAt": "2019-07-11T17:00:30Z", "url": "https://abc", "title": "title3"}},
                            {"node": {"createdAt": "2019-07-12T13:00:01Z", "url": "https://xyz", "title": "title2"}},
                            {"node": {"createdAt": "2019-07-12T13:00:01Z", "url": "https://abc", "title": "title1"}},
                        ]
                    }
                }
            }
        }
    )
    result = runner.invoke(cli.main, ["pr", "list"])
    assert result.exit_code == ExitCode.NO_ERROR.value
    assert result.output == (
        "CREATED      URL          TITLE\n"
        "-----------  -----------  -------\n"
        "Today        https://abc  title1\n"
        "Today        https://xyz  title2\n"
        "Yesterday    https://abc  title3\n"
        "Yesterday    https://efg  title4\n"
        "Yesterday    https://xyz  title5\n"
        "10 days ago  https://abc  title6\n"
        "10 days ago  https://xyz  title7\n"
        "45 days ago  https://abc  title8\n"
        "46 days ago  https://xyz  title9\n"
    )
