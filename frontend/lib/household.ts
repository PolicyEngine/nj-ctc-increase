/**
 * Build a PolicyEngine household situation for the PE API.
 *
 * For the enacted NJ CTC increase dashboard (S-4531 / P.L.2026, c.26):
 * - Current law on the PE API already includes the enacted 25% bracket
 *   increase for 2026-2028, so it plays the "reform" role.
 * - The "baseline" applies the prior-law counterfactual (pre-increase
 *   bracket amounts restored for 2026-2028), so the household calculator
 *   shows impact = current law - prior law (positive = household gains
 *   from the enacted increase).
 */

import type { HouseholdRequest } from "./types";

const GROUP_UNITS = ["families", "spm_units", "tax_units", "households"] as const;

/**
 * Prior-law counterfactual policy parameters for the PE API.
 * Mirrors reform_prior_law.json so the household calculator ships the
 * policy with the bundle. 2029+ needs no override because current law
 * reverts to these amounts on its own.
 */
const PRIOR_LAW_POLICY: Record<string, Record<string, number>> = {
  "gov.states.nj.tax.income.credits.ctc.amount[0].amount": {
    "2026-01-01.2028-12-31": 1000,
  },
  "gov.states.nj.tax.income.credits.ctc.amount[1].amount": {
    "2026-01-01.2028-12-31": 800,
  },
  "gov.states.nj.tax.income.credits.ctc.amount[2].amount": {
    "2026-01-01.2028-12-31": 600,
  },
  "gov.states.nj.tax.income.credits.ctc.amount[3].amount": {
    "2026-01-01.2028-12-31": 400,
  },
  "gov.states.nj.tax.income.credits.ctc.amount[4].amount": {
    "2026-01-01.2028-12-31": 200,
  },
};

function addMemberToUnits(
  situation: Record<string, unknown>,
  memberId: string
): void {
  for (const unit of GROUP_UNITS) {
    const unitObj = situation[unit] as Record<string, { members: string[] }>;
    const key = Object.keys(unitObj)[0];
    unitObj[key].members.push(memberId);
  }
}

export function buildHouseholdSituation(
  params: HouseholdRequest
): Record<string, unknown> {
  const {
    age_head,
    age_spouse,
    dependent_ages,
    income,
    year,
    max_earnings,
    state_code,
  } = params;
  const effectiveStateCode = state_code || "NJ";
  const yearStr = String(year);
  const axisMax = Math.max(max_earnings, income);

  const situation: Record<string, unknown> = {
    people: {
      you: {
        age: { [yearStr]: age_head },
        employment_income: { [yearStr]: null },
      },
    },
    families: { "your family": { members: ["you"] } },
    marital_units: { "your marital unit": { members: ["you"] } },
    spm_units: { "your household": { members: ["you"] } },
    tax_units: {
      "your tax unit": {
        members: ["you"],
        adjusted_gross_income: { [yearStr]: null },
        income_tax: { [yearStr]: null },
        nj_income_tax: { [yearStr]: null },
      },
    },
    households: {
      "your household": {
        members: ["you"],
        state_code: { [yearStr]: effectiveStateCode },
        household_net_income: { [yearStr]: null },
      },
    },
    axes: [
      [
        {
          name: "employment_income",
          min: 0,
          max: axisMax,
          count: Math.min(4001, Math.max(501, Math.floor(axisMax / 500))),
          period: yearStr,
          target: "person",
        },
      ],
    ],
  };

  if (age_spouse != null) {
    const people = situation.people as Record<string, Record<string, unknown>>;
    people["your partner"] = { age: { [yearStr]: age_spouse } };
    addMemberToUnits(situation, "your partner");
    const maritalUnits = situation.marital_units as Record<string, { members: string[] }>;
    maritalUnits["your marital unit"].members.push("your partner");
  }

  for (let i = 0; i < dependent_ages.length; i++) {
    const childId =
      i === 0
        ? "your first dependent"
        : i === 1
          ? "your second dependent"
          : `dependent_${i + 1}`;

    const people = situation.people as Record<string, Record<string, unknown>>;
    people[childId] = { age: { [yearStr]: dependent_ages[i] } };
    addMemberToUnits(situation, childId);
    const maritalUnits = situation.marital_units as Record<string, { members: string[] }>;
    maritalUnits[`${childId}'s marital unit`] = {
      members: [childId],
    };
  }

  return situation;
}

/**
 * Build the prior-law counterfactual policy dict for the PE API.
 * Used by the household calculator to compute:
 *   impact = current law (enacted increase) - prior law (this policy)
 */
export function buildPriorLawPolicy(): Record<string, Record<string, number>> {
  return PRIOR_LAW_POLICY;
}

/**
 * Linear interpolation helper - find the value at `x` in sorted arrays.
 */
export function interpolate(
  xs: number[],
  ys: number[],
  x: number
): number {
  if (x <= xs[0]) return ys[0];
  if (x >= xs[xs.length - 1]) return ys[ys.length - 1];
  for (let i = 1; i < xs.length; i++) {
    if (xs[i] >= x) {
      const t = (x - xs[i - 1]) / (xs[i] - xs[i - 1]);
      return ys[i - 1] + t * (ys[i] - ys[i - 1]);
    }
  }
  return ys[ys.length - 1];
}
