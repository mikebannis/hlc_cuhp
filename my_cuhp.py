"""
Calculate runoff volumes for multiple rain events for multiple subcatchments. Considers imperviousnesss, area,
depression storage and infiltration using hortons equation.
"""
from rain import import_storms, RainEvent
from subcatch import import_params, Subcatchment
import math


class RunOff(object):
    def __init__(self, storm, sc):
        """
        Calculates runoff for a given storm and subcatchment (sc) using impervious area, depression storage, and hortons infiltration
        :param storm: RainEvent object
        :param sc: Subcatchment object
        """
        self.storm = storm
        self.sc = sc
        
        # Adjust subcatch params
        self.area_acre = sc.area * 640.0
        self.imp_area = self.area_acre * sc.imperv/100.0
        self.perv_area = self.area_acre - self.imp_area

        # Calculate runoff volumes
        self.imp_vol = self.imp_area * (storm.total_rain - sc.depress_stor_imperv) / 12.0  # ac-ft
        self.infil = self.infiltration(sc.horton_init, sc.horton_decay, sc.horton_final, storm.length)  # inches
        self.per_vol = self.perv_area * (storm.total_rain - sc.depress_stor_perv - self.infil) / 12.0  # ac-ft

        # Make sure nothing is below zero
        if self.imp_vol < 0.0:
            self.imp_vol = 0.0
        if self.per_vol < 0.0:
            self.per_vol = 0.0

        # Total runoff
        self.runoff = self.imp_vol + self.per_vol  # ac-ft
        #print storm.id, '\t', sc.name, '\t', storm.total_rain, '\t', round(imp_vol,1),'\t', round(per_vol,1),'\t', round(runoff,1),'\t',  i

    @staticmethod
    def infiltration(f0, k, fc, t):
        """
        Calculate total water infiltration using Horntons eq
        :param f0: initial infiltration rate (in/hr)
        :param k: decay rate (1/sec):
        :param fc: final infiltration rate (in/hr):
        :param t: storm time (secs)
        :return: total infilitration for storm (in)
        """
        t_hr = t/(60.0*60.0)  # convert to hrs
        k_hr = k*(60.0*60.0)  # convert 1/sec to 1/hr
        infil = fc*t_hr + ((f0-fc)/k_hr)*(1-math.e**(-k_hr*t_hr))
        return infil
    
    @staticmethod
    def header():
        """ header for __str__() in csv """
        return 'area_acre,imp_area,perv_area,imp_vol,infil,per_vol,runoff'

    def __str__(self):
        s = str(self.sc) + ','
        s += str(self.storm) + ','
        s += str(self.area_acre) + ','
        s += str(self.imp_area) + ','
        s += str(self.perv_area) + ','
        s += str(self.imp_vol) + ','
        s += str(self.infil) + ','
        s += str(self.per_vol) + ','
        s += str(self.runoff) 
        return s


class SubcatchResult(object):
    def __init__(self):
        self.months = {}  # keys are months (4,5,etc), values are MonthValues objects

class MonthValues(object):
    def __init__(self):
        self.years = {}  # keys are years (1998, 2006, etc), values are YearValues objects
        self.average = None  # average 

class YearValues(object):
    def __init__(self):
        self.values = []  # list of runoff volumes (float)
        self.average = None  # average of values (float)


def average_monthly_runoff(results):
    """
    prints a csv list of average monthly rainfall by subcatchment
    :param results: list of RunOff objects
    """
    months = range(4,10+1)
    subcatch_names = []
    for result in results:
        if not result.sc.name in subcatch_names:
            subcatch_names.append(result.sc.name)
    years = []
    for result in results:
        # print result.storm.storm_start.month 
        if not result.storm.storm_start.year in years:
            years.append(result.storm.storm_start.year)
    print subcatch_names
    print years

    sc_results = {}  # keys are subcatch names, values are SubcatchResult obecjts
    for sc in subcatch_names:
        scr = SubcatchResult()
        for month in months:
            mv = MonthValues()
            for year in years:
                yv = YearValues() 
                for result in results



    
def not_used(results):
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

def main():
    rainfile = 'csv/more_rain2.csv'
    paramfile = 'csv/hlc_sc_combined.csv'

    subcatches = import_params(paramfile)
    storms = import_storms(rainfile)

    results = []
    for sc in subcatches:
        # print 'processing subcatch', sc.name
        for storm in storms:
            runoff = RunOff(storm, sc)
            results.append(runoff)
    
    if not True:
        print Subcatchment.header() + ','  + RainEvent.header() + ',' + RunOff.header()
        for result in results:
            print result
    
    average_monthly_runoff(results)


if __name__ == '__main__':
    main()
