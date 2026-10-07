#!/usr/bin/env node
// B7 dry-run runner: Maya-lint v2 dictionary + file/git-log scanning of 8 repos.
// Read-only к репозиториям (git ls-files/show HEAD); writes только в out/.
// Детерминирован: фиксированный HEAD, сортировки, без timestamps.
// Термины в отчёте — только коды tNN + external-категория (язык-граница).
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const dictPath = process.argv.includes("--dict") ? process.argv[process.argv.indexOf("--dict") + 1] : "/home/rudra/dotfiles/tools/maya-lint/dictionary.json";
const dict = JSON.parse(readFileSync(dictPath, "utf8"));
const REPOS = [
  "/home/rudra/dotfiles", "/home/rudra/Projects/OpenCode-Vault",
  "/home/rudra/Projects/AndroidOS", "/home/rudra/Projects/ChaT",
  "/home/rudra/Projects/recruiting-hr", "/home/rudra/Projects/dv-hub",
  "/home/rudra/Projects/serp", "/home/rudra/Projects/TradingMind",
].sort();
const EXT = /\.(md|txt|json|jsonc|ya?ml|toml|js|mjs|cjs|ts|tsx|py|sh|zsh|html|css|sql|go|rs|cfg|ini|conf|example)$/i;
const MAXB = 512 * 1024;
const termId = new Map(dict.terms.map((t, i) => [t.phrase, "t" + String(i + 1).padStart(2, "0")]));
const WHITELIST = dict.whitelist || [];
const sha = (s) => createHash("sha256").update(s).digest("hex");
const lineAt = (text, idx) => { let n = 1; for (let i = 0; i < idx; i++) if (text[i] === "\n") n++; return n; };

mkdirSync(join(HERE, "out"), { recursive: true });
const heads = {}, hits = [], scanned = {};
for (const repo of REPOS) {
  heads[repo] = execFileSync("git", ["-C", repo, "rev-parse", "HEAD"], { encoding: "utf8" }).trim();
  let files = [];
  try { files = execFileSync("git", ["-C", repo, "ls-files"], { encoding: "utf8", maxBuffer: 64e6 }).split("\n").filter(Boolean); } catch {}
  files = files.filter((f) => EXT.test(f)).sort();
  let n = 0;
  for (const f of files) {
    let text;
    try {
      const buf = execFileSync("git", ["-C", repo, "show", `HEAD:${f}`], { maxBuffer: MAXB + 4096 });
      if (buf.length > MAXB || buf.includes(0)) continue;
      text = buf.toString("utf8");
    } catch { continue; }
    n++;
    for (const term of dict.terms) {
      const re = new RegExp(term.phrase.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi");
      for (const m of text.matchAll(re)) {
        const label = `${repo}::${f}`;
        if (WHITELIST.some((w) => w.path === label && term.phrase === w.phrase &&
          (!w.fragments || w.fragments.some((fr) => text.toLowerCase().includes(fr.toLowerCase()))))) continue;
        hits.push({ repo, file: f, line: lineAt(text, m.index), term: termId.get(term.phrase), cat: term.external, src: "files" });
      }
    }
  }
  let log = "";
  try { log = execFileSync("git", ["-C", repo, "log", "--color=never", "-200", "--pretty=format:%H%x09%s%n%b"], { encoding: "utf8", maxBuffer: 64e6 }); } catch {}
  for (const term of dict.terms) {
    const re = new RegExp(term.phrase.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi");
    for (const m of log.matchAll(re)) {
      if (WHITELIST.some((w) => w.path === `${repo}::git-log` && term.phrase === w.phrase &&
        (!w.fragments || w.fragments.some((fr) => log.toLowerCase().includes(fr.toLowerCase()))))) continue;
      const commit = (log.slice(0, m.index).split("\n").filter((l) => /^[0-9a-f]{40}\t/.test(l)).pop() || "").slice(0, 12);
      hits.push({ repo, file: "git-log", line: lineAt(log, m.index), term: termId.get(term.phrase), cat: term.external, src: "history", commit });
    }
  }
  scanned[repo] = n;
}
hits.sort((a, b) => a.repo.localeCompare(b.repo) || String(a.file).localeCompare(b.file) || a.line - b.line || a.term.localeCompare(b.term));
const INTERNAL = /(docs\/specs\/maya-lint|tools\/maya-lint|dictionary\.json|02-Methods|04-Memory[\\/]idea-graph|06-Audits|docs\/decisions|(^|\/)tests?(\/|__))/;
for (const h of hits) h.bucket = h.src === "history" ? "history" : INTERNAL.test(h.file) ? "internal-infra" : "live";

const buckets = {
  live: hits.filter((h) => h.bucket === "live").length,
  history: hits.filter((h) => h.bucket === "history").length,
  internal_infra: hits.filter((h) => h.bucket === "internal-infra").length,
  total: hits.length,
};
const outJson = { dict_version: dict.version, dict_sha: sha(readFileSync(dictPath, "utf8")), heads, scanned, buckets, hits };
writeFileSync(join(HERE, "out", "maya-boundary.json"), JSON.stringify(outJson, null, 2));

let md = `# B7: Maya-lint v2 dry-run — 8 репо (report-mode, координаты+категории)

- dict v${dict.version} sha=${outJson.dict_sha.slice(0, 16)}…
- HEAD: ${REPOS.map((r) => `${r.split("/").pop()}@${heads[r].slice(0, 7)}`).join(", ")}
- источник: файлы из HEAD (текстовые ≤512КБ) + git-log -200; whitelist словаря применён

## Итог по репо

| Репо | файлов | live | history | internal |
|---|---|---|---|---|
`;
for (const r of REPOS) {
  const h = hits.filter((x) => x.repo === r);
  md += `| ${r.split("/").pop()} | ${scanned[r]} | ${h.filter((x) => x.bucket === "live").length} | ${h.filter((x) => x.bucket === "history").length} | ${h.filter((x) => x.bucket === "internal-infra").length} |\n`;
}
const carry = new Set(hits.map((h) => h.file).filter((f) => dict.terms.some((x) => f.toLowerCase().includes(x.phrase.toLowerCase()))));
md += `\nNon-whitelisted hits: ${buckets.total} (live=${buckets.live}, history=${buckets.history}, internal=${buckets.internal_infra})\n- отдельный finding: путей-носителей термина в координатах: ${carry.size} — сами имена файлов несут термин (переименование — зона проектных пайплайнов, сканер путей не чинит)\n\n## FP-корзина (history+internal — в 2-недельный дайджест перед гейтом)\n\n| bucket | репо | файл:строка | терм | категория |\n|---|---|---|---|---|\n`;
for (const h of hits.filter((x) => x.bucket !== "live")) md += `| ${h.bucket} | ${h.repo.split("/").pop()} | ${h.file}:${h.line} | ${h.term} | ${h.cat} |\n`;
md += `\n## Live-нарушения границы (кандидаты на фикс через проектные пайплайны)\n\n| репо | файл:строка | коммит | терм | категория |\n|---|---|---|---|---|\n`;
for (const h of hits.filter((x) => x.bucket === "live")) md += `| ${h.repo.split("/").pop()} | ${h.file}:${h.line} | ${h.commit || "—"} | ${h.term} | ${h.cat} |\n`;
writeFileSync(join(HERE, "out", "maya-boundary.md"), md);
console.log(`TOTAL ${buckets.total} live=${buckets.live} history=${buckets.history} internal=${buckets.internal_infra}`);
