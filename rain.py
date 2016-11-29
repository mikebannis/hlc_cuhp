"""
Imports, parse and exports raingages in the updaed project format. Cumulative time and rainfall are in columns O & P.
"""
from time import mktime, strptime
from datetime import datetime
from calendar import month_name


class RainEvent(object):
    def __init__(self, lines):
        """
        :param lines: list of lines of rain event info in the project format w/o the header
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
            self.id = fields[0]+'-'+fields[1]
            temp = strptime(fields[0]+'-'+fields[1], '%m/%d/%Y-%H:%M:%S')
            self.storm_start = datetime.fromtimestamp(mktime(temp))

            # burn through lines, check total rain calc
            temp_rain = 0.0
            for line in lines:
                fields = line.strip().split(',')
                temp_rain += float(fields[3])

            # Last line is end of storm, convert to seconds
            self.length = float(fields[14]) * 60.0
            self.total_rain = float(fields[15])
            assert abs(self.total_rain-temp_rain) < 0.001

        #print self.id, self.total_rain, self.length, self.storm_start

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

            # value of 0 in line 14 means new storm
            if fields[0] == '':
                # Look out for double blanks
                if lines:
                    temp = RainEvent(lines)
                    storms.append(temp)
                    lines = []
            else:
                lines.append(line.strip())
        temp = RainEvent(lines)
        storms.append(temp)
    return storms


def monthly_rain(storms):
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

        # Check for existence of year in dict
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
    s = 'Year'
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


def monthly_events(storms):
    """
    calculate number of rainfall events by month and year
    :param storms: list of RainEvent objects
    """
    # Tally rainfall events by month and year
    years = {}
    for storm in storms:
        this_month = storm.storm_start.month
        this_year = storm.storm_start.year
        rain = storm.total_rain

        # Check for existence of year in dict
        if this_year in years:
            # Check for existance of month in dict
            if this_month in years[this_year]:
                # already exists, append
                years[this_year][this_month] += 1
            else:
                # doesn't exist, create
                years[this_year][this_month] = 1
        else:
            # doesn't exist, create year and month
            years[this_year] = {}
            years[this_year][this_month] = 1

    # Months to print out records for (jan = 1)
    start_month = 4
    end_month = 10

    # print header
    s = 'Year'
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
                s += ',0'
        print s


def main():
    filename = 'csv/more_rain2.csv'
    storms = import_storms(filename)
    print 'number of events=', len(storms)

    monthly_rain(storms)
    monthly_events(storms)

if __name__ == '__main__':
    main()
