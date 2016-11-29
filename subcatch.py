"""
Tools to import subcatchment paramaters saved as a csv
"""


class Subcatchment(object):
    def __init__(self, fields):
        """
        load paramaters from fields
        :param fields: list of subcatch parameters in typical CUHP order
        """
        self.name = fields[0]
        self.area = float(fields[3])  # area in square miles
        self.imperv = float(fields[7])  # imperviousness as a percentange: 50%, 99% (not 0.5 or .99)
        self.depress_stor_perv = float(fields[8])  # pervious depression storage (inches)
        self.depress_stor_imperv = float(fields[9])  # impervious depression storage (inches)
        self.horton_init = float(fields[10]) # initial hortons infiltration (in/hr)
        self.horton_decay = float(fields[11])  # hortons decay coeff (1/secs)
        self.horton_final = float(fields[12])  # final hortons infiltration (in/hr)
        self.fields = fields

    @staticmethod
    def header():
        return 'subcatch_id,area,imperv_percent,depress_stor_perv,depress_stor_imperv,hrtn_init, hrtn_decay, hrtn_final'

    def __str__(self):
        s = str(self.name) + ','
        s += str(self.area) + ','
        s += str(self.imperv) + ','
        s += str(self.depress_stor_perv) + ','
        s += str(self.depress_stor_imperv) + ','
        s += str(self.horton_init) + ','
        s += str(self.horton_decay) + ','
        s += str(self.horton_final) 
        return s


def import_params(param_filename):
    """
    Imports subcatchment parameters from csv in typical CUHP order, no headings
    :param param_filename: filename of csv file
    :return: list of Subcatchment objects
    """
    subcatches = []
    with open(param_filename, 'rt') as infile:
        for line in infile:
            fields = line.strip().split(',')
            new_subcatch = Subcatchment(fields)
            subcatches.append(new_subcatch)
    return subcatches


def main():
    filename = 'csv/hlc_subcatch.csv'
    scs = import_params(filename)
    print len(scs)
    for item in scs:
        print item.name, item.__dict__
        print

if __name__ == '__main__':
    main()


