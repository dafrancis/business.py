"""Business Calendar."""
import datetime
from dateutil import rrule
from dateutil import parser
import os

import yaml


def parse_date(date):
    """Parse date string."""
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

    def __init__(self, working_days=None, holidays=None):
        self._working_days = None
        self._holidays = None

        self.working_days = working_days
        self.holidays = holidays

    @classmethod
    def load(cls, rules, custom_path=None):
        """
        Load a calendar with predefined rules.

        e.g.
            bacs_calendar = Calendar.load('bacs')
        """
        file_name = '{}.yml'.format(rules)
        if custom_path is None:
            rules_path = os.path.join('business', 'data', file_name)
        else:
            rules_path = os.path.join(custom_path, file_name)

        if not os.path.isfile(rules_path):
            raise Exception('Rules Does Not Exist')

        with open(rules_path, 'r') as rules_file:
            rules_yaml = yaml.load(rules_file)

        return Calendar(working_days=rules_yaml.get('working_daysk'),
                        holidays=rules_yaml.get('holidays'))

    @property
    def working_days(self):
        """Return working days."""
        return self._working_days

    @working_days.setter
    def working_days(self, value):
        """
        Set the working days.

        This normalises the inputs and checks if it's on the list of valid days.
        """
        days = value or self.DEFAULT_WORKING_DAYS
        normalised_days = []
        for day in days:
            normalised_day = day.lower()[:3]
            if normalised_day not in self.DAY_NAMES:
                raise Exception("Invalid Day {}".format(day))
            normalised_days.append(normalised_day)
        self._working_days = normalised_days

    @property
    def holidays(self):
        """Return holidays."""
        return self._holidays

    @holidays.setter
    def holidays(self, value):
        """
        Set the holidays.

        This parses the date from a list of date strings.
        """
        dates = value or []
        holidays = []
        for date in dates:
            holiday = parse_date(date)
            holidays.append(holiday)
        self._holidays = holidays

    def is_business_day(self, day):
        """Return True if business day."""
        parsed_day = parse_date(day)
        if parsed_day.strftime('%a').lower() not in self.working_days:
            return False
        if parsed_day in self.holidays:
            return False
        return True

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
        """Get next business day."""
        day += self.DAY_INTERVAL
        return self.roll_forward(day)

    def previous_business_day(self, day):
        """Get previous business day."""
        day -= self.DAY_INTERVAL
        return self.roll_backward(day)

    def add_business_days(self, day, days):
        """Add business days."""
        day = self.roll_forward(day)
        for _ in range(days):
            day = self.next_business_day(day)
        return day

    def subtract_business_days(self, day, days):
        """Subtract business days."""
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
