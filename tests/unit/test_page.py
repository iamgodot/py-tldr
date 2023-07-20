import json
from time import sleep

import pytest

from py_tldr.core import make_page_finder
from py_tldr.page import PageCache


class TestPageCache:
    def test_cache(self, tmp_path):
        cache = PageCache(1 / 3600 / 10, tmp_path, "")
        name, platform, content = "foo", "common", "bar"
        cache.set(name, platform, content)
        assert cache.get(name, platform) == content
        sleep(0.1)
        assert cache.get(name, platform) == ""

    def test_index(self, tmp_path, mocker):
        cache = PageCache(1, tmp_path, "")
        assert cache.check_index() is False
        mocker.patch(
            "py_tldr.page.download_data",
            return_value=json.dumps(
                {
                    "commands": [
                        {
                            "name": "tldr",
                            "platform": ["linux"],
                            "language": ["en"],
                            "targets": [{"os": "linux", "language": "en"}],
                        }
                    ]
                }
            ),
        )
        cache.update_index()
        with open(cache.index_file) as f:
            assert json.load(f)["tldr"] == {"linux": ["en"]}
        assert cache.check_index() is True


class TestPageFinder:
    page_finder = make_page_finder()
    command = "tldr"
    platform = "linux"
    languages = ["zh", "en"]
    patch_path_cache_get = "py_tldr.page.PageCache.get"
    patch_path_cache_set = "py_tldr.page.PageCache.set"
    patch_path_finder_query = "py_tldr.page.PageFinder._query"
    patch_path_finder_search = "py_tldr.page.PageFinder.search"
    patch_path_finder_get_index = "py_tldr.page.PageFinder.get_index"

    def test_by_cache(self, mocker):
        patched_search = mocker.patch(
            self.patch_path_finder_search,
            return_value=(self.command, self.platform, self.languages[0]),
        )
        patched_get = mocker.patch(self.patch_path_cache_get, return_value="foobar")
        patched_query = mocker.patch(self.patch_path_finder_query)

        assert (
            self.page_finder.find(
                self.command, platform=self.platform, languages=self.languages
            )
            == "foobar"
        )
        patched_search.assert_called_once_with(
            self.command, self.platform, self.languages
        )
        patched_get.assert_called_once_with(
            self.command, self.platform, language=self.languages[0]
        )
        patched_query.assert_not_called()

    def test_by_query(self, mocker):
        patched_search = mocker.patch(
            self.patch_path_finder_search,
            return_value=(self.command, self.platform, self.languages[0]),
        )
        patched_get = mocker.patch(self.patch_path_cache_get, return_value="")
        patched_query = mocker.patch(
            self.patch_path_finder_query, return_value="foobar"
        )
        patched_set = mocker.patch(self.patch_path_cache_set)

        assert (
            self.page_finder.find(
                self.command, platform=self.platform, languages=self.languages
            )
            == "foobar"
        )
        patched_search.assert_called_once_with(
            self.command, self.platform, self.languages
        )
        patched_get.assert_called_once_with(
            self.command, self.platform, language=self.languages[0]
        )
        patched_query.assert_called_once_with(
            self.page_finder._make_page_url(
                self.command, self.platform, self.languages[0]
            )
        )
        patched_set.assert_called_once_with(
            self.command, self.platform, "foobar", language=self.languages[0]
        )

    @pytest.mark.parametrize(
        "index, search_params, search_result",
        (
            (
                {},
                ("tldr", "linux", ["en"]),
                ("", "", ""),
            ),
            (
                {"tldr": {"linux": ["en"], "common": ["en"]}},
                ("tldr", "linux", ["en"]),
                ("tldr", "linux", "en"),
            ),
            (
                {"tldr": {"linux": ["en"], "common": ["en"]}},
                ("tldr", "osx", ["en"]),
                ("tldr", "common", "en"),
            ),
            (
                {
                    "tldr": {
                        "linux": ["en"],
                    }
                },
                ("tldr", "osx", ["en"]),
                ("tldr", "linux", "en"),
            ),
            (
                {
                    "tldr": {
                        "linux": ["en"],
                    }
                },
                ("tldr", "linux", ["en"]),
                ("tldr", "linux", "en"),
            ),
            (
                {
                    "tldr": {
                        "linux": ["en"],
                    }
                },
                ("tldr", "linux", ["zh", "en"]),
                ("tldr", "linux", "en"),
            ),
            (
                {
                    "tldr": {
                        "linux": ["en"],
                    }
                },
                ("tldr", "linux", ["zh"]),
                ("tldr", "", ""),
            ),
        ),
    )
    def test_search(self, mocker, index, search_params, search_result):
        mocker.patch(self.patch_path_finder_get_index, return_value=index)
        assert self.page_finder.search(*search_params) == search_result
