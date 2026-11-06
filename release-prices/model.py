"""Illustrative principal release arithmetic. No market-calibrated assumptions."""
from decimal import Decimal, ROUND_HALF_UP

D = lambda x: Decimal(str(x))
CENT = Decimal('0.01')

def money(x):
    return D(x).quantize(CENT, rounding=ROUND_HALF_UP)

def calculate(units=6, price=500000, debt=1950000, sold=4, release_pct=60,
              costs_pct=2, monthly_pct=0.8, months=6, target_pct=65, sweep=False):
    if not isinstance(units, int) or not isinstance(sold, int) or not 1 <= units <= 30 or not 0 <= sold <= units:
        raise ValueError('Units must be whole numbers; sales cannot exceed units.')
    price, debt = money(price), money(debt)
    release, costs, rate, target = map(D, (release_pct, costs_pct, monthly_pct, target_pct))
    if price <= 0 or debt < 0 or not 0 <= costs <= 100 or not 0 <= release <= 150 or rate < 0 or months < 0 or not 0 <= target <= 100:
        raise ValueError('Invalid amount, rate or percentage.')
    net = money(price * (1 - costs / 100))
    balance, cash, topup = debt, D(0), D(0)
    rows = []
    for n in range(1, sold + 1):
        repayment = min(balance, net if sweep else money(price * release / 100))
        balance -= repayment
        available, gap = max(D(0), net - repayment), max(D(0), repayment - net)
        cash += available
        topup += gap
        value = price * (units - n)
        rows.append(dict(sale=n, net_proceeds=net, principal_repayment=repayment,
                         cash_retained=available, external_topup=gap, debt=balance,
                         remaining_value=value, ltv=(balance / value * 100 if value else None)))
    value = price * (units - sold)
    target_debt = money(value * target / 100)
    required = max(D(0), debt - target_debt)
    return dict(rows=rows, debt=balance, remaining_value=value,
                ltv=(balance / value * 100 if value else None), cash=cash, topup=topup,
                interest=money(balance * rate / 100 * D(months)), net=net,
                required_total=required, required_per_sale=(required / sold if sold else None),
                target_shortfall=max(D(0), balance - target_debt))
