import unittest
from decimal import Decimal as D
from model import calculate

class ReleaseTests(unittest.TestCase):
    def test_default_and_cash_conservation(self):
        r=calculate()
        self.assertEqual((r['debt'],r['ltv'],r['interest'],r['cash']),(D(750000),D(75),D(36000),D(760000)))
        self.assertEqual(r['required_per_sale'],D(325000))
        self.assertEqual(D(4*490000)+r['topup'], D(1950000)-r['debt']+r['cash'])
    def test_net_sweep_stops_at_zero(self):
        r=calculate(sweep=True)
        self.assertEqual((r['debt'],r['cash'],r['interest']),(0,10000,0))
        self.assertEqual(r['rows'][-1]['principal_repayment'],480000)
    def test_unfunded_release_is_explicit(self):
        r=calculate(sold=1, release_pct=110)
        self.assertEqual((r['topup'],r['debt'],r['cash']),(60000,1400000,0))
    def test_all_units_sold_with_debt(self):
        r=calculate(sold=6,release_pct=50)
        self.assertEqual(r['debt'],450000)
        self.assertIsNone(r['ltv'])
        self.assertEqual(r['remaining_value'],0)
    def test_no_sales_and_zero_debt(self):
        r=calculate(sold=0)
        self.assertEqual(r['debt'],1950000)
        self.assertIsNone(r['required_per_sale'])
        r=calculate(debt=0)
        self.assertEqual((r['debt'],r['interest'],r['cash']),(0,0,1960000))
    def test_invalid_input(self):
        for args in [dict(sold=7),dict(price=0),dict(costs_pct=101),dict(release_pct=-1)]:
            with self.assertRaises(ValueError):calculate(**args)

if __name__=='__main__':unittest.main()
