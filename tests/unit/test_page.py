from time import sleep

from py_tldr.core import make_page_finder
from py_tldr.page import PageCache


class TestCache:
    def test_validation(self, tmp_path):
        cache = PageCache(1 / 3600 / 10, tmp_path, "")
        name, platform, content = "foo", "common", "bar"
        cache.set(name, platform, content)
        assert cache.get(name, platform) == content
        sleep(0.1)
        assert cache.get(name, platform) == ""

    def test_update(self):
        pass


class TestPageFinder:
    page_finder = make_page_finder()

    def test_by_cache(self, mocker):
        patched_get = mocker.patch("py_tldr.page.PageCache.get", return_value="foobar")
        patched_query = mocker.patch("py_tldr.page.PageFinder._query")

        assert self.page_finder.find("tldr") == "foobar"
        patched_get.assert_called_once()
        patched_query.assert_not_called()

    def test_by_finder(self, mocker):
        patched_get = mocker.patch("py_tldr.page.PageCache.get", return_value="")
        patched_query = mocker.patch(
            "py_tldr.page.PageFinder._query", return_value="foobar"
        )
        patched_set = mocker.patch("py_tldr.page.PageCache.set")

        assert self.page_finder.find("tldr") == "foobar"
        patched_get.assert_called_once()
        patched_query.assert_called_once()
        patched_set.assert_called_once()

    def test_no_result(self, mocker):
        patched_get = mocker.patch("py_tldr.page.PageCache.get", return_value="")
        patched_query = mocker.patch("py_tldr.page.PageFinder._query", return_value="")

        assert self.page_finder.find("tldr") == ""
        patched_get.assert_called_once()
        patched_query.assert_called_once()
