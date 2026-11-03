// DevExit DX-02. All rates are user-selected illustrative assumptions.
export function calculate({gross, redemption, rate, months, fee, costs}) {
  const limits = {gross:[1,1e10], redemption:[0,1e10], rate:[0,10], months:[0,60], fee:[0,100], costs:[0,1e10]};
  for (const [key, [min,max]] of Object.entries(limits)) {
    const value = {gross,redemption,rate,months,fee,costs}[key];
    if (!Number.isFinite(value) || value < min || value > max) throw new RangeError(`Invalid ${key}`);
  }
  if (!Number.isInteger(months)) throw new RangeError('Use whole reserve months');
  const interest = gross * rate / 100 * months;
  const arrangement = gross * fee / 100;
  const net = gross - interest - arrangement - costs;
  const balance = net - redemption;
  const fraction = 1 - rate / 100 * months - fee / 100;
  const requiredGross = fraction > 0 ? (redemption + costs) / fraction : null;
  return {interest, arrangement, net, balance, requiredGross};
}
