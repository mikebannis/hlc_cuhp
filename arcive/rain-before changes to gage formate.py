"""
Imports, parse and exports raingages in the project format. Note latest data point is at top. Storms are delineated
by blank lines.

    Date	Time	inches	inches	Raw	Alarm	Date	Time	Date/Time	Within 1 day	Winter	Zeros
    9/23/2015	0:54:39	41.1	0.04	1044		42270	0.037951	42270.038	#REF!	1	#REF!
    9/23/2015	0:46:18	41.06	0.04	1043		42270	0.032153	42270.032	0.04	1	#REF!
    9/23/2015	0:40:12	41.02	0.04	1042		42270	0.027917	42270.028	0.04	1	1
    9/23/2015	0:35:21	40.98	0.04	1041		42270	0.024549	42270.025	0.04	1	1
    9/23/2015	0:29:20	40.94	0.04	1040		42270	0.020370	42270.020	0.04	1	1
    9/23/2015	0:23:52	40.91	0.04	1039		42270	0.016574	42270.017	0.04	1	1
    9/23/2015	0:22:22	40.87	0.04	1038		42270	0.015532	42270.016	0.04	1	1
    9/23/2015	0:21:02	40.83	0.04	1037		42270	0.014606	42270.015	0.04	1	#REF!
"""
from time import mktime, strptime
from datetime import datetime
from calendar import month_name


class RainEvent(object):
    def __init__(self, lines):
        """
        :param lines: list of lines of rain event info in the above format w/o the header
        """
        self.id = None  # Storm id in format '9/23/2015-0:21:02', where date time is the start of the storm
        self.total_rain = 0  # total rain during event in inches
        self.length = None  # length of storm in seconds
        self.storm_start = None  # start date/time of storm in datetime.datetime format

        if len(lines) == 1:
            # One line storm
            fields = lines[0].strip().split(',')
            self.id = fields[0]+'-'+fields[1]
            temp_time = strptime(self.id, '%m/%d/%Y-%H:%M:%S')
            self.storm_start = datetime.fromtimestamp(mktime(temp_time))
            self.total_rain = float(fields[3])
            self.length = 5*60  # One line storm, default to 5 minutes
            #print self.id, 'is a one line storm:', self.__dict__
        else:
            # Multi-line storm - First line is end of storm
            fields = lines[0].strip().split(',')
            storm_end = strptime(fields[0]+'-'+fields[1], '%m/%d/%Y-%H:%M:%S')
            storm_end = datetime.fromtimestamp(mktime(storm_end))

            # parse lines - get total rainfall
            for line in lines:
                fields = line.strip().split(',')
                self.total_rain += float(fields[3])

            # Last line is start of storm
            self.id = fields[0]+'-'+fields[1]
            temp_time = strptime(self.id, '%m/%d/%Y-%H:%M:%S')
            self.storm_start = datetime.fromtimestamp(mktime(temp_time))

            self.length = (storm_end - self.storm_start).seconds

    @staticmethod
    def header():
        return 'storm_id,total_rain,time'

    def __str__(self):
        s = self.id + ','
        s += str(self.total_rain) + ','
        s += str(self.length)
        return s


def import_storms(filename):
    """
    Import storm events from filename (see format at top of this file). Header is ignored if present
    :param filename: csv file of storm events
    :return: list of RainEvent() objects
    """
    with open(filename, 'rt') as infile:
        storms = []  # holds all RainEvent instances
        lines = []
        for line in infile:
            fields = line.strip().split(',')

            # Ignore header if it exists
            if fields[0] == 'Date':
                continue

            # Blank line indicates next storm
            if fields[0] == '':
                # Look out for double blanks
                if lines:
                    temp = RainEvent(lines)
                    storms.append(temp)
                    lines = []
            else:
                lines.append(line.strip())
    return storms


def monthly_stats(storms):
    """
    calculate total rainfall by month and year
    :param storms: list of RainEvent objects
    """

    # Tally rainfall by month and year
    years = {}
    for storm in storms:
        this_month = storm.storm_start.month
        this_year = storm.storm_start.year
        rain = storm.total_rain

        # Check for existance of year in dict
        if this_year in years:
            # Check for existance of month in dict
            if this_month in years[this_year]:
                # already exists, append
                years[this_year][this_month] += rain
            else:
                # doesn't exist, create
                years[this_year][this_month] = rain
        else:
            # doesn't exist, create year and month
            years[this_year] = {}
            years[this_year][this_month] = rain

    # Months to print out records for (jan = 1)
    start_month = 4
    end_month = 10

    # print header
    s =  'Year'
    for month in range(start_month, end_month+1):
        s += ',' + month_name[month]
    print s

    # print monthly data
    year_keys = sorted(years.keys())
    for year in year_keys:
        s = str(year)
        for month in range(start_month, end_month+1):
            if month in years[year]:
                s += ',' + str(years[year][month])
            else:
                s += ',0.0'
        print s


def main():
    filename = 'csv/more_rain2.csv'
    storms = import_storms(filename)

    print 'lenght of storms is', len(storms)
    for s in storms:
        print s.length/60/60.0, s

    monthly_stats(storms)

if __name__ == '__main__':
    main()
