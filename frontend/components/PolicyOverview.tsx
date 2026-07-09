'use client';

export default function PolicyOverview() {
  return (
    <div className="space-y-10">
      {/* Summary */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          New Jersey&apos;s enacted Child Tax Credit increase
        </h2>
        <p className="text-gray-700 mb-4">
          As part of the FY2027 state budget, New Jersey enacted S-4531
          (P.L.2026, c.26), which raises every New Jersey Child Tax Credit
          amount by 25% for tax years 2026 through 2028. Credit amounts
          revert to their prior levels in 2029. Eligibility is unchanged:
          the credit remains available per child age 5 or younger to
          filers with New Jersey taxable income of $80,000 or less. This
          dashboard reports household, statewide, and congressional
          district impacts of the increase relative to prior law for tax
          year 2026.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-gray-800 mb-2">What changed</h3>
            <p className="text-sm text-gray-600">
              Per-child credit amounts rise 25%, to{' '}
              <strong>$1,250 / $1,000 / $750 / $500 / $250</strong> across
              the existing $0&ndash;$30k, $30k&ndash;$40k, $40k&ndash;$50k,
              $50k&ndash;$60k, and $60k&ndash;$80k taxable income tiers
              (previously $1,000 / $800 / $600 / $400 / $200). The $80,000
              income ceiling and under-6 age limit are unchanged.
            </p>
          </div>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-gray-800 mb-2">
              Effective 2026&ndash;2028
            </h3>
            <p className="text-sm text-gray-600">
              The higher amounts apply for tax years 2026, 2027, and 2028,
              and revert to prior levels in 2029. This dashboard models tax
              year 2026; impacts are reported relative to prior law (the
              pre-increase credit amounts).
            </p>
          </div>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-gray-800 mb-2">Cost</h3>
            <p className="text-sm text-gray-600">
              The Office of Legislative Services estimates the increase
              reduces state revenue by $51.9 million in FY2027, $50.3
              million in FY2028, and $48.7 million in FY2029. The NJ
              Treasury estimates $50.0 million for FY2027, and reports
              232,500 credits claimed for tax year 2024 ($220.7 million).
              PolicyEngine&apos;s microsimulation estimates $60 million for
              tax year 2026 (see the Statewide tab).
            </p>
          </div>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-gray-800 mb-2">Who benefits</h3>
            <p className="text-sm text-gray-600">
              Families with children age 5 or younger and taxable income of
              $80,000 or less. The credit is refundable and is claimed on
              the NJ-1040; it is available to all filing statuses except
              married filing separately.
            </p>
          </div>
        </div>
      </div>

      {/* Parameter changes table */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          Credit amounts per child (tax years 2026&ndash;2028)
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-900">NJ taxable income</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-900">Prior law (and 2029+)</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-900">Enacted 2026&ndash;2028</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-900">Change</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-100">
                <td className="py-3 px-4 text-gray-700">$30,000 or less</td>
                <td className="py-3 px-4 text-right text-gray-700">$1,000</td>
                <td className="py-3 px-4 text-right text-gray-700">$1,250</td>
                <td className="py-3 px-4 text-right font-semibold text-primary-600">+$250</td>
              </tr>
              <tr className="border-b border-gray-100">
                <td className="py-3 px-4 text-gray-700">$30,001 &ndash; $40,000</td>
                <td className="py-3 px-4 text-right text-gray-700">$800</td>
                <td className="py-3 px-4 text-right text-gray-700">$1,000</td>
                <td className="py-3 px-4 text-right font-semibold text-primary-600">+$200</td>
              </tr>
              <tr className="border-b border-gray-100">
                <td className="py-3 px-4 text-gray-700">$40,001 &ndash; $50,000</td>
                <td className="py-3 px-4 text-right text-gray-700">$600</td>
                <td className="py-3 px-4 text-right text-gray-700">$750</td>
                <td className="py-3 px-4 text-right font-semibold text-primary-600">+$150</td>
              </tr>
              <tr className="border-b border-gray-100">
                <td className="py-3 px-4 text-gray-700">$50,001 &ndash; $60,000</td>
                <td className="py-3 px-4 text-right text-gray-700">$400</td>
                <td className="py-3 px-4 text-right text-gray-700">$500</td>
                <td className="py-3 px-4 text-right font-semibold text-primary-600">+$100</td>
              </tr>
              <tr className="border-b border-gray-100">
                <td className="py-3 px-4 text-gray-700">$60,001 &ndash; $80,000</td>
                <td className="py-3 px-4 text-right text-gray-700">$200</td>
                <td className="py-3 px-4 text-right text-gray-700">$250</td>
                <td className="py-3 px-4 text-right font-semibold text-primary-600">+$50</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* References */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">References</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-gray-800 mb-2">
              Enacted legislation
            </h4>
            <ul className="text-sm text-gray-700 space-y-1">
              <li>
                <a
                  href="https://pub.njleg.state.nj.us/Bills/2026/S5000/4531_I1.PDF"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:underline"
                >
                  S-4531 (P.L.2026, c.26) &mdash; text amending
                  N.J.S.A. 54A:4-17.1
                </a>
              </li>
              <li>
                <a
                  href="https://pub.njleg.state.nj.us/Bills/2026/S5000/4531_F1.PDF"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:underline"
                >
                  OLS fiscal estimate ($51.9M FY2027)
                </a>
              </li>
            </ul>
          </div>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-gray-800 mb-2">
              Program administration and cost
            </h4>
            <ul className="text-sm text-gray-700 space-y-1">
              <li>
                <a
                  href="https://www.nj.gov/treasury/taxation/individuals/childtaxcredit.shtml"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:underline"
                >
                  NJ Division of Taxation &mdash; Child Tax Credit
                </a>
              </li>
              <li>
                <a
                  href="https://www.nj.gov/treasury/taxation/pdf/taxexpenditurereport2027.pdf#page=44"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:underline"
                >
                  NJ Treasury FY2027 tax expenditure report (item 63)
                </a>
              </li>
            </ul>
          </div>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-gray-800 mb-2">Calculations</h4>
            <p className="text-sm text-gray-700">
              Powered by{' '}
              <a
                href="https://github.com/PolicyEngine/policyengine-us"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-600 hover:underline"
              >
                policyengine-us
              </a>
              , which encodes the enacted change from the statute.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
