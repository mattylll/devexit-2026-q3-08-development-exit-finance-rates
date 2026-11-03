# DevExit net advance calculator

DX-02. By Matt Lenzie / DevExit, prepared with AI assistance. Published 3 November 2026.

This browser-local calculator compares the cash left at completion after retained simple interest, a fee on gross facility and other completion costs. It does not compare whole-life borrowing cost or determine loan eligibility. It makes no requests with entered figures, stores no figures and includes no analytics or contact form.

Default illustrative comparison: £3.3m gross, £3m redemption, 2% fee, £20,000 other costs. Structure A retains 12 months at 0.65% per month: £257,400 interest, £2,956,600 net, £43,400 shortfall. Structure B retains six months at 0.85%: £168,300 interest, £3,045,700 net, £45,700 remaining. These are invented assumptions, not quotes or observed deals.

## Method

Retained interest = gross × rate / 100 × months. Arrangement fee = gross × fee / 100. Net = gross − interest − arrangement fee − other costs. Balance = net − redemption. Required gross = (redemption + costs) / (1 − rate / 100 × months − fee / 100), when the denominator is positive.

All inputs are non-negative finite numbers; gross must be positive. Reserve months must be whole numbers. Input guardrails are software limits, not lending criteria. Display is rounded to pounds and CSV to pence, without intermediate rounding. Actual facilities may calculate interest on another base, compound it, service it monthly or refund reserves. The model excludes changing balances, sales, maturity repayment, new-loan exit fees and other items unless explicitly included in a relevant input. Six retained months does not establish the loan term or cover interest after month six.

## Run and verify

No dependencies or build step. Serve the repository with any static HTTP server, then open `net-advance/`. ES modules require HTTP rather than a local file URL. Run `node --test net-advance/model.test.mjs` from the repository root.

## Evidence and rights

Related research: [DevExit Q3 2026 report](https://devexit.co.uk/reports/q3-2026-development-exit-finance-report/) and [national supplement](https://doi.org/10.5281/zenodo.23925176). The research counts do not calibrate the illustrative rates. This is a companion to the same research programme, not an independent study. No dataset or Rightmove series is redistributed.

© 2026 DevExit. Original content and code: all rights reserved. No blanket open licence is assigned. DevExit is a trading name of Lenzie Consulting Ltd and a finance arranger and introducer, not a lender. General illustrative analysis, not an offer of finance or financial, legal, tax or investment advice.
