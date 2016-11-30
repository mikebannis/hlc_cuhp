"""
Calculate runoff volumes for multiple rain events for multiple subcatchments. Considers imperviousnesss, area,
depression storage and infiltration using hortons equation.
"""
from rain import import_storms, RainEvent
from subcatch import import_params, Subcatchment
from stats import Stats
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

def adjust_volume(results, adjust_file):
    """
    Reduce runoff volumes in results based on adjust_file. This is based on subcatchment names
    :param results: list of RunOff objects
    :param adjust_file: file name of csv file with adjustments in "sc_name,adjust_factor" format
    """
    # import adjustment factors
    factors = {}
    with open(adjust_file) as infile:
        for line in infile:
            fields = line.strip().split(',')
            factors[fields[0]] = float(fields[1])
    # Adjust
    for result in results:
        result.runoff = result.runoff * factors[result.sc.name]


def main():
    rainfile = 'csv/more_rain2.csv'
    paramfile = 'csv/hlc_sc_combined.csv'
    adjust_file = 'csv/adjust.csv'

    subcatches = import_params(paramfile)
    storms = import_storms(rainfile)

    results = []
    for sc in subcatches:
        # print 'processing subcatch', sc.name
        for storm in storms:
            runoff = RunOff(storm, sc)
            results.append(runoff)

    adjust_volume(results, adjust_file)
    
    # print all output data
    if True:
        print Subcatchment.header() + ','  + RainEvent.header() + ',' + RunOff.header()
        for result in results:
            print result
    
    # print monthly average runoff for each subcatchment
    if not True:
        stats = Stats(results)
        #stats.print_vals()
        stats.print_average_runoff()



if __name__ == '__main__':
    main()
