import datetime

from dateutil import parser

s = '2005-12-12'
date_object = parser.parse(s).date()
date_object -= datetime.timedelta(days=1)
print(date_object)