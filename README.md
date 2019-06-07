# Teammood-Client
Python client for the Teammood API.

Teammood (https://app.teammood.com) is a online app that polls teams daily to see how they are doing and to catch problems before they become big. Geared towards agile dev teams it's a easy way to see how everyone is operating.

**I AM NOT PERSONALLY AFFILIATED WITH TEAMMOOD**

I use this for my teams and i needed a python client for reporting. Hence this project. Any help you want to contribute is appreciated.

## Dependencies
- requests

## Usage

1. Import the module
```python
from teammood.teammood import Teammood, INTERVALS, TAG_COMBINATOR
```

2. Create the client
```python
teammood_client = Teammood(team_id="TEAM_ID",
                           api_key="API_KEY")
```
### Moods With Participation
Query moods with associated participation
```python
super_mood = teammood_client.get_moods_with_participation(
            start_datetime=datetime.datetime(year=2019, month=5, day=1),
            end_datetime=datetime.datetime(year=2019, month=5, day=27)
        )
```

### Moods

Query moods by a date range
```python
moods = teammood_client.get_all_moods_for_dates(start_datetime=datetime.datetime(year=2019, month=5, day=1),
                                                end_datetime=datetime.datetime(year=2019, month=5, day=31)
                                                )
```

Query moods for last X days
```python
moods = teammood_client.get_all_moods_since(since=7)
```

Response
```python
Team
    tags: [Tag]
    days: [Day
            moods: [Mood]
          ]
```
### Participation

Query participation by a date range
```python
participation = teammood_client.get_participation_for_dates(start_datetime=datetime.datetime(year=2019, month=5, day=1),
                                                            end_datetime=datetime.datetime(year=2019, month=5, day=27)
                                                            )
```

Response
```python
Participation
    rates: [Rate]
```