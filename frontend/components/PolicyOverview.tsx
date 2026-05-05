'use client';

export default function PolicyOverview() {
  return (
    <div className="space-y-10">
      {/* Summary */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          NJ Cash Alliance CTC + EITC expansion
        </h2>
        <p className="text-gray-700 mb-4">
          The New Jersey Cash Alliance and a coalition of advocacy groups,
          community leaders, and policy organizations are calling on the state
          to expand two of New Jersey&apos;s flagship cash supports for families:
          the state Child Tax Credit and the state Earned Income Tax Credit.
          This dashboard models three variants of the proposal &mdash; the CTC
          expansion alone, the EITC expansion alone, and the combined package
          &mdash; and reports household, statewide, and district-level fiscal
          and distributional impacts for tax year 2026.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-gray-800 mb-2">CTC expansion</h3>
            <p className="text-sm text-gray-600">
              Raises the per-bracket NJ Child Tax Credit amounts to{' '}
              <strong>$1,500 / $1,000 / $750 / $500 / $250</strong> across
              the existing $0&ndash;$30k, $30k&ndash;$40k, $40k&ndash;$50k,
              $50k&ndash;$60k, and $60k&ndash;$80k income tiers (currently
              $1,000 / $800 / $600 / $400 / $200; phase-out at $80k stays).
              Extends the age limit from <strong>under 6</strong> to{' '}
              <strong>under 12</strong>.
            </p>
          </div>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-gray-800 mb-2">EITC expansion</h3>
            <p className="text-sm text-gray-600">
              Raises the New Jersey EITC match from <strong>40%</strong> of the
              federal Earned Income Tax Credit to <strong>50%</strong>.
            </p>
          </div>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-gray-800 mb-2">Combined package</h3>
            <p className="text-sm text-gray-600">
              Both expansions enacted together. The Statewide and Congressional
              Districts tabs let you compare the three variants side by side.
            </p>
          </div>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-gray-800 mb-2">Effective 2026</h3>
            <p className="text-sm text-gray-600">
              All three variants are modeled for tax year 2026. Impacts are
              reported as the change relative to current New Jersey law.
            </p>
          </div>
        </div>
      </div>

      {/* Parameter changes table */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          Parameter changes (combined variant, 2026)
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-900">Parameter</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-900">Current law</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-900">Proposed</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-900">Change</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-100">
                <td className="py-3 px-4 text-gray-700">CTC amount &mdash; $0&ndash;$30k bracket</td>
                <td className="py-3 px-4 text-right text-gray-700">$1,000</td>
                <td className="py-3 px-4 text-right text-gray-700">$1,500</td>
                <td className="py-3 px-4 text-right font-semibold text-primary-600">+$500</td>
              </tr>
              <tr className="border-b border-gray-100">
                <td className="py-3 px-4 text-gray-700">CTC amount &mdash; $30k&ndash;$40k bracket</td>
                <td className="py-3 px-4 text-right text-gray-700">$800</td>
                <td className="py-3 px-4 text-right text-gray-700">$1,000</td>
                <td className="py-3 px-4 text-right font-semibold text-primary-600">+$200</td>
              </tr>
              <tr className="border-b border-gray-100">
                <td className="py-3 px-4 text-gray-700">CTC amount &mdash; $40k&ndash;$50k bracket</td>
                <td className="py-3 px-4 text-right text-gray-700">$600</td>
                <td className="py-3 px-4 text-right text-gray-700">$750</td>
                <td className="py-3 px-4 text-right font-semibold text-primary-600">+$150</td>
              </tr>
              <tr className="border-b border-gray-100">
                <td className="py-3 px-4 text-gray-700">CTC amount &mdash; $50k&ndash;$60k bracket</td>
                <td className="py-3 px-4 text-right text-gray-700">$400</td>
                <td className="py-3 px-4 text-right text-gray-700">$500</td>
                <td className="py-3 px-4 text-right font-semibold text-primary-600">+$100</td>
              </tr>
              <tr className="border-b border-gray-100">
                <td className="py-3 px-4 text-gray-700">CTC amount &mdash; $60k&ndash;$80k bracket</td>
                <td className="py-3 px-4 text-right text-gray-700">$200</td>
                <td className="py-3 px-4 text-right text-gray-700">$250</td>
                <td className="py-3 px-4 text-right font-semibold text-primary-600">+$50</td>
              </tr>
              <tr className="border-b border-gray-100">
                <td className="py-3 px-4 text-gray-700">CTC age limit (qualifying child)</td>
                <td className="py-3 px-4 text-right text-gray-700">under 6</td>
                <td className="py-3 px-4 text-right text-gray-700">under 12</td>
                <td className="py-3 px-4 text-right font-semibold text-primary-600">+6 years</td>
              </tr>
              <tr className="border-b border-gray-100">
                <td className="py-3 px-4 text-gray-700">EITC match (% of federal EITC)</td>
                <td className="py-3 px-4 text-right text-gray-700">40%</td>
                <td className="py-3 px-4 text-right text-gray-700">50%</td>
                <td className="py-3 px-4 text-right font-semibold text-primary-600">+10 pp</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Signatories + references */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Letter signatories</h3>
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-gray-700 mb-2">
            The proposal is supported by the following organizations and
            community leaders:
          </p>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-x-6 text-sm text-gray-700 list-disc pl-5">
            <li>The New Jersey Cash Alliance</li>
            <li>The Bridge Project</li>
            <li>Community Health Acceleration Partnership</li>
            <li>Clinton Hill Community Action</li>
            <li>Economic Security Project</li>
            <li>Homes For All Newark</li>
            <li>La Casa de Don Pedro, Inc.</li>
            <li>Mayors for a Guaranteed Income</li>
            <li>New Jersey Citizen Action</li>
            <li>New Jersey Institute for Social Justice</li>
            <li>New Jersey Policy Perspective</li>
            <li>The United Ways of New Jersey (all 12 counties)</li>
          </ul>
        </div>

        <h3 className="text-lg font-semibold text-gray-900 mb-3">References</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-gray-800 mb-2">
              NJ Child Tax Credit (current law)
            </h4>
            <ul className="text-sm text-gray-700 space-y-1">
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
              <li>
                <a
                  href="https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf#page=46"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:underline"
                >
                  2025 NJ-1040 instructions (line 65)
                </a>
              </li>
            </ul>
          </div>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-gray-800 mb-2">
              NJ Earned Income Tax Credit (current law)
            </h4>
            <ul className="text-sm text-gray-700 space-y-1">
              <li>
                <a
                  href="https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-4-7/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:underline"
                >
                  N.J. Stat. § 54A:4-7 &mdash; New Jersey EITC
                </a>
              </li>
              <li>
                <a
                  href="https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf#page=44"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:underline"
                >
                  2025 NJ-1040 instructions (line 58)
                </a>
              </li>
            </ul>
          </div>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-gray-800 mb-2">Calculations</h4>
            <p className="text-sm text-gray-700">
              Powered by{' '}
              <a
                href="https://github.com/PolicyEngine/policyengine.py"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-600 hover:underline"
              >
                policyengine
              </a>{' '}
              v4.3.1.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
