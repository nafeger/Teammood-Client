import requests
import datetime
import logging

from requests.auth import HTTPBasicAuth
from requests.utils import requote_uri
from urllib.parse import urlencode, quote_plus
from enum import Enum


class MOOD_TYPE(Enum):

    BAD = "BAD"
    HARD = "HARD"
    AVERAGE = "AVERAGE"
    GOOD = "GOOD"
    EXCELLENT = "EXCELLENT"

    @classmethod
    def get_mood(cls, name: str):
        if name.upper() == "BAD":
            return cls.BAD

        if name.upper() == "HARD":
            return cls.HARD

        if name.upper() == "AVERAGE":
            return cls.AVERAGE

        if name.upper() == "GOOD":
            return cls.GOOD

        if name.upper() == "EXCELLENT":
            return cls.EXCELLENT

    @classmethod
    def get_numerical_value(cls, mood) -> float:
        if mood == cls.BAD:
            return 1.00
        if mood == cls.HARD:
            return 2.00
        if mood == cls.AVERAGE:
            return 3.00
        if mood == cls.GOOD:
            return 4.00
        if mood == cls.EXCELLENT:
            return 5.00

    @classmethod
    def get_mood_by_numerical_value(cls, value: float):
        if value < 2.00:
            return cls.BAD
        elif value < 3.00:
            return cls.HARD
        elif value < 4.00:
            return cls.AVERAGE
        elif value < 5.00:
            return cls.GOOD
        elif value < 6.00:
            return cls.EXCELLENT


class TAG_COMBINATOR(Enum):
    UNION = "union"
    INTERSECTION = "intersection"


class INTERVALS(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Tag(object):
    """
    Tag Class

    Attributes:
        name (str): Name of the Tag
        switched_on (bool): Is the Tag turned on
        is_active (bool):  Is the Tag active
    """

    name = None
    switched_on = None
    is_active = None

    def __init__(self, name: str, switched_on: bool, is_active: bool):
        self.name = name
        self.switched_on = switched_on
        self.is_active = is_active


class Mood(object):
    """
    Mood Class

    Attributes:
        mood (MOOD_TYPE) = Tee mood
        mood_id (str) = Unique id for mood response
        comment (str) = User comment on mood
    """

    mood = None
    mood_id = None
    comment = None

    def __init__(self, mood: MOOD_TYPE, mood_id: str):
        self.mood = mood
        self.mood_id = mood_id

    def add_comment(self, comment: str) -> None:
        self.comment = comment


class Rate(object):
    """
    Rate Class

    Attributes:
        date (datetime): Date for the Rate
        percentage (int): The % of people who responded
        distinct_participants (int): Amount of distinct responders
    """

    date = None
    percentage = None
    distinct_participants = None

    def __init__(self,
                 date: datetime,
                 percentage: int,
                 distinct_participants: int):

        self.date = date
        self.percentage = percentage
        self.distinct_participants = distinct_participants


class Day(object):
    """
    Day Class

    Attributes:
        date (datetime): Datetime for the day
        today (bool): Is it today
        moods (list): List of Mood Classes
        average_mood (MOOD_TYPE): Average Mood for the day
        participation (Rate): The participation for the day
    """

    date = datetime
    today = bool
    moods = list()
    average_mood = MOOD_TYPE
    average_mood_raw = float
    comments = list()
    participation = Rate

    def __init__(self, date: datetime, today: bool):
        self.date = date
        self.today = today
        self.moods = []
        self.comments = []
        self.average_mood_raw = 0
        self.average_mood = None
        self.participation = None

    def __set_avg_mood(self) -> None:
        mood_float = 0.00

        for mood in self.moods:
            mood_float += MOOD_TYPE.get_numerical_value(mood=mood.mood)

        self.average_mood_raw = float(mood_float/float(len(self.moods)))
        self.average_mood = MOOD_TYPE.get_mood_by_numerical_value(
            value=self.average_mood_raw
        )

    def __add_comment(self, comment: str):
        self.comments.append(comment)

    def add_mood(self, mood: Mood) -> None:
        self.moods.append(mood)

        if mood.comment:
            self.__add_comment(comment=mood.comment)

        self.__set_avg_mood()

    def add_participation(self, rate: Rate) -> None:
        self.participation = rate



class Team(object):
    """
    Team Class

    Attributes:
        name (str): Mame of the Team
        tags (list): List of Tag Classes
        days (list): List of Day Classes
    """

    name = str
    tags = list()
    days = list()

    def __init__(self, team_name: str):
        self.name = team_name
        self.tags = []
        self.days = []

    def add_tag(self, tag: Tag) -> None:
        self.tags.append(tag)

    def add_day(self, day: Day) -> None:
        self.days.append(day)


class Participation(object):
    """
    Participation Class

    Attributes:
        rates (list): list of Rate classes
    """
    rates = list()

    def __init__(self):
        self.rates = []

    def add_rate(self, rate: Rate) -> None:
        """Add a rate

        Args:
            rate (Rate): The Rate to add
        """
        self.rates.append(rate)

    def get_rate_by_date(self, date: datetime) -> Rate:
        """Search for a participation rate by date

        Args:
            date (datetime): Datetime to search for

        Returns:
            Rate
        """
        for rate in self.rates:
            if rate.date.date() == date.date():
                return rate


class Teammood(object):
    """
    Teammood Client Class

    Attributes:
        BASE_URL (str): The base url for all API calls
        TEAM_ID (str): The Teammood Team Id
        API_KEY (str): The Teammood API Key
    """

    BASE_URL = "https://app.teammood.com/api/v2"
    TEAM_ID = None
    API_KEY = None

    def __init__(self,
                 team_id: str = None,
                 api_key: str = None,
                 base_url: str = None,
                 logging_level = logging.DEBUG
                 ) -> None:
        """Class Init

        Args:
            team_id (str): Teamood Team Id
            api_key (str): Teamood API Key
            base_url (str): (optional) Overide the base url with new one
            logging_level (logging.level): Level you want to log to
        """

        if base_url:
            self.BASE_URL = base_url

        if team_id:
            self.TEAM_ID = team_id

        if api_key:
            self.API_KEY = api_key

        logging.basicConfig(format='%(levelname)s:%(message)s',
                            level=logging_level)

    @staticmethod
    def __parameters_to_querystring(params: dict) -> str:
        """Formats the Query Parameters

        Args:
            params (dict): A dict of items to be query parameters

        Returns:
            A formatted str of query parameters
        """
        parameter_string = urlencode(params, quote_via=quote_plus)

        if len(parameter_string) > 0:
            return "&" + parameter_string
        else:
            return ""

    @staticmethod
    def __date_formatter(date: datetime) -> str:
        """Unified date format for Teammood

        Args:
            date (datetime): The inpot datetime

        Returns:
            Properly formatted str

        """
        return date.strftime('%d-%m-%Y')

    def __call_api(self,
                   route: str,
                   params: dict
                   ) -> dict:
        """API Caller

        Management of the call to the Teammood API

        Args:
            route (str): route to call
            params (dict): additional query parameters to send

        Returns:
            JSON formattes HTTPResponse
        """

        if self.TEAM_ID and self.API_KEY:
            url = requote_uri("{base}{route}{parameters}".format(
                base=self.BASE_URL,
                route=route,
                parameters=self.__parameters_to_querystring(params)
                )
            )
            logging.debug(url)

            r = requests.get(url=url, auth=HTTPBasicAuth(self.TEAM_ID, self.API_KEY))

            if r.status_code == 200:
                return r.json()
            else:
                raise Exception("Code: {code}\nError: error".format(code=r.status_code,
                                                                    error=r.text))
        else:
            raise Exception("TEAM_ID and/or API_KEY not found. Please Authenticate")

    def __mood_response_to_classes(self, mood_response: dict) -> Team:
        """Mood Response to Class

        Map the Mood API response to the associated classes

        Args:
            mood_response (dict): Response dict from the Teammood API call

        Returns:
            Team Class
        """

        team = Team(team_name=mood_response['teamName'])

        for tag_data in mood_response['tags']:
            tag = Tag(name=tag_data['name'],
                      switched_on=tag_data['switchedOn'],
                      is_active=tag_data['isActive']
                      )

            team.add_tag(tag=tag)

        for day_data in mood_response['days']:
            moods_date = datetime.datetime.fromtimestamp(int(day_data['nativeDate'])/1000)

            day = Day(date=moods_date,
                      today=day_data['today'])

            for value in day_data['values']:

                mood = Mood(
                    mood=MOOD_TYPE.get_mood(
                        name=value['mood']
                    ),
                    mood_id=value['moodId']
                )

                if 'comment' in value:
                    mood.add_comment(comment=value['comment']['body'])

                day.add_mood(mood=mood)

            team.add_day(day=day)

        return team

    def __participation_response_to_classes(self, participation_response: dict) -> Participation:

        """Participation Response to Class

        Map the Participation API response to the associated classes

        Args:
            participation_response (dict): Response dict from the Teammood API call

        Returns:
            Participation Class
        """
        participation = Participation()

        for participation_rate in participation_response['participation_rates']:

            rate = Rate(date=datetime.datetime.strptime(participation_rate['date'], "%d-%m-%Y"),
                        percentage=participation_rate['rate_percentage'],
                        distinct_participants=participation_rate['distinct_participants']
                        )

            participation.add_rate(rate)

        return participation


    def set_authentication(self,
                           team_id: str,
                           api_key: str
                           ) -> None:
        """Set Authentication

        Add the required keys to the client

        Args:
            team_id (str): Teammood Team Id
            api_key (str): Teammood API key
        """

        self.TEAM_ID = team_id
        self.API_KEY = api_key

    def get_all_moods_since(self,
                            since: int,
                            tags: [str] = None,
                            tagscombinator: TAG_COMBINATOR = None
                            ) -> Team:
        """Moods Since

        Get the Moods for the last X number of days

        Args:
            since (int): Amout of days back to get results for
            tags [str]: List of tags your querying
            tagscombinator (TAG_COMBINATOR): If multiple tags are defined, this parameter describes how filtering is applied.

        Returns:

        """

        route = "/team/moods?since={since}".format(
            since=since
        )

        params = {}

        if tags:
            params['tags'] = ','.join(tags)

        if tagscombinator:
            params['tagscombinator'] = tagscombinator.value

        response = self.__call_api(route=route,
                                   params=params)
        logging.debug(response)

        return self.__mood_response_to_classes(mood_response=response)

    def get_all_moods_for_dates(self,
                                start_datetime: datetime,
                                end_datetime: datetime,
                                tags: [str] = None,
                                tagscombinator: TAG_COMBINATOR = None
                                ) -> Team:
        """Moods for a date range

        Get the Moods for a certain date range

        Args:
            start_datetime (datetime): Start Date/Time for query
            end_datetime (datetime): End Date/Time for query
            tags [str]: List of tags your querying
            tagscombinator (TAG_COMBINATOR): If multiple tags are defined, this parameter describes how filtering is applied.

        Returns:
            Team class
        """

        route = "/team/moods?start={start}&end={end}".format(
            start=self.__date_formatter(start_datetime),
            end=self.__date_formatter(end_datetime)
        )

        params = {}

        if tags:
            params['tags'] = ','.join(tags)

        if tagscombinator:
            params['tagscombinator'] = tagscombinator.value

        response = self.__call_api(route=route,
                                   params=params)
        logging.debug(response)

        return self.__mood_response_to_classes(mood_response=response)

    def get_participation_for_dates(self,
                                    start_datetime: datetime,
                                    end_datetime: datetime,
                                    tags: [str] = None,
                                    interval: INTERVALS = None,
                                    tagscombinator: TAG_COMBINATOR = None
                                    ) -> Participation:
        """Participation for date range

        Get the participation data for the date range defined

        Args:
            start_datetime (datetime): Start Date/Time for query
            end_datetime (datetime): End Date/Time for query
            tags [str]: List of tags your querying
            interval (INTERVALS): The interval for aggregating the participation
            tagscombinator (TAG_COMBINATOR): If multiple tags are defined, this parameter describes how filtering is
                applied.

        Returns:
            Participation Class
        """

        route = "/team/participation?start={start}&end={end}".format(
            start=self.__date_formatter(start_datetime),
            end=self.__date_formatter(end_datetime)
        )

        params = {}

        if interval:
            params['interval'] = interval.value

        if tags:
            params['tags'] = ','.join(tags)

        if tagscombinator:
            params['tagscombinator'] = tagscombinator.value

        response = self.__call_api(route=route,
                                   params=params)
        logging.debug(response)

        return self.__participation_response_to_classes(participation_response=response)

    def get_moods_with_participation(self,
                                     start_datetime: datetime,
                                     end_datetime: datetime,
                                     tags: [str] = None,
                                     tagscombinator: TAG_COMBINATOR = None
                                     ) -> Team:
        """Moods and Participation together

        Gets the moods for the defined time and adds the participation for each day.

        Args:
            start_datetime (datetime): Start Date/Time for query
            end_datetime (datetime): End Date/Time for query
            tags [str]: List of tags your querying
            tagscombinator (TAG_COMBINATOR): If multiple tags are defined, this parameter describes how filtering is applied.

        Returns:
            Team class with Participation for each day in Team.days

        """

        team = self.get_all_moods_for_dates(start_datetime=start_datetime,
                                            end_datetime=end_datetime,
                                            tags=tags,
                                            tagscombinator=tagscombinator)

        participation = self.get_participation_for_dates(start_datetime=start_datetime,
                                                         end_datetime=end_datetime,
                                                         tags=tags,
                                                         interval=INTERVALS.DAILY,
                                                         tagscombinator=tagscombinator)

        for day in team.days:
            synced_rate = participation.get_rate_by_date(date=day.date)

            if synced_rate:
                day.add_participation(rate=synced_rate)

        return team

