import unittest
from app import *

class testApp(unittest.TestCase):

    def test_parse_meeting_times(self):
        i = {
            'MeetsOn1': 'M',
            'StartTime1': '12:00:20',
            'EndTime1': '18:00:00'
        }
        expected = [(
            datetime.datetime(
                year=1970,
                month=1,
                day=5,
                hour=12,
                minute=0,
                second=20,),
            datetime.datetime(
                year=1970,
                month=1,
                day=5,
                hour=18,
                minute=0,
                second=0,)
        )]

        result = parse_meeting_times(i)
        self.assertEqual(expected, result)

        i = {
            'MeetsOn1': 'MS',
            'StartTime1': '12:00:20',
            'EndTime1': '18:00:00'
        }
        expected = [
            (
                datetime.datetime(
                    year=1970, month=1, day=5,
                    hour=12, minute=0, second=20,
                ),
                datetime.datetime(
                    year=1970, month=1, day=5,
                    hour=18, minute=0, second=0,
                )
            ),
            (
                datetime.datetime(
                    year=1970, month=1, day=10,
                    hour=12, minute=0, second=20,
                ),
                datetime.datetime(
                    year=1970, month=1, day=10,
                    hour=18, minute=0, second=0,
                )
            )
        ]

        result = parse_meeting_times(i)
        self.assertEqual(expected, result)

        i = {
            'MeetsOn1': 'M',
            'StartTime1': '12:00:20',
            'EndTime1': '18:00:00',
            'MeetsOn2': 'R',
            'StartTime2': '00:10:00',
            'EndTime2': '14:30:00'
        }
        expected = [
            (
                datetime.datetime(
                    year=1970, month=1, day=5,
                    hour=12, minute=0, second=20,
                ),
                datetime.datetime(
                    year=1970, month=1, day=5,
                    hour=18, minute=0, second=0,
                )
            ),
            (
                datetime.datetime(
                    year=1970, month=1, day=8,
                    hour=0, minute=10, second=0,
                ),
                datetime.datetime(
                    year=1970, month=1, day=8,
                    hour=14, minute=30, second=0,
                )
            )
        ]

        result = parse_meeting_times(*i)
        self.assertEqual(expected, result)
