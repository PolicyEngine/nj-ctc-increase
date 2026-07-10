'use client';

import { useState, useEffect } from 'react';
import NJDistrictMap, { NJDistrictData } from './DynamicDistrictMap';
import ChartWatermark from './ChartWatermark';

interface Props {
  year?: number;
}

// New Jersey representatives (119th Congress).
const NJ_REPRESENTATIVES: Record<string, { name: string; party: 'R' | 'D' }> = {
  '1': { name: 'Donald Norcross', party: 'D' },
  '2': { name: 'Jeff Van Drew', party: 'R' },
  '3': { name: 'Herb Conaway', party: 'D' },
  '4': { name: 'Chris Smith', party: 'R' },
  '5': { name: 'Josh Gottheimer', party: 'D' },
  '6': { name: 'Frank Pallone', party: 'D' },
  '7': { name: 'Tom Kean Jr', party: 'R' },
  '8': { name: 'Rob Menendez', party: 'D' },
  '9': { name: 'Nellie Pou', party: 'D' },
  '10': { name: 'LaMonica McIver', party: 'D' },
  '11': { name: 'Analilia Mejia', party: 'D' },
  '12': { name: 'Bonnie Watson Coleman', party: 'D' },
};

function partyColor(party: 'R' | 'D' | undefined) {
  if (party === 'R') return 'var(--party-r)';
  if (party === 'D') return 'var(--party-d)';
  return 'var(--party-none)';
}

export default function CongressionalDistrictImpact({ year = 2026 }: Props) {
  const [data, setData] = useState<NJDistrictData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDistrict, setSelectedDistrict] = useState<string | null>(null);

  useEffect(() => {
    const basePath = process.env.NEXT_PUBLIC_BASE_PATH !== undefined
      ? process.env.NEXT_PUBLIC_BASE_PATH
      : '/us/nj-ctc-increase';

    setLoading(true);
    setError(null);

    fetch(`${basePath}/data/congressional_districts.csv`)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load district data');
        return res.text();
      })
      .then((text) => {
        const lines = text.trim().split(/\r?\n/);
        const headers = lines[0].split(',').map((h) => h.trim());
        const rows = lines.slice(1).map((line) => {
          const values = line.split(',').map((v) => v.trim());
          const row: Record<string, string | number> = {};
          headers.forEach((h, i) => {
            const val = values[i];
            row[h] = isNaN(Number(val)) ? val : Number(val);
          });
          return row as unknown as NJDistrictData & { state: string; year: number };
        });
        const njRows = rows
          .filter((r) => r.state === 'NJ' && r.year === year)
          .map((r) => {
            const districtNum = String(r.district).split('-')[1] || '';
            const districtId = districtNum.replace(/^0+/, '') || districtNum;
            const rep = NJ_REPRESENTATIVES[districtId];
            return {
              ...r,
              district_number: districtId,
              representative: rep?.name || '',
              party: rep?.party,
              region: '',
            } as NJDistrictData;
          })
          .sort((a, b) =>
            Number(a.district_number) - Number(b.district_number)
          );
        setData(njRows);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [year]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary border-r-transparent"></div>
          <p className="mt-4 text-gray-600">Loading New Jersey district data...</p>
        </div>
      </div>
    );
  }

  if (error || data.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h2 className="text-yellow-800 font-semibold mb-2">
          New Jersey district data not yet available
        </h2>
        <p className="text-yellow-700">
          {error || 'NJ district-level impact data has not been generated yet.'}
        </p>
        <p className="text-yellow-700 mt-2">
          Run: <code className="bg-yellow-100 px-2 py-1 rounded">modal run scripts/modal_district_pipeline.py</code>
        </p>
      </div>
    );
  }

  const selectedData = selectedDistrict
    ? data.find((d) => d.district_number === selectedDistrict) || null
    : null;

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold text-gray-900 mb-2">
          New Jersey congressional district impacts ({year})
        </h3>
        <p className="text-gray-600">
          Average household impact by congressional district under the{' '}
          <strong>enacted 25% CTC increase</strong> vs. prior law.
          Hover over a district for details and click to pin.
        </p>
      </div>

      {/* Map */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <NJDistrictMap
          data={data}
          selectedDistrict={selectedDistrict}
          onSelect={(districtNum) =>
            setSelectedDistrict((prev) =>
              prev === districtNum ? null : districtNum
            )
          }
        />
        <ChartWatermark />
      </div>

      {/* Detail card below map */}
      {selectedData ? (
        <DistrictDetailCard
          district={selectedData}
          onClose={() => setSelectedDistrict(null)}
        />
      ) : (
        <div className="bg-gray-50 border border-dashed border-gray-300 rounded-lg p-6 text-center">
          <p className="text-gray-500 text-sm">
            Click a district on the map to see detailed impact analysis.
          </p>
        </div>
      )}

      {/* All districts table */}
      <div>
        <h4 className="text-lg font-semibold text-gray-900 mb-3">
          All New Jersey districts
        </h4>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-900">District</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-900">Representative</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-900">Winners</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-900">Average change</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-900">Child poverty change</th>
              </tr>
            </thead>
            <tbody>
              {data.map((d) => (
                <tr
                  key={d.district_number}
                  className={`border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${
                    selectedDistrict === d.district_number ? 'bg-primary-50' : ''
                  }`}
                  onClick={() =>
                    setSelectedDistrict((prev) =>
                      prev === d.district_number ? null : d.district_number
                    )
                  }
                >
                  <td className="py-3 px-4 text-gray-700 font-medium">
                    NJ-{String(d.district_number).padStart(2, '0')}
                    <span className="block text-xs text-gray-500 font-normal">{d.region}</span>
                  </td>
                  <td className="py-3 px-4" style={{ color: partyColor(d.party) }}>
                    {d.representative}
                    {d.party ? <span className="ml-1 text-xs">({d.party})</span> : null}
                  </td>
                  <td className="py-3 px-4 text-right text-gray-700">
                    {(d.winners_share_residents ?? d.winners_share) !== undefined
                      ? `${((d.winners_share_residents ?? d.winners_share)! * 100).toFixed(1)}%`
                      : '—'}
                  </td>
                  <td className="py-3 px-4 text-right text-gray-700">
                    {d.average_household_income_change >= 0 ? '+' : ''}
                    ${d.average_household_income_change.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                  </td>
                  <td className="py-3 px-4 text-right text-gray-700">
                    {d.child_poverty_pct_change !== undefined
                      ? `${d.child_poverty_pct_change > 0 ? '+' : ''}${d.child_poverty_pct_change.toFixed(2)}%`
                      : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Methodology note */}
      <p className="text-xs text-gray-500">
        Winners are residents whose household&apos;s net income rises,
        matching the statewide tab. District estimates use
        PolicyEngine&apos;s district-calibrated datasets (~9,000 households
        per district), from the same enhanced CPS family as the statewide
        estimates. District figures may not exactly aggregate to statewide
        figures because each district file is calibrated independently.
      </p>
    </div>
  );
}

function DistrictDetailCard({
  district,
  onClose,
}: {
  district: NJDistrictData;
  onClose: () => void;
}) {
  const avgChange = district.average_household_income_change;
  const isPositive = avgChange > 0;
  const isNegative = avgChange < 0;
  const winnersShare =
    district.winners_share_residents ?? district.winners_share ?? 0;
  const losersShare =
    district.losers_share_residents ?? district.losers_share ?? 0;
  // "No change" is the residual after winners + losers.
  const noChangeShare = Math.max(0, 1 - winnersShare - losersShare);
  const childPovChange = district.child_poverty_pct_change ?? 0;

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
      <div className="flex items-start justify-between mb-4 pb-4 border-b border-gray-100">
        <div className="flex items-center gap-3">
          <span
            className="inline-flex items-center justify-center w-10 h-10 rounded-lg text-white font-bold text-lg"
            style={{
              backgroundColor: isPositive
                ? 'var(--chart-1)'
                : isNegative
                  ? 'var(--destructive)'
                  : 'var(--muted-foreground)',
            }}
          >
            {district.district_number}
          </span>
          <div>
            <h4 className="text-lg font-semibold text-gray-900">
              New Jersey District {district.district_number}
            </h4>
            <p className="text-sm text-gray-500">
              <span style={{ color: partyColor(district.party) }}>
                {district.representative}
                {district.party ? ` (${district.party})` : ''}
              </span>
              {district.region ? ` — ${district.region}` : ''}
            </p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 p-1"
          title="Close"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">
            Average household impact
          </p>
          <p
            className={`text-xl font-bold ${
              isPositive ? 'text-primary-700' : isNegative ? 'text-red-700' : 'text-gray-700'
            }`}
          >
            {isPositive ? '+' : ''}
            ${avgChange.toLocaleString('en-US', { maximumFractionDigits: 0 })}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {(district.relative_household_income_change * 100).toFixed(2)}% of income
          </p>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Winners</p>
          <p className="text-xl font-bold text-primary-600">
            {(winnersShare * 100).toFixed(1)}%
          </p>
          <p className="text-xs text-gray-500 mt-1">of residents gain</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Child poverty change</p>
          <p
            className={`text-xl font-bold ${
              childPovChange < 0 ? 'text-primary-700' : childPovChange > 0 ? 'text-red-700' : 'text-gray-700'
            }`}
          >
            {childPovChange > 0 ? '+' : ''}
            {childPovChange.toFixed(2)}%
          </p>
          <p className="text-xs text-gray-500 mt-1">vs. prior law</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">No change</p>
          <p className="text-xl font-bold text-gray-600">
            {(noChangeShare * 100).toFixed(1)}%
          </p>
          <p className="text-xs text-gray-500 mt-1">of residents</p>
        </div>
      </div>
    </div>
  );
}
