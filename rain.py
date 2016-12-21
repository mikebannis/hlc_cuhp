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
        self.values = [(0,0)]  # list of cumulative (time, rainfall) data points as tuples (minutes, inches)

        if len(lines) == 1:
            # One line storm
            fields = lines[0].strip().split(',')
            self.id = fields[0]+'-'+fields[1]
            temp_time = strptime(self.id, '%m/%d/%Y-%H:%M:%S')
            self.storm_start = datetime.fromtimestamp(mktime(temp_time))
            self.total_rain = float(fields[3])
            self.length = 5*60  # One line storm, default to 5 minutes
            self.values.append((fields[14], fields[15]))
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
                self.values.append((fields[14], fields[15]))

            # Last line is end of storm, convert to seconds
            self.length = float(fields[14]) * 60.0
            self.total_rain = float(fields[15])
            assert abs(self.total_rain-temp_rain) < 0.001

        #print self.id, self.total_rain, self.length, self.storm_start
        #print self.id, self.values

    @staticmethod
    def header():
        return 'storm_id,month,year,total_rain,time'

    def __str__(self):
        s = self.id + ','
        s += str(self.storm_start.month) + ','
        s += str(self.storm_start.year) + ','
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

def monthly_storm_length(storms):
    """
    calculate total length of storms in a month by month and year
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
                years[this_year][this_month] += storm.length
            else:
                # doesn't exist, create
                years[this_year][this_month] = storm.length
        else:
            # doesn't exist, create year and month
            years[this_year] = {}
            years[this_year][this_month] = storm.length

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

def plot_hyeto_by_year(storms, start=1998, end=2015):
    """
    Plot all storms by year and save a figure for every year
    """
    def load_2_year(filename):
        """
        Imports design storm from csv and returns x coorids in lists and y coords in list
        """
        first_lap = True
        x = []; y = []
        
        with open(filename, 'rt') as infile:
            for line in infile:
                # Strip two line header
                if first_lap:
                    line = next(infile)
                    line = next(infile)
                    first_lap = False

                fields = line.strip().split(',')
                x.append(float(fields[0]))
                y.append(float(fields[2]))
        return x, y

    from matplotlib import pyplot, axes

    design_x, design_y = load_2_year('csv/2-Year Design Storm.csv')

    max_rain = max_rain_rainfall(storms)
    for year in range(start, end+1):
        print 'processing', year
        events = 0
        total_rain = 0
        for storm in storms:
            if storm.storm_start.year == year:
                #print storm.values
                events += 1
                total_rain += storm.total_rain
                x = []
                y = []
                for value in storm.values:
                    x.append(value[0])
                    y.append(value[1])
                pyplot.plot(x,y)
        # add design storm
        pyplot.plot(design_x, design_y, color='red', linewidth=2)
        xy = (design_x[-1], design_y[-1]+0.05)
        pyplot.annotate('2-Yr Design\nStorm', xy=xy)

        # set axis
        x1,x2,y1,y2 = pyplot.axis()
        pyplot.axis((x1,x2,0,max_rain))
        #import pdb; pdb.set_trace()
        
#        title = str(year) + ', # of Storms = ' + str(events) + ', Cumulative Rainfall (in) = ' + \ 
#                str(total_rain)
        title = '{}, # of Storms = {}, Cumulative Rainfall (in) = {}'.format(year, events, total_rain)
        
        pyplot.title(title)
        pyplot.xlabel('Time since start of storm (minutes)')
        pyplot.ylabel('Cumulative rainfall (inches)')


        pyplot.savefig(str(year)+'.pdf')
        pyplot.clf()  # Clear figure
        print events, 'storms in ', year, 'total rain', total_rain

def plot_hyeto_by_month(storms):
    """
    Plot all storms by month
    """
    from matplotlib import pyplot
    i = 0
    for month in range(4, 10+1):
        for storm in storms:
            if storm.storm_start.month == month:
                #print storm.values
                i += 1
                x = []
                y = []
                for value in storm.values:
                    x.append(value[0])
                    y.append(value[1])
                pyplot.plot(x,y)
        pyplot.title(month_name[month])
        pyplot.show()
        print i, 'storms in ', month_name[month]

def max_rain_rainfall(storms):
    """
    Returns single createst stormfall total from storms
    """
    max_rain = 0
    for storm in storms:
        if storm.total_rain > max_rain:
            max_rain = storm.total_rain
    assert max_rain != 0
    return max_rain

def main():
    filename = 'csv/more_rain2.csv'
    print 'importing storms'
    storms = import_storms(filename)
    print 'number of events=', len(storms)

    #monthly_rain(storms)
    #monthly_events(storms)
    max_rain = max_rain_rainfall(storms)
    print max_rain
    monthly_storm_length(storms)

    biggest = storms[0]
    for storm in storms:
        if storm.total_rain > biggest.total_rain:
            biggest = storm

    print biggest

    
    plot_hyeto_by_year(storms)

if __name__ == '__main__':
    main()
