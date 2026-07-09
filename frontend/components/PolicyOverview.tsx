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
              The NJ Treasury&apos;s FY2027 tax expenditure report estimates
              the credit costs $207.4 million under prior law, implying
              roughly $52 million per year in additional outlays from the
              25% increase (about $260 million in total credits).
              PolicyEngine&apos;s microsimulation estimates a similar
              baseline ($216 million in 2026, about 237,000 recipient tax
              units averaging $912).
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
                  href="https://www.njleg.state.nj.us/bill-search/2026/S4531"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:underline"
                >
                  S-4531 (P.L.2026, c.26)
                </a>
              </li>
              <li>
                <a
                  href="https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-4-17-1/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:underline"
                >
                  N.J. Stat. § 54A:4-17.1 &mdash; Child tax credit
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
                  href="https://www.nj.gov/treasury/taxation/pdf/taxexpenditurereport2027.pdf"
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
