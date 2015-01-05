import unittest
import numpy as np
import os
from batchcalc import calculator as cal
from batchcalc.controller import add_chemical_record

class TestChemical(unittest.TestCase):

    def setUp(self):
        self.bc = cal.BatchCalculator()
        self.bc.new_dbsession(os.path.join(os.getcwd(), 'test.db'))

    def tearDown(self):
        #os.remove('test.db')
        pass

    def test_add_chemical(self):
        reac
        naoh = {'name':'ethanol', 'formula':'C2H5OH', 'molwt':46.0688,
                            'short_name':'EtOH', 'concentration':0.998, 'cas':'64-17-5',
                            'density':0.789, 'pk':15.9, 'kind':'reactant'}
        add_chemical_record(self.bc.session, naoh)





if __name__ == "__main__":
    unittest.main()
