from time import sleep

from py_tldr import core
from py_tldr.core import cli


class TestCache:
    def test_validation(self, tmp_path):
        cache = core.PageCache(1 / 3600 / 10, tmp_path, "")
        name, platform, content = "foo", "common", "bar"
        cache.set(name, platform, content)
        assert cache.get(name, platform) == content
        sleep(0.1)
        assert cache.get(name, platform) == ""

    def test_update(self):
        pass


class TestPageGet:
    def test_by_cache(self, mocker, runner):
        patched_get = mocker.patch("py_tldr.core.PageCache.get", return_value="foobar")
        patched_find = mocker.patch("py_tldr.core.PageFinder.find")
        result = runner.invoke(cli, ["tldr"])
        assert result.exit_code == 0
        assert "foobar" in result.output
        patched_get.assert_called_once()
        patched_find.assert_not_called()

    def test_by_finder(self, mocker, runner):
        patched_get = mocker.patch("py_tldr.core.PageCache.get", return_value=None)
        patched_find = mocker.patch(
            "py_tldr.core.PageFinder.find",
            return_value={"name": "foo", "platform": "common", "content": "bar"},
        )
        result = runner.invoke(cli, ["tldr"])
        assert result.exit_code == 0
        assert "bar" in result.output
        patched_get.assert_called_once()
        patched_find.assert_called_once()

    def test_no_result(self, mocker, runner):
        mocker.patch("py_tldr.core.PageCache.get", return_value=None)
        mocker.patch("py_tldr.core.PageFinder.find", return_value={})
        result = runner.invoke(cli, ["foobar"])
        assert result.exit_code == 1
        assert "no available pages" in result.output
