"""Data-free checks for enrichment scraper parsing and safe rate-limit handling."""
import os
import sys
import unittest
from unittest.mock import patch

import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enrichment_scraper import (Fetcher, RateLimited, _fotmob_candidates,
                                _sofascore_candidates, match_candidate)


class EnrichmentScraperTests(unittest.TestCase):
    def test_candidate_parsers_and_team_matching(self):
        fotmob = _fotmob_candidates({"leagues": [{"matches": [{
            "id": 10, "home": {"name": "Man Utd"},
            "away": {"name": "Tottenham Hotspur"},
            "status": {"utcTime": "2026-11-05T20:00:00Z"},
        }]}]})
        sofa = _sofascore_candidates({"events": [{
            "id": 20, "homeTeam": {"name": "Manchester United"},
            "awayTeam": {"name": "Tottenham"}, "startTimestamp": 1793908800,
        }]})
        fixture = {"home": "Manchester United", "away": "Tottenham"}
        self.assertEqual(fotmob[0]["id"], "10")
        self.assertEqual(sofa[0]["id"], "20")
        self.assertEqual(match_candidate(fixture, fotmob)[0]["id"], "10")
        self.assertEqual(match_candidate(fixture, sofa)[0]["id"], "20")

    def test_429_stops_without_proxy_rotation(self):
        fetcher = Fetcher(delay=0, tries=1, max_retry_after=0)
        request = httpx.Request("GET", "https://example.test")
        response = httpx.Response(429, headers={"Retry-After": "300"}, request=request)
        with patch.object(fetcher.client, "get", return_value=response):
            with self.assertRaisesRegex(RateLimited, "Retry-After=300s"):
                fetcher.get_json("https://example.test")
        fetcher.close()


if __name__ == "__main__":
    unittest.main()
