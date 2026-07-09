/**
 * Spawn-and-poll client for the Modal household backend
 * (scripts/modal_household_endpoint.py), mirroring CPID's pattern:
 *
 *   POST /household/start          -> { job_id }
 *   GET  /household/status/{id}    -> { status: 'computing' | 'ok' | 'error', result? }
 *
 * The backend pins its own policyengine-us (with the enacted NJ CTC
 * increase), so the household calculator does not depend on what
 * api.policyengine.org has deployed.
 */

export interface HouseholdSweepPayload {
  age_head: number;
  age_spouse: number | null;
  dependent_ages: number[];
  income: number;
  year: number;
  max_earnings: number;
  state_code?: string;
}

export interface HouseholdSweepResult {
  income_range: number[];
  net_income_change: number[];
  nj_income_tax_change: number[];
  income_tax_change: number[];
  benefit_at_income: {
    baseline: number;
    reform: number;
    difference: number;
    federal_tax_change: number;
    state_tax_change: number;
  };
  point: {
    baseline: {
      household_net_income: number;
      nj_income_tax: number;
      income_tax: number;
    };
    reform: {
      household_net_income: number;
      nj_income_tax: number;
      income_tax: number;
    };
  };
  x_axis_max: number;
}

interface StartResponse {
  job_id: string;
}

interface StatusResponse {
  status: 'computing' | 'ok' | 'error';
  result?: HouseholdSweepResult;
  message?: string;
}

const POLL_INTERVAL_MS = 2_000;
// Cold Modal containers pay the policyengine-us import (~1 min) before
// the two-sim sweep, so allow a generous ceiling; warm+cached responses
// return in one or two polls.
const POLL_TIMEOUT_MS = 5 * 60 * 1_000;

function modalBaseUrl(): string {
  const base = process.env.NEXT_PUBLIC_MODAL_NJ_URL;
  if (!base) {
    throw new Error(
      'NEXT_PUBLIC_MODAL_NJ_URL is not set; the household calculator requires the Modal backend.',
    );
  }
  return base.replace(/\/$/, '');
}

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Modal backend error ${res.status}: ${text.slice(0, 300)}`);
  }
  return res.json() as Promise<T>;
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export async function runHouseholdSweep(
  payload: HouseholdSweepPayload,
): Promise<HouseholdSweepResult> {
  const base = modalBaseUrl();
  const { job_id } = await fetchJson<StartResponse>(
    `${base}/household/start`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    },
  );

  const deadline = Date.now() + POLL_TIMEOUT_MS;
  for (;;) {
    const status = await fetchJson<StatusResponse>(
      `${base}/household/status/${encodeURIComponent(job_id)}`,
    );
    if (status.status === 'ok' && status.result) return status.result;
    if (status.status === 'error') {
      throw new Error(status.message || 'Household computation failed.');
    }
    if (Date.now() > deadline) {
      throw new Error('Household computation timed out; please retry.');
    }
    await sleep(POLL_INTERVAL_MS);
  }
}
