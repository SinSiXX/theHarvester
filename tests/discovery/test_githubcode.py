from theHarvester.discovery import githubcode
from theHarvester.discovery.githubcode import RetryResult, ErrorResult, SuccessResult
from theHarvester.discovery.constants import MissingKey
from theHarvester.lib.core import Core
from unittest.mock import MagicMock
from requests import Response
import pytest


class TestSearchGithubCode:

    class OkResponse:
        response = Response()
        json = {
            "items": [
                {
                    "text_matches": [
                        {
                            "fragment": "test1"
                        }
                    ]
                },
                {
                    "text_matches": [
                        {
                            "fragment": "test2"
                        }
                    ]
                }
            ]
        }
        response.status_code = 200
        response.json = MagicMock(return_value=json)

    class FailureResponse:
        response = Response()
        response.json = MagicMock(return_value={})
        response.status_code = 401

    class RetryResponse:
        response = Response()
        response.json = MagicMock(return_value={})
        response.status_code = 403

    class MalformedResponse:
        response = Response()
        json = {
            "items": [
                {
                    "fail": True
                },
                {
                    "text_matches": []
                },
                {
                    "text_matches": [
                        {
                            "weird": "result"
                        }
                    ]
                }
            ]
        }
        response.json = MagicMock(return_value=json)
        response.status_code = 200

    @pytest.mark.asyncio
    async def test_missing_key(self):
        with pytest.raises(MissingKey):
            Core.github_key = MagicMock(return_value=None)
            githubcode.SearchGithubCode(word="test", limit=500)

    @pytest.mark.asyncio
    async def test_fragments_from_response(self):
        Core.github_key = MagicMock(return_value="lol")
        test_class_instance = githubcode.SearchGithubCode(word="test", limit=500)
        test_result = await test_class_instance.fragments_from_response(self.OkResponse.response.json())
        print('test_result: ', test_result)
        assert test_result == ["test1", "test2"]

    @pytest.mark.asyncio
    async def test_invalid_fragments_from_response(self):
        Core.github_key = MagicMock(return_value="lol")
        test_class_instance = githubcode.SearchGithubCode(word="test", limit=500)
        test_result = await test_class_instance.fragments_from_response(self.MalformedResponse.response.json())
        assert test_result == []

    @pytest.mark.asyncio
    async def test_handle_response_ok(self):
        Core.github_key = MagicMock(return_value="lol")
        test_class_instance = githubcode.SearchGithubCode(word="test", limit=500)
        test_result = await test_class_instance.handle_response()
        assert isinstance(test_result, SuccessResult)

    @pytest.mark.asyncio
    async def test_handle_response_retry(self):
        Core.github_key = MagicMock(return_value="lol")
        test_class_instance = githubcode.SearchGithubCode(word="test", limit=500)
        test_result = await test_class_instance.handle_response(self.RetryResponse.response.json())
        assert isinstance(test_result, RetryResult)

    @pytest.mark.asyncio
    async def test_handle_response_fail(self):
        Core.github_key = MagicMock(return_value="lol")
        test_class_instance = githubcode.SearchGithubCode(word="test", limit=500)
        test_result = await test_class_instance.handle_response(self.FailureResponse.response.json())
        assert isinstance(test_result, ErrorResult)

    @pytest.mark.asyncio
    async def test_next_page(self):
        Core.github_key = MagicMock(return_value="lol")
        test_class_instance = githubcode.SearchGithubCode(word="test", limit=500)
        test_result = githubcode.SuccessResult(list(), next_page=2, last_page=4)
        assert(2 == await test_class_instance.next_page_or_end(test_result))

    @pytest.mark.asyncio
    async def test_last_page(self):
        Core.github_key = MagicMock(return_value="lol")
        test_class_instance = githubcode.SearchGithubCode(word="test", limit=500)
        test_result = githubcode.SuccessResult(list(), None, None)
        assert(None is await test_class_instance.next_page_or_end(test_result))

    if __name__ == '__main__':
        pytest.main()
