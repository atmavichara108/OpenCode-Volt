#!/usr/bin/env node
// xp-ledger validator (сцена «Сила мира», закон 4).
// Правила: (1) запись без непустого evidence недействительна (ERROR);
// (2) повтор task_id+action+verdict = ноль начислений (WARN duplicate-of, не ERROR);
// (3) инструмент НЕ присуждает награду — только проверяет журнал.
// Usage: node tools/xp/validate.mjs [path-to-ledger]  (default: control-plane/telemetry/xp-ledger.jsonl)
import { readFileSync } from "node:fs";
const path = process.argv[2] ?? "control-plane/telemetry/xp-ledger.jsonl";
let lines = [];
try { lines = readFileSync(path, "utf8").split("\n").filter((l) => l.trim()); }
catch { console.log(`ledger: ${path} (не найден — пусто, PASS)`); process.exit(0); }
const errors = [], warnings = [];
const seen = new Map();
let counted = 0;
for (const [i, line] of lines.entries()) {
  const ln = i + 1;
  let r;
  try { r = JSON.parse(line); } catch { errors.push(`${ln}: bad json`); continue; }
  for (const f of ["ts", "task_id", "kind", "amount"]) {
    if (r[f] === undefined) errors.push(`${ln}: missing ${f}`);
  }
  if (r.kind && !["xp", "coins"].includes(r.kind)) errors.push(`${ln}: unknown kind "${r.kind}"`);
  if (r.amount !== undefined && !(typeof r.amount === "number" && r.amount > 0)) errors.push(`${ln}: amount must be >0`);
  const ev = r.evidence;
  if (!ev || typeof ev !== "object" || Array.isArray(ev) || Object.keys(ev).length === 0) {
    errors.push(`${ln}: evidence missing/empty — запись недействительна`);
    continue;
  }
  if (!ev.audit_action || !ev.verifier_verdict) {
    errors.push(`${ln}: evidence неполный (нужны audit_action + verifier_verdict)`);
    continue;
  }
  const fp = `${r.task_id}|${ev.audit_action}|${ev.verifier_verdict}`;
  if (seen.has(fp)) { warnings.push(`duplicate-of:${seen.get(fp)} zero-accrual (fp=${fp})`); continue; }
  seen.set(fp, ln); counted += Number(r.amount) || 0;
}
console.log(`xp-ledger: ${lines.length} записей, начислено ${counted} (после анти-фарм дедупликации)`);
if (warnings.length) { console.log(`WARNINGS (${warnings.length}):`); warnings.forEach((w) => console.log(`  ! ${w}`)); }
if (errors.length) { console.log(`ERRORS (${errors.length}):`); errors.forEach((e) => console.log(`  ✗ ${e}`)); console.log("FAIL"); process.exit(1); }
console.log("PASS");
