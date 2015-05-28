# business.py

![travis build](https://travis-ci.org/dafrancis/business.py.svg?branch=master)

Date calculations based on business calendars.

This is basically a python version of a [ruby gem](github.com/gocardless/business).

## Documentation

To get business, simply:

```bash
$ python setup.py install
```

### Getting started

Get started with business by creating an instance of the calendar class,
passing in a hash that specifies with days of the week are considered working
days, and which days are holidays.

```python
calendar = business.Calendar(
  working_days=['mon', 'tue', 'wed', 'thu', 'fri'],
  holidays=["01/01/2014", "03/01/2014"]
)
```

A few calendar configs are bundled with the gem (see lib/business/data for
details). Load them by calling the `load` class method on `Calendar`.

```python
calendar = business.Calendar.load("weekdays")
```

### Checking for business days

To check whether a given date is a business day (falls on one of the specified
working days, and is not a holiday), use the `is_business_day` method on
`Calendar`.

```python
>>> calendar.is_business_day("Monday, 9 June 2014")
True
>>> calendar.is_business_day("Sunday, 8 June 2014")
False
```

### Custom calendars

To use a calendar you've written yourself, you need to add the directory it's
stored in as an additional calendar load parameter:

```python
calendar = business.Calendar.load("your_calendar",
                                  data_path="path/to/your/calendar/directory")
```

### Business day arithmetic

The `add_business_days` and `subtract_business_days` are used to perform
business day arithemtic on dates.

```python
>>> date = datetime.strptime("Thursday, 12 June 2014", "%A, %d %B %Y")
>>> calendar.add_business_days(date, 4).strftime("%A, %d %B %Y")
'Wednesday, 18 June 2014'
>>> calendar.subtract_business_days(date, 4).strftime("%A, %d %B %Y")
'Friday, 06 June 2014'
```

The `roll_forward` and `roll_backward` methods snap a date to a nearby business
day. If provided with a business day, they will return that date. Otherwise,
they will advance (forward for `roll_forward` and backward for `roll_backward`)
until a business day is found.

```python
>>> date = datetime.strptime("Saturday, 14 June 2014", "%A, %d %B %Y")
>>> calendar.roll_forward(date).strftime("%A, %d %B %Y")
'Monday, 16 June 2014'
>>> calendar.roll_backward(date).strftime("%A, %d %B %Y")
'Friday, 13 June 2014'
```

To count the number of business days between two dates, pass the dates to
`business_days_between`. This method counts from start of the first date to
start of the second date. So, assuming no holidays, there would be two business
days between a Monday and a Wednesday.

```python
>>> date = datetime.strptime("Saturday, 14 June 2014", "%A, %d %B %Y")
>>> calendar.business_days_between(date, date + timedelta(days=7))
5
```

## But there's already a library that does this

In ruby, sure. I'm doing this for python because I'm a monster. Also some
people use Django I suppose.
