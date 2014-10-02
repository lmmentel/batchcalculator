import unittest
import numpy as np
from batchcalc import calculator as cal

class TestCalculator(unittest.TestCase):

    def setUp(self):
        self.m = cal.BatchCalculator()

    def tearDown(self):
        self.m.reset()

    def test_update_components_add_one(self):
        selections = [(1, 1.0)]
        self.m.update_components("zeolite", selections)
        self.assertEqual(len(self.m.components), 1)

    def test_update_components_change_moles(self):
        selections = [(1, 1.0)]
        self.m.update_components("zeolite", selections)
        selections = [(1, 2.5)]
        self.m.update_components("zeolite", selections)
        self.assertEqual(self.m.components[0].moles, 2.5)

    def test_update_components_add_two(self):
        selections = [(1, 1.0), (2, 2.0)]
        self.m.update_components("zeolite", selections)
        self.assertEqual(len(self.m.components), 2)

    def test_update_components_add_two_remove_one_existing(self):
        selections = [(1, 1.0), (2, 2.0)]
        self.m.update_components("zeolite", selections)
        selections = [(2, 3.0)]
        self.m.update_components("zeolite", selections)
        self.assertEqual(len(self.m.components), 1)
        self.assertEqual(self.m.components[0].id, 2)
        self.assertAlmostEqual(self.m.components[0].moles, 3.0, places=2)

    def test_update_components_add_one_remove_two_existing(self):
        selections = [(2, 1.0), (3, 2.0)]
        self.m.update_components("zeolite", selections)
        selections = [(4, 3.0)]
        self.m.update_components("zeolite", selections)
        self.assertEqual(len(self.m.components), 1)
        self.assertEqual(self.m.components[0].id, 4)
        self.assertAlmostEqual(self.m.components[0].moles, 3.0, places=2)

    def test_update_reactants_add_one(self):
        selections = [(1, 0.1)]
        self.m.update_reactants(selections)
        self.assertEqual(len(self.m.reactants), 1)

    def test_update_reactants_change_concentration(self):
        selections = [(1, 0.1)]
        self.m.update_reactants(selections)
        selections = [(1, 0.25)]
        self.m.update_reactants(selections)
        self.assertEqual(self.m.reactants[0].concentration, 0.25)

    def test_update_reactants_add_two(self):
        selections = [(1, 0.1), (2, 0.2)]
        self.m.update_reactants(selections)
        self.assertEqual(len(self.m.reactants), 2)

    def test_update_reactants_add_two_remove_one(self):
        selections = [(1, 0.1), (2, 0.2)]
        self.m.update_reactants(selections)
        selections = [(3, 0.3)]
        self.m.update_reactants(selections)
        self.assertEqual(len(self.m.reactants), 1)
        self.assertEqual(self.m.reactants[0].id, 3)
        self.assertAlmostEqual(self.m.reactants[0].concentration, 0.3, places=2)

    def test_get_A_matrix_one_zeolite(self):
        self.m.update_components("zeolite", [(1, 1.0)])
        ref = np.array([self.m.components[0].molwt])
        A_vector = self.m.get_A_matrix()
        self.assertTrue(np.allclose(A_vector, ref, rtol=1.0e-4, atol=1.0e-4))

    def test_get_A_matrix_1_zeolite_1_osda_1_zgm(self):
        self.m.update_components("zeolite", [(1, 1.0)])
        self.m.update_components("template", [(6, 2.0)])
        self.m.update_components("zgm", [(20, 3.0)])
        ref = np.array([self.m.components[0].molwt,
                        self.m.components[1].molwt*2.0,
                        self.m.components[2].molwt*3.0])
        A_vector = self.m.get_A_matrix()
        self.assertTrue(np.allclose(A_vector, ref, rtol=1.0e-4, atol=1.0e-4))

    def test_get_wight_fraction_mixture_SiO2(self):
        self.m.update_reactants([(7, 0.3), (10, 1.0)])
        comps = self.m.session.query(cal.Batch,cal.DBComponent).\
                    filter(cal.Batch.reactant_id == 7).\
                    filter(cal.DBComponent.id == cal.Batch.component_id).all()

        wfs = self.m.get_weight_fractions(0, comps)
        self.assertEqual(wfs[0][0], 4)
        self.assertEqual(wfs[1][0], 5)
        self.assertAlmostEqual(wfs[0][1], 0.3, places=2)
        self.assertAlmostEqual(wfs[1][1], 0.7, places=2)

    def test_get_wight_fraction_mixture_H2O(self):
        self.m.update_reactants([(7, 0.3), (10, 1.0)])
        comps = self.m.session.query(cal.Batch,cal.DBComponent).\
                    filter(cal.Batch.reactant_id == 10).\
                    filter(cal.DBComponent.id == cal.Batch.component_id).all()

        wfs = self.m.get_weight_fractions(1, comps)
        self.assertEqual(wfs[0][0], 5)
        self.assertAlmostEqual(wfs[0][1], 1.0, places=2)

    def test_get_B_matrix_NaOH_H2O(self):
        ref = np.array([[0.7593, 0.2407], [0.0, 1.0]])
        self.m.update_components("zeolite", [(1, 4.8), (5, 249.5)])
        self.m.update_reactants([(1, 0.98), (10, 1.0)])
        B_matrix = self.m.get_B_matrix()
        self.assertTrue(np.allclose(B_matrix, ref, rtol=1.0e-4, atol=1.0e-4))

    def test_calculate_offretite(self):
        self.m.update_components("zeolite", [(2, 1.0), (3, 1.0), (4, 15.8), (5, 249.5), (1, 4.8)])
        self.m.update_reactants([(2, 0.87), (10, 1.0), (1, 0.98), (5, 0.98), (9, 1.0)])
        self.m.calculate()
        X_ref = np.array([ 128.9783908,
                          4419.74648854,
                           391.80803265,
                           408.48928,
                           949.33194])
        B_ref = np.array([[ 0.73032389,  0.        ,  0.        ,  0.26967611,  0.        ],
                          [ 0.        ,  0.        ,  0.        ,  1.        ,  0.        ],
                          [ 0.        ,  0.        ,  0.        ,  0.24070237,  0.75929763],
                          [ 0.        ,  0.24960577,  0.        , -0.13230604,  0.        ],
                          [ 0.        ,  0.        ,  1.        ,  0.        ,  0.        ]])
        self.assertTrue(np.allclose(self.m.B, B_ref, rtol=8, atol=6))
        self.assertTrue(np.allclose(self.m.X, X_ref, rtol=8, atol=6))

if __name__ == "__main__":
    unittest.main()
