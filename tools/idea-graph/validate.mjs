#!/usr/bin/env node
// idea-graph v2 validator — контракт: docs/specs/idea-graph-v2.md
// Запуск: node tools/idea-graph/validate.mjs   (exit 0 = PASS)

import { readFileSync, existsSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const argvPath = process.argv[2];
const isProd = argvPath === undefined;
const DIR = isProd ? join(ROOT, "04-Memory/idea-graph") : resolve(process.cwd(), argvPath);

const GRAPHS = new Set(["world", "organ", "mech", "tech", "proto", "event", "quest", "stream"]);
const EDGE_TYPES = new Set([
  // структурные
  "belongs_to", "contains", "depends_on",
  // эпистемические
  "refines", "generalizes", "follows_from", "prerequisite_for",
  "example_of", "contradicts", "related",
  // эволюционные
  "inspires", "evolves_into", "devours", "synthesizes", "names",
  // событийные
  "announces", "gates",
]);
const STATUSES = new Set(["raw", "candidate", "accepted", "implemented"]);

const errors = [];
const warnings = [];

function loadJsonl(file, required = isProd) {
  const path = isProd ? join(DIR, file) : file;
  if (!existsSync(path)) {
    if (required) errors.push(`MISSING file: ${path}`);
    return [];
  }
  const out = [];
  const lines = readFileSync(path, "utf8").split("\n");
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    try {
      out.push({ line: i + 1, obj: JSON.parse(line) });
    } catch (e) {
      errors.push(`${file}:${i + 1} JSON parse error: ${e.message}`);
    }
  }
  return out;
}

function requireFields(file, entry, fields) {
  for (const f of fields) {
    if (entry.obj[f] === undefined || entry.obj[f] === null || entry.obj[f] === "") {
      errors.push(`${file}:${entry.line} missing required field "${f}" (id=${entry.obj.id ?? "?"})`);
    }
  }
}

// --- загрузка ---
import { readdirSync } from "node:fs";

function listSandboxJsonl() {
  try {
    if (statSync(DIR).isFile()) return DIR.endsWith(".jsonl") ? [DIR] : [];
    return readdirSync(DIR)
      .filter((f) => f.endsWith(".jsonl"))
      .map((f) => join(DIR, f));
  } catch {
    return [];
  }
}

const nodes = [];
const edges = [];
const protocol = [];

if (isProd) {
  for (const n of loadJsonl("nodes.jsonl")) nodes.push({ file: "nodes.jsonl", ...n });
  for (const e of loadJsonl("edges.jsonl")) edges.push({ file: "edges.jsonl", ...e });
  for (const p of loadJsonl("protocol.jsonl")) protocol.push({ file: "protocol.jsonl", ...p });
} else {
  // Песочница: каталог даёт все *.jsonl, файл — только сам файл.
  // Класс записи определяется содержимым, а не именем файла.
  const files = listSandboxJsonl();
  if (files.length === 0) errors.push(`MISSING jsonl files in sandbox: ${DIR}`);
  for (const f of files) {
    const recs = loadJsonl(f, true).map((r) => ({ file: f, ...r }));
    for (const rec of recs) {
      if (Object.prototype.hasOwnProperty.call(rec.obj, "from") ||
          Object.prototype.hasOwnProperty.call(rec.obj, "to")) {
        edges.push(rec);
      } else {
        nodes.push(rec);
      }
    }
  }
}

const fname = (file, fallback) => (file ?? fallback);

// --- узлы ---
const nodeById = new Map();
for (const n of nodes) {
  requireFields(fname(n.file, "nodes.jsonl"), n, ["id", "graph", "kind", "label", "status", "provenance", "projection"]);
  const id = n.obj.id;
  if (id === undefined) continue;
  if (nodeById.has(id)) errors.push(`${n.file}:${n.line} duplicate node id: ${id}`);
  nodeById.set(id, n.obj);
  if (n.obj.graph !== undefined && !GRAPHS.has(n.obj.graph)) {
    errors.push(`${n.file}:${n.line} unknown graph "${n.obj.graph}" (id=${id})`);
  }
  if (n.obj.status !== undefined && !STATUSES.has(n.obj.status)) {
    errors.push(`${n.file}:${n.line} unknown status "${n.obj.status}" (id=${id})`);
  }
  if (n.obj.provenance && (!n.obj.provenance.source || !n.obj.provenance.observed_at)) {
    errors.push(`${n.file}:${n.line} provenance incomplete (id=${id})`);
  }
  // Голос Мира (закон 2): объявление допустимо только о доказанном.
  if (n.obj.announcement === true && n.obj.status !== "accepted") {
    warnings.push(`announce-on-unaccepted:${id} (status=${n.obj.status})`);
  }
}

// --- рёбра ---
const edgeIds = new Set();
let relatedCount = 0;
for (const e of edges) {
  requireFields(fname(e.file, "edges.jsonl"), e, ["id", "graph", "from", "to", "type", "status", "provenance"]);
  const { id, from, to, type } = e.obj;
  if (id === undefined) continue;
  if (edgeIds.has(id)) errors.push(`${e.file}:${e.line} duplicate edge id: ${id}`);
  edgeIds.add(id);
  if (!EDGE_TYPES.has(type)) errors.push(`${e.file}:${e.line} unknown edge type "${type}" (id=${id})`);
  if (type === "related") relatedCount++;
  const fn = nodeById.get(from);
  const tn = nodeById.get(to);
  if (from !== undefined && !fn) errors.push(`${e.file}:${e.line} dangling from: ${from} (id=${id})`);
  if (to !== undefined && !tn) errors.push(`${e.file}:${e.line} dangling to: ${to} (id=${id})`);
  if (fn && fn.external !== true && e.obj.graph !== fn.graph) {
    errors.push(`${e.file}:${e.line} graph mismatch: edge.graph=${e.obj.graph} vs from-node graph=${fn.graph} (id=${id})`);
  }
}

// --- protocol ---
for (const p of protocol) {
  requireFields(fname(p.file, "protocol.jsonl"), p, ["id", "kind", "status", "provenance"]);
}

// --- пороги v2 (S-приёмка) ---
if (isProd) {
  if (nodeById.size < 90) errors.push(`nodes count ${nodeById.size} < 90 (spec acceptance)`);
  if (edgeIds.size < 120) errors.push(`edges count ${edgeIds.size} < 120 (spec acceptance)`);
  const graphsUsed = new Set([...nodeById.values()].map((n) => n.graph));
  for (const g of ["world", "organ", "mech", "tech", "proto", "event", "quest", "stream"]) {
    if (!graphsUsed.has(g)) errors.push(`graph "${g}" has no nodes`);
  }
  if (edges.length > 0) {
    const share = relatedCount / edges.length;
    if (share > 0.4) errors.push(`"related" share ${(share * 100).toFixed(1)}% > 40% — дисциплина typed edges нарушена`);
  }

  // --- архив эпохи v1 ---
  if (!existsSync(join(DIR, "archive/v1-2026-10-04/nodes.jsonl"))) {
    errors.push("archive/v1-2026-10-04/nodes.jsonl missing — эпоха v1 не заархивирована");
  }
  if (!existsSync(join(ROOT, "docs/specs/idea-graph-v2.md"))) {
    errors.push("docs/specs/idea-graph-v2.md missing");
  }
}

// --- сводка ---
const byGraph = {};
const byStatus = {};
for (const n of nodeById.values()) {
  byGraph[n.graph] = (byGraph[n.graph] || 0) + 1;
  byStatus[n.status] = (byStatus[n.status] || 0) + 1;
}
const typeCounts = {};
for (const e of edges) {
  if (!e.obj.type) continue;
  typeCounts[e.obj.type] = (typeCounts[e.obj.type] || 0) + 1;
}

console.log("=== idea-graph v2 validation ===");
if (!isProd) {
  console.log(`MODE: sandbox (${DIR}) — прод-пороги не применяются`);
}
console.log(`nodes: ${nodeById.size}   edges: ${edgeIds.size}   protocol: ${protocol.length}`);
console.log(`by graph:  ${JSON.stringify(byGraph)}`);
console.log(`by status: ${JSON.stringify(byStatus)}`);
console.log(`edge types: ${JSON.stringify(typeCounts)}`);
if (warnings.length) {
  console.log(`\nWARNINGS (${warnings.length}):`);
  for (const w of warnings) console.log(`  ! ${w}`);
}
if (errors.length) {
  console.log(`\nERRORS (${errors.length}):`);
  for (const err of errors) console.log(`  x ${err}`);
  console.log("\nFAIL");
  process.exit(1);
}
console.log("\nPASS");
process.exit(0);
