"""Offline tests for the opt-in 1xBet market adapter."""
import os
import sys
import unittest

import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xbet_scrape import (  # noqa: E402
    BlockedResponse,
    ProxyPool,
    extract_game,
    normalize_game,
    response_body,
)


class XBetScrapeTests(unittest.TestCase):
    def test_proxy_pool_uses_explicit_authorized_proxies(self):
        pool = ProxyPool(["http://8.8.8.8:8080", "http://1.1.1.1:8080"])
        self.assertEqual(pool.urls(), [
            "http://8.8.8.8:8080", "http://1.1.1.1:8080"
        ])
        self.assertEqual(pool.next(), "http://8.8.8.8:8080")
        self.assertEqual(pool.next(), "http://1.1.1.1:8080")
        self.assertEqual(pool.next(), "http://8.8.8.8:8080")

    def test_proxy_pool_rejects_private_and_malformed_urls(self):
        with self.assertRaises(ValueError):
            ProxyPool(["http://127.0.0.1:8080"])
        with self.assertRaises(ValueError):
            ProxyPool(["ftp://198.51.100.10:8080"])
        with self.assertRaises(ValueError):
            ProxyPool(["http://user:pass@198.51.100.10:8080"])

    def test_block_page_is_not_a_success(self):
        request = httpx.Request("GET", "https://sa.1xbet.com/en/line/football/1-match")
        response = httpx.Response(200, text="Cloudflare challenge", request=request)
        with self.assertRaises(BlockedResponse):
            response_body(response)

    def test_normalize_full_time_markets_and_retain_all_outcomes(self):
        game = {
            "id": 77,
            "permanentId": 123,
            "firstOpponentName": "Home FC",
            "secondOpponentName": "Away FC",
            "startUnixTimestamp": 2000000000,
            "hasScores": False,
            "isSubGame": False,
            "gamePeriodId": 0,
            "baseSubGames": [],
            "unparsedEventGroups": [
                {"groupId": 1, "events": [[{"type": 1, "cf": 2.0}],
                                             [{"type": 2, "cf": 3.0}],
                                             [{"type": 3, "cf": 4.0}]]},
                {"groupId": 8, "events": [[{"type": 4, "cf": 1.4}],
                                             [{"type": 5, "cf": 1.5}],
                                             [{"type": 6, "cf": 2.2}]]},
                {"groupId": 17, "events": [[{"type": 9, "cf": 1.8,
                                               "parameter": 2.5}],
                                              [{"type": 10, "cf": 2.0,
                                               "parameter": 2.5}]]},
                {"groupId": 19, "events": [[{"type": 180, "cf": 1.7}],
                                              [{"type": 181, "cf": 2.1}]]},
            ],
        }
        rows = normalize_game(game, "game-123")
        supported = {(r["market"], r["selection"], r["line"]): r["odds"]
                     for r in rows if r["market"] != "raw"}
        self.assertEqual(supported[("1X2", "1", "")], 2.0)
        self.assertEqual(supported[("DC", "1X", "")], 1.4)
        self.assertEqual(supported[("OU", "Over", "2.5")], 1.8)
        self.assertEqual(supported[("BTS", "Yes", "")], 1.7)
        self.assertEqual(sum(r["market"] == "raw" for r in rows), 0)

    def test_extract_game_validates_event_identity(self):
        state = {"pinia": {"game": {"currentGameId": "77",
                                      "gamesById": {"77": {"permanentId": 123}}}}}
        self.assertEqual(extract_game(state, 123)["permanentId"], 123)
        with self.assertRaises(ValueError):
            extract_game(state, 999)


if __name__ == "__main__":
    unittest.main()
