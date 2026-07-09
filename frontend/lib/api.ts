/**
 * Household impact via the Modal household backend
 * (scripts/modal_household_endpoint.py), which pins the same
 * policyengine-us as the data pipelines. The backend runs two
 * simulations per request — prior law (the pre-increase NJ CTC
 * bracket amounts restored for 2026-2028) and plain current law
 * (which includes the enacted 25% increase from S-4531 / P.L.2026,
 * c.26) — and returns the sweep plus point values:
 *
 *   impact = current law (enacted increase) - prior law (counterfactual)
 *
 * which is positive when the household gains from the enacted increase.
 */

import {
  HouseholdRequest,
  HouseholdImpactResponse,
} from "./types";
import { runHouseholdSweep } from "./modalApi";

export const api = {
  async calculateHouseholdImpact(
    request: HouseholdRequest,
  ): Promise<HouseholdImpactResponse> {
    const result = await runHouseholdSweep({
      age_head: request.age_head,
      age_spouse: request.age_spouse,
      dependent_ages: request.dependent_ages,
      income: request.income,
      year: request.year,
      max_earnings: request.max_earnings,
      state_code: request.state_code || "NJ",
    });

    return {
      income_range: result.income_range,
      net_income_change: result.net_income_change,
      federalTaxChange: result.income_tax_change,
      stateTaxChange: result.nj_income_tax_change,
      netIncomeChange: result.net_income_change,
      benefit_at_income: {
        baseline: result.benefit_at_income.baseline,
        reform: result.benefit_at_income.reform,
        difference: result.benefit_at_income.difference,
        federal_tax_change: result.benefit_at_income.federal_tax_change,
        state_tax_change: result.benefit_at_income.state_tax_change,
        net_income_change: result.benefit_at_income.difference,
      },
      x_axis_max: request.max_earnings,
    };
  },
};
