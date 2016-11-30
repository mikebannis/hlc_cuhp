"""
Calculates and prints out statistics related from RunOff objects
"""
import calendar

class Stats(object):
    def __init__(self, results, start_month=4, end_month=10):

        self.results = results  # list of RunOff objects
        self.subcatch_names = []  # subcatchment names in self.results
        self.months = range(start_month, end_month+1)  # list of months to work with (4,5...)
        self.years = []  # years with data in results
        self.subcatches = {}  # dict of SubcatchResult objects

        # determine subcatch_names and years
        for result in results:
            if not result.sc.name in self.subcatch_names:
                self.subcatch_names.append(result.sc.name)
            if not result.storm.storm_start.year in self.years:
                self.years.append(result.storm.storm_start.year)

        if not True:
            print self.subcatch_names
            print self.years

        # create structure for storing all this crap
        for sc in self.subcatch_names:
            scr = SubcatchResult()
            self.subcatches[sc] = scr
            for month in self.months:
                mv = MonthValues()
                self.subcatches[sc].months[month] = mv
                for year in self.years:
                    yv = YearValues() 
                    self.subcatches[sc].months[month].years[year] = yv

        # Populate sc_results
        for result in results:
            sc = result.sc.name
            month = result.storm.storm_start.month
            year = result.storm.storm_start.year
            runoff = result.runoff
            self.subcatches[sc].months[month].years[year].values.append(runoff)

        # Average runoffs by subcatch and month
        for sc in self.subcatches:
            for m in self.subcatches[sc].months:
                self.subcatches[sc].months[m].calc_average()


    def print_average_runoff(self):
        """ print all average total run off per month (ac-ft) by subcatchment in self in csv format with header"""
        # header
        s = 'Subcatchment'
        for m in self.months:
            s += ',' + calendar.month_name[m]
        print s

        # values
        for sc in self.subcatches:
            s = sc
            for m in self.subcatches[sc].months:
                s += ',' + str(self.subcatches[sc].months[m].average)
            print s

    def print_vals(self):
        """ print all values in self """
        for sc in self.subcatches:
            for m in self.subcatches[sc].months:
                for y in self.subcatches[sc].months[m].years:
                    print sc, m, y, self.subcatches[sc].months[m].years[y].values


# All classes below here are "helper" classes
class SubcatchResult(object):
    def __init__(self):
        self.months = {}  # keys are months (4,5,etc), values are MonthValues objects

    def __str__(self):
        return str(self.months)

class MonthValues(object):
    def __init__(self):
        self.years = {}  # keys are years (1998, 2006, etc), values are YearValues objects
        self.average = None  # average total runoff for month

    def calc_average(self):
        """ total run off by year, then caclulate average """
        total = 0
        for year in self.years:
            total += self.years[year].calc_total_runoff()

        self.average = total/float(len(self.years))

class YearValues(object):
    def __init__(self):
        self.values = []  # list of runoff volumes (float)
        self.total_runoff = None  # total runoff for year/subcatchment/month

    def calc_total_runoff(self):
        self.total_runoff = sum(self.values)
        return self.total_runoff

