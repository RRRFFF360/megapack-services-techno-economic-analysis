"""Run with: python -m unittest discover -s tests -v"""
import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'model'))
from dispatch_optimization import solve_day
from service_economics import pv_annuity,service_scenarios

class TestOutageModel(unittest.TestCase):
    def day(self):
        return pd.DataFrame({'operating_date':['2025-01-01']*24,'lmp_per_mwh':[25.]*12+[100.]*12})

    def test_full_outage_prevents_all_dispatch(self):
        result=solve_day(self.day(),availability=np.zeros(24))
        self.assertAlmostEqual(float(result.charge_mw.abs().sum()),0,places=6)
        self.assertAlmostEqual(float(result.discharge_mw.abs().sum()),0,places=6)
        self.assertAlmostEqual(float(result.hourly_market_value_usd.sum()),0,places=6)
        self.assertAlmostEqual(float(result.soc_end_mwh.iloc[-1]),19.58,places=6)

    def test_outage_never_raises_objective(self):
        day=self.day()
        baseline=solve_day(day).hourly_market_value_usd.sum()
        mask=np.ones(24);mask[13:17]=0
        after=solve_day(day,availability=mask)
        self.assertLessEqual(after.hourly_market_value_usd.sum(),baseline+0.01)
        self.assertTrue((after.iloc[13:17].charge_mw.abs()<1e-6).all())
        self.assertTrue((after.iloc[13:17].discharge_mw.abs()<1e-6).all())

    def test_invalid_masks_rejected(self):
        with self.assertRaises(ValueError): solve_day(self.day(),availability=np.ones(23))
        with self.assertRaises(ValueError): solve_day(self.day(),availability=np.full(24,1.1))
        for value in (-.1, float('nan'), float('inf')):
            with self.assertRaises(ValueError): solve_day(self.day(),availability=np.full(24,value))

    def test_dst_days_preserve_all_intervals_and_soc(self):
        for hours in (23,25):
            with self.subTest(hours=hours):
                day=pd.DataFrame({'lmp_per_mwh':[25.]*(hours//2)+[100.]*(hours-hours//2)})
                result=solve_day(day,availability=np.zeros(hours))
                self.assertEqual(len(result),hours)
                self.assertTrue(np.allclose(result.soc_end_mwh,19.58))
                self.assertAlmostEqual(result.hourly_market_value_usd.sum(),0.,places=6)

    def test_partial_availability_enforces_power_and_energy_balance(self):
        result=solve_day(self.day(),availability=np.full(24,.25))
        self.assertLessEqual(result.charge_mw.max(),9.79*.25+1e-6)
        self.assertLessEqual(result.discharge_mw.max(),9.79*.25+1e-6)
        eta=np.sqrt(.937)
        self.assertTrue(np.allclose(result.soc_end_mwh-result.soc_start_mwh,
                                    eta*result.charge_mw-result.discharge_mw/eta))
        self.assertLessEqual(result.discharge_mw.sum()/eta,39.16+1e-6)
        self.assertTrue((np.minimum(result.charge_mw,result.discharge_mw)<1e-6).all())
        self.assertAlmostEqual(result.soc_end_mwh.iloc[-1],19.58,places=6)

    def test_nonfinite_parameters_rejected(self):
        for value in (float('nan'),float('inf')):
            with self.assertRaises(ValueError): solve_day(self.day(),cycles=value)
            with self.assertRaises(ValueError): solve_day(self.day(),rte=value)

    def test_example_cost_arithmetic_not_provider_evidence(self):
        s=service_scenarios(250.)
        own=s.loc[s.service_path.str.contains('in-house')].iloc[0]
        self.assertEqual(own.annual_service_plus_da_loss_usd,36500.)
        self.assertFalse(bool(own.is_verified_provider_performance))
        self.assertGreater(pv_annuity(20000.),0)

if __name__=='__main__':
    unittest.main()
