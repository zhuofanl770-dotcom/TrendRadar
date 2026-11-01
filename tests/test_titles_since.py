from types import SimpleNamespace
from unittest import TestCase

from trendradar.core.data import detect_titles_since_from_storage, select_rss_urls_since


def _news(title, first_time, url="https://example.com/a"):
    return SimpleNamespace(
        title=title,
        first_time=first_time,
        crawl_time=first_time,
        ranks=[1],
        rank=1,
        url=url,
        mobile_url="",
    )


def _storage(items):
    return SimpleNamespace(get_today_all_data=lambda: SimpleNamespace(items=items))


class DetectTitlesSinceTest(TestCase):
    def test_keeps_only_titles_first_seen_after_last_push(self):
        storage = _storage({
            "weibo": [
                _news("上午已推送", "08-05"),
                _news("推送同一分钟抓到", "08-12"),
                _news("下午抓到但已下榜", "13-30"),
                _news("晚间新抓到", "20-05"),
            ],
        })

        titles = detect_titles_since_from_storage(storage, "08-12")

        self.assertEqual(set(titles["weibo"]), {"下午抓到但已下榜", "晚间新抓到"})

    def test_returns_whole_day_when_no_push_yet_today(self):
        storage = _storage({"weibo": [_news("早上", "06-40"), _news("下午", "17-30")]})

        titles = detect_titles_since_from_storage(storage, None)

        self.assertEqual(set(titles["weibo"]), {"早上", "下午"})

    def test_same_title_with_new_url_is_not_new(self):
        storage = _storage({
            "weibo": [
                _news("换了链接的旧闻", "08-05", url="https://example.com/old"),
                _news("换了链接的旧闻", "15-00", url="https://example.com/new"),
            ],
        })

        self.assertEqual(detect_titles_since_from_storage(storage, "08-12"), {})

    def test_skips_platforms_no_longer_monitored(self):
        storage = _storage({"weibo": [_news("a", "15-00")], "tieba": [_news("b", "15-00")]})

        titles = detect_titles_since_from_storage(storage, "08-12", ["weibo"])

        self.assertEqual(set(titles), {"weibo"})

    def test_no_data_returns_empty(self):
        storage = SimpleNamespace(get_today_all_data=lambda: None)

        self.assertEqual(detect_titles_since_from_storage(storage, None), {})


class SelectRssUrlsSinceTest(TestCase):
    def setUp(self):
        self.rss_data = SimpleNamespace(items={
            "hacker-news": [
                SimpleNamespace(url="https://a", first_time="08:05", crawl_time="08:05"),
                SimpleNamespace(url="https://b", first_time="13:30", crawl_time="13:30"),
                SimpleNamespace(url="", first_time="13:30", crawl_time="13:30"),
            ],
        })

    def test_normalizes_rss_time_format_before_comparing(self):
        self.assertEqual(select_rss_urls_since(self.rss_data, "08-12"), {"https://b"})

    def test_returns_all_urls_when_no_push_yet_today(self):
        self.assertEqual(select_rss_urls_since(self.rss_data, None), {"https://a", "https://b"})
