import pytz
from datetime import datetime, timedelta
from config import TIMEZONE


DATES = [
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec'
]


def get_local_date_now():
    """Get local date now from a UTC date

    Returns:
        datetime: Datetime object
    """
    utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    local = utc.astimezone(TIMEZONE)
    return local


def get_utc_date_now():
    date_string = str(datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S"))
    naive = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    local_dt = TIMEZONE.localize(naive, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt


def get_utc_today_start_date(date=None):
    if date:
        local = date
    else:
        local = get_local_date_now()

    local_start_date = local.replace(hour=0, minute=0, second=0, microsecond=0)
    utc_start_date = local_start_date.astimezone(pytz.utc)
    return utc_start_date


def get_utc_today_end_date(date=None):
    if date:
        local = date
    else:
        local = get_local_date_now()

    local_end_date = local.replace(hour=23, minute=59, second=59)
    utc_end_date = local_end_date.astimezone(pytz.utc)
    return utc_end_date


def get_last_n_days(days=7):
    now = get_local_date_now()
    results = []
    
    for x in range(days):
        day = now - timedelta(days=x)
        results.append(day)
    results.reverse()
    return results


def convert_date_input_to_utc(date_str, date_type=None, date_format="%Y-%m-%d"):
    if date_str == '':
        return None
    naive = datetime.strptime(date_str, date_format)
    local_dt = TIMEZONE.localize(naive, is_dst=None)

    if date_type == "date_from":
        local_dt = local_dt.replace(hour=0, minute=0, second=0)
    elif date_type == "date_to":
        local_dt = local_dt.replace(hour=23, minute=59, second=59)

    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt


def format_utc_to_local(date, date_format="%B %d, %Y", with_time=False):
    if date is None:
        return ''
    
    if date == '':
        return ''
    
    if with_time:
        date_format = "%B %d, %Y %I:%M %p"
    
    if type(date == datetime):
        local_dt = date.replace(tzinfo=pytz.utc).astimezone(TIMEZONE).strftime(date_format)
    elif type(date == str):
        naive = datetime.strptime(date, "%Y-%m-%d")
        local_dt = TIMEZONE.localize(naive, is_dst=None).strftime(date_format)
    else:
        local_dt = ''
    return local_dt
    
    
def convert_utc_to_local(date):
    if date is None:
        return None
    
    if type(date == datetime):
        local_dt = date.replace(tzinfo=pytz.utc).astimezone(TIMEZONE)
        return local_dt
    elif type(date == str):
        naive = datetime.strptime(date, "%Y-%m-%d")
        local_dt = TIMEZONE.localize(naive, is_dst=None)
        return local_dt
    return None
    

def format_date(date: datetime, date_format="%B %d, %Y"):
    if date is None:
        return ''
    return date.strftime(date_format)
