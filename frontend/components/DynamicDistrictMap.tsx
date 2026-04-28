'use client';

// The NJ map is rendered from the bundled congressional_districts.geojson
// with no browser-only deps, so we re-export the component directly.
export { default } from './USDistrictChoroplethMap';
export type { NJDistrictData } from './USDistrictChoroplethMap';
