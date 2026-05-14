// workers/_shared/auth-cross-write.test.js
//
// Day 2 BUILD Track C test runner.
// Invokes the in-module _tests() suite against a synthetic mock env
// and prints a PASS/FAIL line per case. Exits 0 on all-pass, 1 otherwise.
//
// Track D's readout script may also invoke _tests() directly via
// dynamic import; this file is the standalone CLI form.
//
// Usage:
//   node workers/_shared/auth-cross-write.test.js
//
// Node 18+. No external deps. Uses global fetch / Request / Response.

import { _tests } from "./auth-cross-write.js";

const result = await _tests();

console.log("");
console.log("auth-cross-write.js — synthetic mock test results");
console.log("==================================================");
for (const c of result.cases) {
  const tag = c.ok ? "PASS" : "FAIL";
  console.log(`  [${tag}] ${c.name}` + (c.ok ? "" : `  -- ${c.detail || ""}`));
}
console.log("--------------------------------------------------");
console.log(`  passed: ${result.passed}`);
console.log(`  failed: ${result.failed}`);
console.log(`  total:  ${result.passed + result.failed}`);
console.log("==================================================");

process.exit(result.failed === 0 ? 0 : 1);
