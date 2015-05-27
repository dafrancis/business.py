import datetime
import os

from mock import Mock
from nose.tools import raises

from business import calendar


def test_load_valid_calendar():
    calendar.yaml = Mock(load=Mock(return_value={}))
    calendar.Calendar.load('weekdays')
    assert calendar.yaml.load.called


def test_load_valid_calendar_from_custom_directory():
    dir_name = os.path.join(os.path.dirname(__file__), 'fixtures', 'calendars')
    calendar.yaml = Mock(load=Mock(return_value={}))
    calendar.Calendar.load('ecb', custom_path=dir_name)
    assert calendar.yaml.load.called


@raises(Exception)
def test_invalid_calendar_throws_exception():
    calendar.Calendar.load('does-not-exist')


def test_given_valid_working_days():
    test_calendar = calendar.Calendar()

    test_calendar.working_days = ['mon', 'fri']
    assert test_calendar.working_days == ['mon', 'fri']


def test_given_valid_working_days_unnormalised():
    test_calendar = calendar.Calendar()

    test_calendar.working_days = ['Monday', 'Friday']
    assert test_calendar.working_days == ['mon', 'fri']


@raises(Exception)
def test_given_invalid_working_days():
    test_calendar = calendar.Calendar()

    test_calendar.working_days = ['Notaday']


def test_given_none_working_days():
    test_calendar = calendar.Calendar()

    test_calendar.working_days = None
    assert test_calendar.working_days == test_calendar.DEFAULT_WORKING_DAYS


def test_holidays_valid_business_days():
    test_calendar = calendar.Calendar()

    test_calendar.holidays = ["1st Jan, 2013"]
    assert len(test_calendar.holidays) > 0
    for holiday in test_calendar.holidays:
        assert isinstance(holiday, datetime.date)


def test_holidays_none():
    test_calendar = calendar.Calendar()

    test_calendar.holidays = None
    assert test_calendar.holidays == []


def test_is_business_day():
    test_calendar = calendar.Calendar()
    test_calendar.holidays = ["9am, Tuesday 1st Jan, 2013"]

    # Business Day
    assert test_calendar.is_business_day("9am, Wednesday 2nd Jan, 2013")

    # Non Business Day
    assert not test_calendar.is_business_day("9am, Saturday 5th Jan, 2013")

    # Holiday
    assert not test_calendar.is_business_day("9am, Tuesday 1st Jan, 2013")


def check_date_change(function, date, days_diff):
    assert function(date) == date + datetime.timedelta(days=days_diff)


def test_roll_forward():
    test_calendar = calendar.Calendar()
    test_calendar.holidays = ["Tuesday 1st Jan, 2013"]

    # Business Day
    date = calendar.parse_date("Wednesday 2nd Jan, 2013")
    yield check_date_change, test_calendar.roll_forward, date, 0

    # Non Business Day
    date = calendar.parse_date("Tuesday 1st Jan, 2013")
    yield check_date_change, test_calendar.roll_forward, date, 1

    date = calendar.parse_date("Saturday 5th Jan, 2013")
    yield check_date_change, test_calendar.roll_forward, date, 2


def test_roll_backward():
    test_calendar = calendar.Calendar()
    test_calendar.holidays = ["Tuesday 1st Jan, 2013"]

    # Business Day
    date = calendar.parse_date("Wednesday 2nd Jan, 2013")
    yield check_date_change, test_calendar.roll_backward, date, 0

    # Non Business Day
    date = calendar.parse_date("Tuesday 1st Jan, 2013")
    yield check_date_change, test_calendar.roll_backward, date, -1

    date = calendar.parse_date("Sunday 6th Jan, 2013")
    yield check_date_change, test_calendar.roll_backward, date, -2


def test_next_business_day():
    test_calendar = calendar.Calendar()
    test_calendar.holidays = ["Tuesday 1st Jan, 2013"]

    # Business Day
    date = calendar.parse_date("Wednesday 2nd Jan, 2013")
    yield check_date_change, test_calendar.next_business_day, date, 1

    # Non Business Day
    date = calendar.parse_date("Tuesday 1st Jan, 2013")
    yield check_date_change, test_calendar.next_business_day, date, 1

    date = calendar.parse_date("Saturday 5th Jan, 2013")
    yield check_date_change, test_calendar.next_business_day, date, 2


def test_previous_business_day():
    test_calendar = calendar.Calendar()
    test_calendar.holidays = ["Tuesday 1st Jan, 2013"]

    # Business Day
    date = calendar.parse_date("Thursday 3nd Jan, 2013")
    yield check_date_change, test_calendar.previous_business_day, date, -1

    # Non Business Day
    date = calendar.parse_date("Tuesday 1st Jan, 2013")
    yield check_date_change, test_calendar.previous_business_day, date, -1

    date = calendar.parse_date("Sunday 6th Jan, 2013")
    yield check_date_change, test_calendar.previous_business_day, date, -2


def check_delta(function, date, days_diff):
    delta = 2

    assert function(date, delta) == date + datetime.timedelta(days=days_diff)


def test_add_business_days():
    test_calendar = calendar.Calendar()
    test_calendar.holidays = ["Tuesday 1st Jan, 2013"]

    delta = 2

    # Business Day
    date = calendar.parse_date("Wednesday 2nd Jan, 2013")
    yield check_delta, test_calendar.add_business_days, date, delta

    date = calendar.parse_date("Friday 4th Jan, 2013")
    yield check_delta, test_calendar.add_business_days, date, delta + 2

    date = calendar.parse_date("Monday 31st Dec, 2012")
    yield check_delta, test_calendar.add_business_days, date, delta + 1

    # Non Business Day
    date = calendar.parse_date("Tuesday 1st Jan, 2013")
    yield check_delta, test_calendar.add_business_days, date, delta + 1


def test_subtract_business_days():
    test_calendar = calendar.Calendar()
    test_calendar.holidays = ["Thursday 3rd Jan, 2013"]

    delta = 2

    # Business Day
    date = calendar.parse_date("Wednesday 2nd Jan, 2013")
    yield check_delta, test_calendar.subtract_business_days, date, -delta

    date = calendar.parse_date("Monday 31st Dec, 2012")
    yield check_delta, test_calendar.subtract_business_days, date, -(delta + 2)

    date = calendar.parse_date("Friday 4th Jan, 2013")
    yield check_delta, test_calendar.subtract_business_days, date, -(delta + 1)

    # Non Business Day
    date = calendar.parse_date("Thursday 3rd Jan, 2013")
    yield check_delta, test_calendar.subtract_business_days, date, -(delta + 1)


def check_business_days_between(test_calendar, date1, date2, dates_in_between):
    date1 = calendar.parse_date(date1)
    date2 = calendar.parse_date(date2)

    business_days = test_calendar.business_days_between(date1, date2)

    assert business_days == dates_in_between


def test_business_days_between():
    test_calendar = calendar.Calendar()
    test_calendar.holidays = [
        "Thu 12/6/2014",
        "Wed 18/6/2014",
        "Fri 20/6/2014",
        "Sun 22/6/2014"
    ]

    dates = [
        # Starting on a business day and..

        # .. Ending on a business day
        ("Mon 2/6/2014", "Thu 5/6/2014", 3),
        ("Mon 2/6/2014", "Mon 9/6/2014", 5),
        ("Mon 9/6/2014", "Fri 13/6/2014", 3),
        ("Mon 2/6/2014", "Fri 13/6/2014", 8),
        # .. Ending on a weekend day
        ("Mon 2/6/2014", "Sun 8/6/2014", 5),
        ("Mon 2/6/2014", "Sat 14/6/2014", 9),
        # .. Ending on a holiday
        ("Mon 9/6/2014", "Thu 12/6/2014", 3),
        ("Mon 2/6/2014", "Thu 12/6/2014", 8),

        # Starting on a weekend and ..

        # .. Ending on a business day
        ("Sat 7/6/2014", "Mon 9/6/2014", 0),
        ("Sat 7/6/2014", "Fri 13/6/2014", 3),
        # .. Ending on a weekend day
        ("Sat 7/6/2014", "Sun 8/6/2014", 0),
        ("Sat 7/6/2014", "Sun 14/6/2014", 4),
        # .. Ending on a holiday
        ("Sat 7/6/2014", "Thu 12/6/2014", 3),

        # Starting on a holiday and ..

        # .. Ending on a business day
        ("Thu 12/6/2014", "Fri 13/6/2014", 0),
        ("Thu 12/6/2014", "Thu 19/6/2014", 3),
        # .. Ending on a weekend day
        ("Thu 12/6/2014", "Sun 15/6/2014", 1),
        # .. Ending on a holiday
        ("Wed 18/6/2014", "Fri 20/6/2014", 1),
        ("Thu 12/6/2014", "Wed 18/6/2014", 3),

        # Calendar has a holiday on a non-working (weekend) day
        ("Thu 19/6/2014", "Tue 24/6/2014", 2),
        ("Mon 16/6/2014", "Tue 24/6/2014", 4),
    ]

    for date1, date2, dates_in_between in dates:
        yield check_business_days_between, test_calendar, date1, date2, dates_in_between
