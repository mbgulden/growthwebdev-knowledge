#!/usr/bin/env node
/**
 * pull-ga4-gsc.js
 *
 * Active Oahu Tours — GA4 + GSC baseline pull
 * Window: 2026-03-19 → 2026-06-19 (90 days)
 *
 * Prerequisites:
 *   - /home/ubuntu/.config/mcp-gdrive/.gdrive-server-credentials.json
 *     contains a refresh token with scopes:
 *       drive.readonly, spreadsheets, documents, gmail.readonly, drive.file,
 *       webmasters.readonly, analytics.readonly
 *   - npm install googleapis (local or in this directory)
 *
 * Run:
 *   node pull-ga4-gsc.js
 *
 * Outputs:
 *   - ga4-gsc-baseline.md       (human-readable report)
 *   - ga4-gsc-baseline-raw.json (raw API responses, for reproducibility)
 */

const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');

const KEYS_PATH = '/home/ubuntu/.config/mcp-gdrive/gcp-oauth.keys.json';
const CREDS_PATH = '/home/ubuntu/.config/mcp-gdrive/.gdrive-server-credentials.json';
const OUT_DIR = __dirname;
const RAW_PATH = path.join(OUT_DIR, 'ga4-gsc-baseline-raw.json');
const MD_PATH = path.join(OUT_DIR, 'ga4-gsc-baseline.md');

const START = '2026-03-19';
const END = '2026-06-19';
const GSC_SITE_CANDIDATES = [
  'https://activeoahutours.com/',
  'sc-domain:activeoahutours.com',
];

const raw = { generated_at: new Date().toISOString(), window: { start: START, end: END }, results: {} };

function bail(msg, e) {
  console.error('FATAL:', msg);
  if (e) console.error(e.message);
  raw.error = { msg, detail: e?.message };
  fs.writeFileSync(RAW_PATH, JSON.stringify(raw, null, 2));
  process.exit(1);
}

async function fetchAllPages(runner, pageSize = 100000) {
  // GA4 + GSC both return max 100k rows per call. Some endpoints paginate via startRow.
  // Implement generic pagination wrapper.
  const out = [];
  let startRow = 0;
  for (;;) {
    const chunk = await runner(startRow, pageSize);
    if (!chunk) break;
    const rows = chunk.rows || chunk;
    if (!rows || (Array.isArray(rows) && rows.length === 0)) break;
    out.push(...rows);
    if (!Array.isArray(rows) || rows.length < pageSize) break;
    startRow += pageSize;
  }
  return out;
}

(async () => {
  // 1. Auth
  if (!fs.existsSync(KEYS_PATH)) bail('OAuth keys not found: ' + KEYS_PATH);
  if (!fs.existsSync(CREDS_PATH)) bail('Creds not found: ' + CREDS_PATH);
  const keys = JSON.parse(fs.readFileSync(KEYS_PATH)).installed;
  const creds = JSON.parse(fs.readFileSync(CREDS_PATH));
  const oauth2 = new google.auth.OAuth2(keys.client_id, keys.client_secret, 'http://localhost');
  oauth2.setCredentials({ refresh_token: creds.refresh_token });
  const { token } = await oauth2.getAccessToken().catch((e) => bail('refresh failed', e));
  const authHeaders = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
  raw.oauth = { scope: creds.scope, refreshed_at: new Date().toISOString() };

  // 2. Discover GA4 property for activeoahutours.com
  console.log('→ Discovering GA4 property...');
  const acctRes = await fetch('https://analyticsadmin.googleapis.com/v1beta/accountSummaries', { headers: authHeaders });
  if (!acctRes.ok) bail(`GA4 accountSummaries failed: ${acctRes.status}`, { message: await acctRes.text() });
  const acctData = await acctRes.json();
  raw.results.ga4_accountSummaries = acctData;
  let ga4Property = null;
  for (const acct of acctData.accountSummaries || []) {
    for (const p of acct.propertySummaries || []) {
      const pn = (p.property || '').toLowerCase();
      if (pn.includes('activeoahutours') || pn.includes('active-oahu') || pn.includes('activeoahu')) {
        ga4Property = p.property;
        break;
      }
    }
    if (ga4Property) break;
  }
  if (!ga4Property) {
    // Fallback: pick first property; log candidates for manual review
    const all = (acctData.accountSummaries || []).flatMap((a) => (a.propertySummaries || []).map((p) => p.property));
    raw.results.ga4_property_candidates = all;
    if (all.length === 1) ga4Property = all[0];
    else bail('No unambiguous GA4 property for activeoahutours.com', { candidates: all });
  }
  console.log('  GA4 property:', ga4Property);

  // GA4 runReport helper
  const ga4Run = async (body) => {
    const url = `https://analyticsdata.googleapis.com/v1beta/${ga4Property}:runReport`;
    const r = await fetch(url, { method: 'POST', headers: authHeaders, body: JSON.stringify(body) });
    if (!r.ok) bail(`GA4 runReport failed: ${r.status}`, { message: await r.text(), body });
    return r.json();
  };

  const DIM = (d) => ({ name: d });
  const MET = (m) => ({ name: m });

  // 3. GA4 sections
  console.log('→ GA4: top 20 pages by sessions (organic)...');
  raw.results.ga4_top_pages_organic = await ga4Run({
    dateRanges: [{ startDate: START, endDate: END }],
    dimensions: [DIM('pagePath'), DIM('pageTitle')],
    metrics: [MET('sessions'), MET('totalUsers'), MET('engagedSessions'), MET('engagementRate')],
    dimensionFilter: {
      andGroup: { expressions: [{ filter: { fieldName: 'sessionDefaultChannelGroup', stringFilter: { value: 'Organic Search', matchType: 'EXACT' } } }] }
    },
    orderBys: [{ metric: { metricName: 'sessions' }, desc: true }],
    limit: 20,
  });

  console.log('→ GA4: top 10 entry pages + bounce + duration...');
  raw.results.ga4_top_entry_pages = await ga4Run({
    dateRanges: [{ startDate: START, endDate: END }],
    dimensions: [DIM('landingPagePlusQueryString'), DIM('pageTitle')],
    metrics: [MET('sessions'), MET('bounceRate'), MET('averageSessionDuration'), MET('engagedSessions')],
    orderBys: [{ metric: { metricName: 'sessions' }, desc: true }],
    limit: 10,
  });

  console.log('→ GA4: conversion events...');
  const candidateEvents = ['purchase', 'book', 'generate_lead', 'begin_checkout', 'add_to_cart', 'view_item', 'sign_up', 'contact', 'submit_lead_form'];
  const eventResults = {};
  for (const ev of candidateEvents) {
    const r = await ga4Run({
      dateRanges: [{ startDate: START, endDate: END }],
      dimensions: [DIM('eventName')],
      metrics: [MET('eventCount'), MET('sessions'), MET('totalUsers')],
      dimensionFilter: {
        andGroup: { expressions: [{ filter: { fieldName: 'eventName', stringFilter: { value: ev, matchType: 'EXACT' } } }] }
      },
    });
    eventResults[ev] = r;
  }
  raw.results.ga4_event_candidates = eventResults;

  // Discover *all* event names for completeness
  raw.results.ga4_all_events = await ga4Run({
    dateRanges: [{ startDate: START, endDate: END }],
    dimensions: [DIM('eventName')],
    metrics: [MET('eventCount'), MET('sessions'), MET('totalUsers')],
    orderBys: [{ metric: { metricName: 'eventCount' }, desc: true }],
    limit: 50,
  });

  console.log('→ GA4: device breakdown...');
  raw.results.ga4_devices = await ga4Run({
    dateRanges: [{ startDate: START, endDate: END }],
    dimensions: [DIM('deviceCategory')],
    metrics: [MET('sessions'), MET('totalUsers'), MET('engagementRate'), MET('averageSessionDuration')],
    orderBys: [{ metric: { metricName: 'sessions' }, desc: true }],
  });

  console.log('→ GA4: source/medium...');
  raw.results.ga4_source_medium = await ga4Run({
    dateRanges: [{ startDate: START, endDate: END }],
    dimensions: [DIM('sessionSource'), DIM('sessionMedium')],
    metrics: [MET('sessions'), MET('totalUsers'), MET('engagementRate'), MET('conversions')],
    orderBys: [{ metric: { metricName: 'sessions' }, desc: true }],
    limit: 30,
  });

  console.log('→ GA4: landing page funnel (entry → book_click → purchase)...');
  // Identify booking event dynamically from the all-events list
  const allEventsRows = raw.results.ga4_all_events.rows || [];
  const bookingEvent = allEventsRows.find((r) =>
    /book|booking|purchase|reservation|checkout|order|book_now/i.test(r.dimensionValues?.[0]?.value || '')
  )?.dimensionValues?.[0]?.value;
  raw.results.booking_event_detected = bookingEvent || null;
  // Visits to landing pages
  raw.results.ga4_funnel_visits = await ga4Run({
    dateRanges: [{ startDate: START, endDate: END }],
    dimensions: [DIM('landingPagePlusQueryString')],
    metrics: [MET('sessions')],
    orderBys: [{ metric: { metricName: 'sessions' }, desc: true }],
    limit: 25,
  });
  // Book-online click
  if (bookingEvent) {
    raw.results.ga4_funnel_book_click = await ga4Run({
      dateRanges: [{ startDate: START, endDate: END }],
      dimensions: [DIM('landingPagePlusQueryString'), DIM('eventName')],
      metrics: [MET('eventCount')],
      dimensionFilter: {
        andGroup: { expressions: [{ filter: { fieldName: 'eventName', stringFilter: { value: bookingEvent, matchType: 'EXACT' } } }] }
      },
      orderBys: [{ metric: { metricName: 'eventCount' }, desc: true }],
      limit: 25,
    });
  }
  // Booking completed (purchase)
  raw.results.ga4_funnel_purchase = await ga4Run({
    dateRanges: [{ startDate: START, endDate: END }],
    dimensions: [DIM('landingPagePlusQueryString')],
    metrics: [MET('eventCount')],
    dimensionFilter: {
      andGroup: { expressions: [{ filter: { fieldName: 'eventName', stringFilter: { value: 'purchase', matchType: 'EXACT' } } }] }
    },
    orderBys: [{ metric: { metricName: 'eventCount' }, desc: true }],
    limit: 25,
  });

  // 4. Discover GSC site URL
  console.log('→ Discovering GSC site URL...');
  const gscListRes = await fetch('https://www.googleapis.com/webmasters/v3/sites', { headers: authHeaders });
  if (!gscListRes.ok) bail(`GSC sites.list failed: ${gscListRes.status}`, { message: await gscListRes.text() });
  const gscList = await gscListRes.json();
  raw.results.gsc_sites = gscList;
  const gscSiteEntry = (gscList.siteEntry || []).find((s) => s.siteUrl === GSC_SITE_CANDIDATES[0] || s.siteUrl === GSC_SITE_CANDIDATES[1]);
  if (!gscSiteEntry) bail('No GSC entry for activeoahutours.com', { available: gscList.siteEntry });
  const gscSite = gscSiteEntry.siteUrl;
  console.log('  GSC site:', gscSite);

  const gscQuery = async (body) => {
    const url = `https://www.googleapis.com/webmasters/v3/sites/${encodeURIComponent(gscSite)}/searchAnalytics/query`;
    const r = await fetch(url, { method: 'POST', headers: authHeaders, body: JSON.stringify(body) });
    if (!r.ok) bail(`GSC query failed: ${r.status}`, { message: await r.text(), body });
    return r.json();
  };

  console.log('→ GSC: top 50 queries...');
  raw.results.gsc_top_queries = await gscQuery({
    startDate: START, endDate: END, dimensions: ['query'], rowLimit: 50,
  });

  console.log('→ GSC: top 20 pages...');
  raw.results.gsc_top_pages = await gscQuery({
    startDate: START, endDate: END, dimensions: ['page'], rowLimit: 20,
  });

  console.log('→ GSC: device breakdown...');
  raw.results.gsc_devices = await gscQuery({
    startDate: START, endDate: END, dimensions: ['device'], rowLimit: 10,
  });

  console.log('→ GSC: country breakdown (top 10)...');
  raw.results.gsc_countries = await gscQuery({
    startDate: START, endDate: END, dimensions: ['country'], rowLimit: 10,
  });

  console.log('→ GSC: search appearance...');
  raw.results.gsc_appearance = await gscQuery({
    startDate: START, endDate: END, dimensions: ['searchAppearance'], rowLimit: 20,
  });

  // 5. Save raw + emit a placeholder MD
  fs.writeFileSync(RAW_PATH, JSON.stringify(raw, null, 2));
  console.log('✓ Wrote', RAW_PATH);
  console.log('Raw sections written:', Object.keys(raw.results).length);
  console.log('Next step: run `node render-report.js` to produce the human-readable MD.');
  console.log('   (or pass --render to this script to do both in one go)');
})().catch((e) => bail('uncaught', e));
