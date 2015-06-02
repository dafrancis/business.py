import datetime
from dateutil import rrule
from dateutil import parser
import os
import yaml


def parse_date(date):
    if isinstance(date, str):
        return parser.parse(date, dayfirst=True).date()
    if isinstance(date, datetime.datetime):
        return date.date()
    return date


class Calendar(object):

    """Calendar object to handle date rules."""

    DAY_INTERVAL = datetime.timedelta(days=1)
    DAY_NAMES = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    DEFAULT_WORKING_DAYS = ['mon', 'tue', 'wed', 'thu', 'fri']
    DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')

    def __init__(self, working_days=None, holidays=None):
        self._working_days = None
        self._holidays = None

        self.working_days = working_days
        self.holidays = holidays

    @classmethod
    def load(cls, rules, data_path=DEFAULT_DATA_PATH):
        """
        Load a calendar with predefined rules.

        e.g.
            bacs_calendar = Calendar.load('bacs')
        """
        file_name = '{0}.yml'.format(rules)
        rules_path = os.path.join(data_path, file_name)
        assert os.path.isfile(rules_path), 'Rules Does Not Exist'

        with open(rules_path, 'r') as rules_file:
            rules_yaml = yaml.load(rules_file)

        return Calendar(working_days=rules_yaml.get('working_days'),
                        holidays=rules_yaml.get('holidays'))

    @property
    def working_days(self):
        return self._working_days

    @working_days.setter
    def working_days(self, value):
        days = value or self.DEFAULT_WORKING_DAYS
        normalised_days = []
        for day in days:
            normalised_day = day.lower()[:3]
            day_is_valid = normalised_day in self.DAY_NAMES
            assert day_is_valid, "Invalid Day: {0}".format(day)
            normalised_days.append(normalised_day)
        self._working_days = normalised_days

    @property
    def holidays(self):
        return self._holidays

    @holidays.setter
    def holidays(self, value):
        """
        Set the holidays.

        This parses the date from a list of date strings.
        """
        dates = value or []
        self._holidays = [parse_date(date) for date in dates]

    def is_working_day(self, day):
        return day.strftime('%a').lower() in self.working_days

    def is_not_holiday(self, day):
        return day not in self.holidays

    def is_business_day(self, day):
        date = parse_date(day)
        return self.is_working_day(date) and self.is_not_holiday(date)

    def roll_forward(self, day):
        """Roll forward to the next business day if not a business day."""
        valid_date = self.is_business_day(day)
        while not valid_date:
            day += self.DAY_INTERVAL
            valid_date = self.is_business_day(day)
        return day

    def roll_backward(self, day):
        """Roll backward to the last business day if not a business day."""
        valid_date = self.is_business_day(day)
        while not valid_date:
            day -= self.DAY_INTERVAL
            valid_date = self.is_business_day(day)
        return day

    def next_business_day(self, day):
        day += self.DAY_INTERVAL
        return self.roll_forward(day)

    def previous_business_day(self, day):
        day -= self.DAY_INTERVAL
        return self.roll_backward(day)

    def add_business_days(self, day, days):
        day = self.roll_forward(day)
        for _ in range(days):
            day = self.next_business_day(day)
        return day

    def subtract_business_days(self, day, days):
        day = self.roll_backward(day)
        for _ in range(days):
            day = self.previous_business_day(day)
        return day

    def business_days_range(self, date1, date2):
        """Get range of business dates between two dates."""
        end_date = date2 - self.DAY_INTERVAL
        dates = rrule.rrule(rrule.DAILY, dtstart=date1, until=end_date)

        return [date.date() for date in dates if self.is_business_day(date)]

    def business_days_between(self, date1, date2):
        """Get count of business dates between two dates."""
        date_range = self.business_days_range(date1, date2)
        return len(date_range)
