import csv
import io
import streamlit as st
from model import calculate

st.set_page_config(page_title='DevExit | Final-unit release calculator', page_icon='🏘️', layout='wide')
st.caption('DEVEXIT RESEARCH TOOLS · DX-06 · 6 NOVEMBER 2026')
st.title('What debt stays with the final units?')
st.markdown('A unit sale reduces the stock securing a loan. How much it reduces the loan depends on the principal repayment agreed for that release. Compare the cash kept now with the debt and interest left for the remaining sales period.')
st.markdown('For funding a completed scheme through that period, see **[DevExit.co.uk’s sales period finance guide](https://devexit.co.uk/finance/sales-period-finance/)**.')
st.caption('By Matt Lenzie for DevExit. An illustrative planning model, not a lender quote or approval.')

st.subheader('1. Set a hypothetical scheme')
st.write('Each unit has the same gross value in this simplified model. The release percentage means principal repaid as a percentage of the gross price, not a percentage of net sale proceeds.')
a,b,c = st.columns(3)
with a:
    units = st.number_input('Units before these sales', min_value=1, max_value=30, value=6, step=1, key='units')
    price = st.number_input('Gross price per unit (£)', min_value=1000, max_value=10000000, value=500000, step=10000, key='price')
    debt = st.number_input('Opening principal (£)', min_value=0, max_value=300000000, value=1950000, step=25000, key='debt')
with b:
    if 'sold' not in st.session_state:
        st.session_state.sold = min(4, units)
    if st.session_state.sold is not None and st.session_state.sold > units:
        st.session_state.sold = units
    sold = st.number_input('Units sold before the holding period', min_value=0, max_value=units, value=None, step=1, key='sold')
    release = st.number_input('Principal release (% of gross price)', min_value=0.0, max_value=150.0, value=60.0, step=5.0, key='release')
    costs = st.number_input('Selling costs (% of gross price)', min_value=0.0, max_value=100.0, value=2.0, step=0.5, key='costs')
with c:
    rate = st.number_input('Illustrative monthly interest (%)', min_value=0.0, max_value=5.0, value=0.8, step=0.05, key='rate')
    months = st.number_input('Further months with no sales', min_value=0, max_value=36, value=6, step=1, key='months')
    target = st.number_input('Comparison LTV ceiling (%)', min_value=0.0, max_value=100.0, value=65.0, step=5.0, key='target')
st.caption('The comparison ceiling is your assumption, not an available lender limit. Interest is paid separately. The holding period starts after the selected sales; earlier interest is excluded.')
if sold is None:
    st.info('Enter the number of units sold to calculate the result.')
    st.stop()
args=dict(units=units, price=price, debt=debt, sold=sold, release_pct=release, costs_pct=costs, monthly_pct=rate, months=months, target_pct=target)
r=calculate(**args)
s=calculate(**args,sweep=True)
gbp=lambda x: f'£{x:,.0f}'
pct=lambda x: 'N/A' if x is None else f'{x:.1f}%'

st.subheader('2. Read the remaining exposure')
a,b,c=st.columns(3)
a.metric('Principal remaining',gbp(r['debt']))
b.metric('LTV on remaining gross value',pct(r['ltv']))
c.metric(f'Interest over {months} further months',gbp(r['interest']))
if sold == units:
    if r['debt']:
        st.error(f"All units are sold but {gbp(r['debt'])} of principal remains. There is no remaining property value in this model. A different repayment source would be needed; do not assume the lender would permit these releases.")
    else:
        st.success('All units are sold and principal is cleared. No further interest is modelled.')
elif r['target_shortfall']:
    st.warning(f"Principal is {gbp(r['target_shortfall'])} above the amount supported by your {target:g}% comparison ceiling. This is a model comparison, not a covenant or lending decision.")
else:
    st.info('Remaining principal is within your comparison ceiling. That alone does not establish refinance availability or lender consent.')
if r['topup']:
    st.error(f"The selected releases require {gbp(r['topup'])} of additional cash beyond net sale proceeds. The debt figures assume this cash is supplied; otherwise the release schedule is not funded.")

comparison=[
    {'Measure':'Principal repaid on selected sales','Chosen releases':gbp(debt-r['debt']),'All net proceeds to principal':gbp(debt-s['debt'])},
    {'Measure':'Cash retained from selected sales*','Chosen releases':gbp(r['cash']),'All net proceeds to principal':gbp(s['cash'])},
    {'Measure':'Additional cash needed for releases','Chosen releases':gbp(r['topup']),'All net proceeds to principal':gbp(s['topup'])},
    {'Measure':'Principal left','Chosen releases':gbp(r['debt']),'All net proceeds to principal':gbp(s['debt'])},
    {'Measure':'Remaining gross property value','Chosen releases':gbp(r['remaining_value']),'All net proceeds to principal':gbp(s['remaining_value'])},
    {'Measure':'Remaining LTV','Chosen releases':pct(r['ltv']),'All net proceeds to principal':pct(s['ltv'])},
    {'Measure':'Further holding-period interest','Chosen releases':gbp(r['interest']),'All net proceeds to principal':gbp(s['interest'])},
]
st.table(comparison)
st.caption('*Before interest, taxes, fees, other debt and historic project costs. This cash is not profit or confirmed distributable equity. Both routes require lender agreement. The net-proceeds route stops repaying when principal reaches zero.')
direction = 'more' if r['debt'] >= s['debt'] else 'less'
st.write(f"The chosen releases leave {gbp(abs(r['debt']-s['debt']))} {direction} principal and {gbp(abs(r['interest']-s['interest']))} {direction} holding-period interest than the net-proceeds route.")

st.subheader('3. Check each release')
if r['rows']:
    display=[]
    for row in r['rows']:
        display.append({'Sale':row['sale'],'Net receipt':gbp(row['net_proceeds']),'Principal repaid':gbp(row['principal_repayment']),'Cash retained':gbp(row['cash_retained']),'Cash top-up':gbp(row['external_topup']),'Debt left':gbp(row['debt']),'Stock value left':gbp(row['remaining_value']),'LTV':pct(row['ltv'])})
    st.dataframe(display,hide_index=True,width='stretch')
else:
    st.write('No sales selected. Opening debt and stock remain unchanged.')
if sold:
    st.write(f"To finish these {sold} sales at or below the {target:g}% comparison ceiling, aggregate principal repayments would need to be at least {gbp(r['required_total'])}. Spread evenly, that is {gbp(r['required_per_sale'])} per sale, or {r['required_per_sale']/price*100:.1f}% of the gross unit price.")
    if r['required_per_sale'] > r['net']:
        st.warning('That average exceeds net proceeds per sale. Sale proceeds alone cannot achieve the selected ceiling.')
else:
    st.write('Select at least one sale to calculate an average release amount for the comparison ceiling.')
st.caption('The average is an aggregate end-point test. It does not test interim covenants, individual unit valuations, release consents or cash availability on each completion date.')

buf=io.StringIO(); writer=csv.writer(buf)
writer.writerow(['DevExit DX-06 illustrative release model','6 November 2026'])
for k,v in args.items():writer.writerow([k,v])
writer.writerow([])
keys=['sale','net_proceeds','principal_repayment','cash_retained','external_topup','debt','remaining_value','ltv']
writer.writerow(keys)
for row in r['rows']:writer.writerow(['' if row[k] is None else row[k] for k in keys])
writer.writerow([])
for k in ['debt','remaining_value','ltv','cash','topup','interest','required_total','required_per_sale','target_shortfall']:writer.writerow([k,r[k]])
writer.writerow(['Scope','Hypothetical only; interest serviced separately; excludes earlier interest, fees, taxes and project costs; lender consent not assumed.'])
st.download_button('Download this scenario (CSV)',buf.getvalue(),'devexit-release-scenario.csv','text/csv')

st.subheader('Why the tail can become more expensive per unit')
st.markdown('In the starting example, six £500,000 units support £1.95 million of debt: 65% of their £3 million gross value. Four sales repay £300,000 each. The debt falls to £750,000, but only two units worth £1 million remain. LTV rises to 75%, even though principal has fallen.')
st.markdown('At the invented 0.8% monthly rate, interest per unsold unit rises from £2,600 at the opening position to £3,000 after those releases. Six further months with no sales cost £36,000. Applying all net proceeds from the same four sales would clear the £1.95 million principal and leave £10,000 before other costs. The trade-off is cash retained earlier versus debt carried later, not a claim that one structure suits every scheme.')
st.caption('This worked explanation always describes the starting example; the outputs above follow your edited inputs. The sale price used for remaining security is an assumption, not a lender valuation.')

st.subheader('Put the result into the wider repayment plan')
st.markdown('The [North West repayment-routes companion](https://sites.google.com/view/devexit-north-west-exit-routes) adds completion dates and a bulk-sale alternative. Use it when the question is whether debt clears before maturity; this calculator isolates release amounts and assumes no further sales during the holding period.')
st.markdown('If the remaining debt needs refinancing, the [net advance calculator](https://mattylll.github.io/devexit-2026-q3-08-development-exit-finance-rates/net-advance/) checks how fees and retained interest affect the cash available to redeem it. If a buyer proposes buying all remaining units, the [bulk-offer briefing](https://devexit-research.blogspot.com/2026/11/blog-post.html) separates a debt-clearing price from the cash the developer wants to retain.')
st.markdown('Bring the lender’s actual release schedule, current redemption figure, unit valuations and dated sales forecast to the funding discussion. **[DevExit.co.uk’s sales period finance guide](https://devexit.co.uk/finance/sales-period-finance/)** explains the relevant funding route. An extension, new facility or release of surplus needs agreement.')

st.subheader('Method, evidence and scope')
st.markdown('The [DevExit Q3 2026 development exit finance report](https://devexit.co.uk/reports/q3-2026-development-exit-finance-report/) is the programme’s market context. Its registered-charge counts do not calibrate the amounts, release percentages, rates or LTV ceiling in this tool. All default model inputs are invented. This app and its linked companions share DevExit authorship and are not independent corroborating studies.')
st.markdown('For each sale: net receipt = gross price × (1 − selling cost %); principal repayment = the smaller of opening outstanding principal and gross price × release %; remaining principal = prior principal − repayment. Cash retained and any external top-up are shown separately. Remaining LTV = debt ÷ assumed gross value of unsold units. Further interest = remaining principal × monthly rate × months, with no compounding or further sales.')
st.markdown('The model excludes interest accrued before the holding period, retained interest, minimum interest, arrangement and exit fees, taxes, build costs, junior debt, valuation changes and legal costs. It assumes the displayed top-ups are funded and each release is permitted. It does not establish net development profit, affordability, loan eligibility or the amount a lender will advance.')
st.caption('Prepared with AI assistance. Original commentary and calculations © 2026 DevExit, all rights reserved. No Rightmove series reproduced. DevExit is a trading name of Lenzie Consulting Ltd, a finance arranger and introducer, not a lender. General information, not financial, legal, tax or investment advice or an offer of finance.')
