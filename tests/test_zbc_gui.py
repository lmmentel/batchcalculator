import unittest
import numpy as np
from batchcalc import zbc

class TestReactantClassOnEtOH(unittest.TestCase):

    def setUp(self):
        self.r = cal.Reactant(id=15,
                          name="ethanol",
                          formula="C2H5OH",
                          molwt=46.0688,
                          short_name="EtOH",
                          typ="reactant",
                          concentration=0.998,
                          cas="64-17-5",
                          mass=50.0,
                          physical_form="liquid",
                          density=0.7893,
                          electrolyte="weak acid",
                          pk=15.9,
                          smiles="CCO")

    def tearDown(self):
        pass

    def test_moles(self):
        self.assertAlmostEqual(self.r.moles, 1.0853332, places=6)

    def test_volume(self):
        self.assertAlmostEqual(self.r.volume, 63.3472697, places=6)

    def test_formula_to_tex(self):
        self.assertEqual(self.r.formula_to_tex(), ur"C$_{2}$H$_{5}$OH")

    def test_formula_to_html(self):
        self.assertEqual(self.r.formula_to_html(), ur"C<sub>2</sub>H<sub>5</sub>OH")

    def test_listctrl_label(self):
        self.assertEqual(self.r.listctrl_label(), "EtOH")

    def test_label(self):
        self.assertEqual(self.r.label(), u"EtOH (99.8\%)")


if __name__ == "__main__":
    unittest.main()
