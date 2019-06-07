import os
import datetime
import unittest

from teammood.teammood import Teammood, INTERVALS, TAG_COMBINATOR

class Test_Functionality(unittest.TestCase):

    def test_01_auth(self):
        teammood_client = Teammood(team_id=os.getenv("TEAM_ID"),
                                   api_key=os.getenv("API_KEY")
                                   )
        assert teammood_client.TEAM_ID and teammood_client.API_KEY

    def test_02_moods_since(self):
        teammood_client = Teammood(team_id=os.getenv("TEAM_ID"),
                                   api_key=os.getenv("API_KEY")
                                   )

        moods = teammood_client.get_all_moods_since(
            since=7
        )

        assert len(moods.days) > 0

    def test_02a_moods_since(self):
        teammood_client = Teammood(team_id=os.getenv("TEAM_ID"),
                                   api_key=os.getenv("API_KEY")
                                   )

        moods = teammood_client.get_all_moods_since(
            since=7,
            tags=[''],
            tagscombinator=TAG_COMBINATOR.INTERSECTION
        )

        assert len(moods.days) > 0

    def test_03_moods_by_date(self):
        teammood_client = Teammood(team_id=os.getenv("TEAM_ID"),
                                   api_key=os.getenv("API_KEY")
                                   )

        moods = teammood_client.get_all_moods_for_dates(
                    start_datetime=datetime.datetime(year=2019, month=5, day=1),
                    end_datetime=datetime.datetime(year=2019, month=5, day=27)
        )

        assert len(moods.days) > 0

    def test_04_participation_by_date(self):
        teammood_client = Teammood(team_id=os.getenv("TEAM_ID"),
                                   api_key=os.getenv("API_KEY")
                                   )

        participation = teammood_client.get_participation_for_dates(
            start_datetime=datetime.datetime(year=2019, month=5, day=1),
            end_datetime=datetime.datetime(year=2019, month=5, day=27),
            interval=INTERVALS.DAILY
            )

        assert len(participation.rates) > 0

    def test_05_get_unified_mood_with_participation(self):
        teammood_client = Teammood(team_id=os.getenv("TEAM_ID"),
                                   api_key=os.getenv("API_KEY")
                                   )

        super_mood = teammood_client.get_moods_with_participation(
            start_datetime=datetime.datetime(year=2019, month=5, day=1),
            end_datetime=datetime.datetime(year=2019, month=5, day=27)
        )

        assert len(super_mood.days) > 1