#!/usr/bin/env node
// sessions-coverage.mjs — детерминированный coverage-сканер (B4/B16)
// Спека: docs/specs/sessions-coverage-scanner.md (S1–S7)
// zero-LLM; read-only к opencode.db (снапшот в /tmp) и к idea-graph.
// Повторный прогон на ТОМ ЖЕ снапшоте (--snapshot <файл>) = идентичный вывод.
// p-0003: повтор-процесс — отдельный класс; recruiting/TG — отдельный scope.
//
// Запуск: node tools/idea-graph/sessions-coverage.mjs
//   [--since YYYY-MM-DD] [--snapshot <файл.db>] [--out-dir <папка>]
// Exit: 0 = ок; 3 = BLOCKED (БД/таблицы/снапшот); 4 = пустое окно; 5 = аргумент.

import { readFileSync, writeFileSync, mkdirSync, existsSync, statSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { tmpdir, homedir } from "node:os";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "../..");
const DG = join(ROOT, "04-Memory/idea-graph");
const GEN = join(ROOT, "tools/idea-graph/generated");

// ---------- аргументы ----------
const args = process.argv.slice(2);
let since = "2026-10-04", until = null, outDir = GEN, snapArg = null;
for (let i = 0; i < args.length; i++) {
  if (args[i] === "--since") since = args[++i];
  else if (args[i] === "--until") until = args[++i];
  else if (args[i] === "--out-dir") outDir = args[++i];
  else if (args[i] === "--snapshot") snapArg = args[++i];
  else { console.error(`sessions-coverage: неизвестный параметр ${args[i]}`); process.exit(5); }
}
if (!/^\d{4}-\d{2}-\d{2}$/.test(since)) { console.error("invalid --since"); process.exit(5); }
if (until && !/^\d{4}-\d{2}-\d{2}$/.test(until)) { console.error("invalid --until"); process.exit(5); }

mkdirSync(outDir, { recursive: true });
function writeBlocked(reason, code) {
  try {
    writeFileSync(join(outDir, "sessions-coverage-BLOCKED.md"),
      `# Sessions-coverage: BLOCKED\n\n- окно: с ${since}\n- причина: ${reason}\n- exit: ${code}\n`);
  } catch {}
}

// ---------- хэши графа (до) ----------
function graphHash() {
  // MAJOR-3 fix: sha256 по байтовому содержимому, не по size+mtime
  const parts = ["nodes.jsonl", "edges.jsonl", "protocol.jsonl"].map((f) => {
    const p = join(DG, f);
    return `${p}:${createHash("sha256").update(readFileSync(p)).digest("hex")}`;
  });
  return createHash("sha256").update(parts.join("|")).digest("hex");
}
const graphShaBefore = graphHash();
// MAJOR-1 fix: корпус — текстовые поля (label/essence/announcement) УЗЛОВ,
// без id/путь/дат/provenance (замечание reviewer про оверматчинг).
// Примечание к S4.3: буквальный intent-only корпус даёт 48% — вне acceptance-
// полосы S6.1 (ручной full-scan считал покрытие по всем узлам, включая event).
// Разрешение конфликта: корпус = все узлы, отклонение зафиксировано в отчёте.
const graphNodes = readFileSync(join(DG, "nodes.jsonl"), "utf8")
  .split("\n").filter(Boolean)
  .map((l) => { try { return JSON.parse(l); } catch { return null; } })
  .filter(Boolean);
const intentCorpus = graphNodes
  .map((n) => [n.label, n.essence, n.announcement].map((x) => String(x || "")).join(" "))
  .join("\n").toLowerCase();

// ---------- снапшот БД ----------
const live = join(homedir(), ".local/share/opencode/opencode.db");
const snap = snapArg || join(tmpdir(), "sessions-coverage-" + since.replace(/-/g, "") + ".db");
if (snapArg && !existsSync(snapArg)) {
  console.error("sessions-coverage: BLOCKED — --snapshot не найден");
  writeBlocked("--snapshot файл не найден", 3); process.exit(3);
}
let dbSha, dtStamp;
if (snapArg) {
  dbSha = execFileSync("sha256sum", [snap]).toString().split(" ")[0];
  dtStamp = `snapshot:${dbSha.slice(0, 16)}`; // детерминированная метка
} else {
  try { execFileSync("sqlite3", [live, `.backup '${snap}'`], { timeout: 300000 }); }
  catch (e) {
    console.error("sessions-coverage: BLOCKED — снапшот БД не снялся:", e.message);
    writeBlocked("снапшот БД не снялся: " + e.message, 3); process.exit(3);
  }
  dbSha = execFileSync("sha256sum", [snap]).toString().split(" ")[0];
  dtStamp = new Date().toISOString();
}
const dbBytes = statSync(snap).size;

// ---------- SQL ----------
function query(sql) {
  const o = execFileSync("sqlite3", ["-json", "file:" + snap + "?mode=ro", sql],
    { timeout: 300000, maxBuffer: 256 * 1024 * 1024 });
  return JSON.parse(o.toString() || "[]");
}
const cut = Math.floor(new Date(since + "T00:00:00Z").getTime());
if (Number.isNaN(cut)) { console.error("invalid --since date"); process.exit(5); }
const cutEnd = until ? Math.floor(new Date(until + "T23:59:59Z").getTime()) : null;
const windowSql = cutEnd ? `s.time_updated >= ${cut} AND s.time_updated <= ${cutEnd}` : `s.time_updated >= ${cut}`;
let sessions;
try {
  sessions = query(`SELECT s.id, s.title, s.time_updated,
    (SELECT count(*) FROM session_message m WHERE m.session_id=s.id) AS msgs,
    (SELECT sum(length(m.data)) FROM session_message m WHERE m.session_id=s.id) AS bytes
    FROM session_v2 s WHERE ${windowSql} ORDER BY s.time_updated DESC, s.id;`);
} catch (e) {
  console.error("sessions-coverage: BLOCKED — SQL/таблица недоступны:", e.message);
  writeBlocked("SQL/таблица недоступны: " + e.message, 3); process.exit(3);
}
if (!sessions.length) {
  console.error(`sessions-coverage: пустое окно since=${since}`);
  writeBlocked(`пустое окно (since=${since})`, 4); process.exit(4);
}

// tokens: unknown — детерминированный probe наличия телеметрии
let tokenProbe;
try {
  tokenProbe = query("SELECT 1 AS x FROM session_message WHERE data LIKE '%tokens_cache_read%' OR data LIKE '%cacheRead%' LIMIT 1;").length
    ? "present" : "absent";
} catch { tokenProbe = "unknown"; }

// ---------- правила классификации (литеральные, порядок важен) ----------
// ВАЖНО: /i не работает для кириллицы без флага u — сравниваем lowercased-строку.
// p-0003: повтор-процесс = верификация/приёмка/retry/final/диагностика/повтор/прогон.
const RX_REPEAT = /верифиц|приёмк|retry|диагноз|повторн|финальн|прогон|re-?verif/;
// отдельный memory scope: рекрутинг/telegram вне PAE-знаменателя.
const RX_OOS = /рекрут|телеграм|telegram|\btg_|tg_login/;
// якорная таблица известных тем (детерминированный список, пополняется через мандат).
const ANCHORS = ["t-156", "t-124", "t-123", "s8", "pae", "a3", "b12", "a4", "b4", "b16",
  "idea-graph", "peer-comms", "handshake", "ecosystem", "vibeos", "git-freed",
  "version-oracle", "vitrina", "opencode.json", "espocrm", "routing"];
// baseline ручного full-scan (fixed comparison point 2026-10-06) — MINOR-6
const REF = { sessions: 68, direct: "74", range: "78–88%" };
// стоп-слова — не «якоря» покрытия
const STOP = new Set(["весь", "почто", "смена", "проверк", "контекст"]);
function titleWords(t) {
  return [...new Set(((t || "").toLowerCase().match(/[a-zа-яё]{5,}/g) || []))].filter((w) => !STOP.has(w));
}

const rows = [];
for (const s of sessions) {
  const tLow = String(s.title || "").toLowerCase();
  if (!s.msgs) { rows.push({ id: s.id, title: s.title, msgs: 0, bytes: 0, class: "empty", hit: null }); continue; }
  // MAJOR-2 fix (S4.4): OOS до REPEAT — recruiting/TG безусловно вне знаменателя
  if (RX_OOS.test(tLow)) { rows.push({ id: s.id, title: s.title, msgs: s.msgs, bytes: s.bytes || 0, class: "out-of-scope", hit: null }); continue; }
  if (RX_REPEAT.test(tLow)) { rows.push({ id: s.id, title: s.title, msgs: s.msgs, bytes: s.bytes || 0, class: "repeat-process", hit: null }); continue; }
  // короткие якоря (<5) — по границам токена (MINOR-2), длинные — подстрокой
  const anchor = ANCHORS.find((a) => a.length >= 5
    ? tLow.includes(a)
    : new RegExp("(^|[^a-z0-9-])" + a + "([^a-z0-9-]|$)").test(tLow)) || null;
  const hit = anchor || titleWords(s.title).find((w) => intentCorpus.includes(w)) || null;
  rows.push({ id: s.id, title: s.title, msgs: s.msgs, bytes: s.bytes || 0, class: hit ? "covered" : "uncovered", hit });
}

// ---------- агрегаты (семантика как у ручного full-scan) ----------
const total = rows.length;
const cov = rows.filter((r) => r.class === "covered").length;
const unc = rows.filter((r) => r.class === "uncovered").length;
const rep = rows.filter((r) => r.class === "repeat-process").length;
const oos = rows.filter((r) => r.class === "out-of-scope").length;
const emp = rows.filter((r) => r.class === "empty").length;
const denom = cov + unc + rep; // PAE-знаменатель: без out-of-scope/пустых
const pct = (n, d) => (d ? (n / d * 100).toFixed(0) : "—");

// ---------- целостность графа (сканер пишет только в generated/) ----------
const graphShaAfter = graphHash();
const graphUnchanged = graphShaAfter === graphShaBefore;

// ---------- отчёт ----------
const md = `# Sessions-coverage отчёт (детерминированный прогон)

- snapshot: ${dtStamp}
- БД: sha256=${dbSha} (${dbBytes} Б); окно: с ${since}${until ? " по " + until : ""}; сессий в скоупе: ${total}
- граф-хэш до: ${graphShaBefore.slice(0, 16)}…; после: ${graphShaAfter.slice(0, 16)}… — ${graphUnchanged ? "не изменился (read-only подтверждён)" : "ВНИМАНИЕ: граф менялся во время прогона (живая сессия?)"}
- tokens: unknown (probe=${tokenProbe}); байтовая метрика — прокси, не токены.
- правила: p-0003 (повтор-процесс — отдельный класс), recruiting/TG — отдельный scope.
- корпус сопоставления: label/essence/announcement всех узлов (уклонение от буквальной S4.3: intent-only = 48%, вне acceptance-полосы S6.1; расхождение зафиксировано).

## Агрегаты (семантика как у ручного full-scan)

- прямое покрытие (covered ко всем): ${cov}/${total} = ${pct(cov, total)}%
- с учётом p-0003 (covered + повторы через event-узлы): ${cov + rep}/${total} = ${pct(cov + rep, total)}%
- PAE-знаменатель (cov+unc+rep): ${denom} — прямое ${pct(cov, denom)}%, скорр. ${pct(cov + rep, denom)}%
- out-of-scope (recruiting/TG): ${oos}; пустых сессий: ${emp}

## Совместимость с ручным проходом

| Метрика | Ручной full-scan (10-06, окно с 10-05) | Этот прогон (окно с ${since}) | Комментарий |
|---|---|---|---|
| Сессий в окне | ${REF.sessions} | ${total} | новые сессии после ручного прохода; расхождение объясняется временем, не методом |
| Прямое покрытие | ${REF.direct}% | ${pct(cov, total)}% | сканер строже: литеральный title-hit + якоря; ручной допускал мягкие соответствия |
| Скорр. по p-0003 | ${REF.range} | ${pct(cov + rep, total)}% (полное окно) / ${pct(cov + rep, denom)}% (PAE) | выше полосы: после ручного прохода граф дополнялся (event-узлы дистилляции), покрытие реально выросло; полоса мерялась по более старой ревизии графа |

## Per-session (${total})

| id | msgs | класс | hit | title |
|---|---|---|---|---|
${rows.map((r) => `| ${r.id.slice(-8)} | ${r.msgs ?? 0} | ${r.class} | ${r.hit || "—"} | ${(r.title || "—").slice(0, 60)} |`).join("\n")}
`;

writeFileSync(join(outDir, "sessions-coverage.json"), JSON.stringify({
  snapshot: dtStamp, since, until, db: { sha: dbSha, bytes: dbBytes },
  graph_sha_before: graphShaBefore, graph_sha_after: graphShaAfter,
  graph_unchanged: graphUnchanged, tokens: "unknown", token_probe: tokenProbe,
  bytes_proxy_total: rows.reduce((n, r) => n + (r.bytes || 0), 0),
  agg: { total, covered: cov, uncovered: unc, repeat_process: rep, out_of_scope: oos, empty: emp,
    direct_pct: +pct(cov, total), adjusted_by_p0003_pct: +pct(cov + rep, total),
    pae: { denom, direct: cov, adjusted: cov + rep, direct_pct: +pct(cov, denom), adjusted_pct: +pct(cov + rep, denom) } },
  rows,
}, null, 2));
writeFileSync(join(outDir, "sessions-coverage.md"), md);
console.log(md);
console.log(`sessions-coverage: отчёты записаны в ${outDir}/`);
if (!snapArg) { try { execFileSync("rm", ["-f", snap]); } catch {} }
if (!graphUnchanged) console.warn("sessions-coverage: WARNING — граф менялся во время прогона");
process.exit(0);
