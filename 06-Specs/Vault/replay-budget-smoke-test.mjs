#!/usr/bin/env node
// Smoke test: replay-budget pure helpers (T-135 порт M Code replay budget).
// Tests: truncateToolOutput (head/tail + marker), pruneToolInput (keep-поля,
// ограничение глубины), image budget, protected budget, reasoning drop.
// No live OpenCode runtime required — imports the actual plugin helpers.

import { strict as assert } from "assert"
import { createRequire } from "module"
import { fileURLToPath } from "url"
import { dirname, join } from "path"

const require = createRequire(import.meta.url)
const here = dirname(fileURLToPath(import.meta.url))

// Плагин лежит в dotfiles canonical: ~/dotfiles/opencode-global/.config/opencode/plugins/
const helpersPath = join(
  here, "..", "..", "..", "..", "dotfiles",
  "opencode-global", ".config", "opencode", "plugins", "replay-budget-helpers.js",
)
const {
  TOOL_OUTPUT_MAX_CHARS,
  REPLAY_PROTECTED_CHARS,
  PRUNED_INPUT_MIN_CHARS,
  IMAGE_BUDGET,
  truncateToolOutput,
  pruneToolInput,
  clearImagePart,
  applyReplayBudget,
} = require(helpersPath)

let passed = 0
let failed = 0

function test(name, fn) {
  try {
    fn()
    console.log(`✓ ${name}`)
    passed++
  } catch (err) {
    console.error(`✗ ${name}`)
    console.error(`  ${err.message}`)
    failed++
  }
}

// --- constants mirror M Code ---
test("constants match M Code app.asar", () => {
  assert.equal(TOOL_OUTPUT_MAX_CHARS, 2000)
  assert.equal(REPLAY_PROTECTED_CHARS, 40000)
  assert.equal(PRUNED_INPUT_MIN_CHARS, 120)
  assert.equal(IMAGE_BUDGET, 5)
})

// --- truncateToolOutput ---
test("truncate: short text untouched", () => {
  const s = "short"
  assert.equal(truncateToolOutput(s), s)
})

test("truncate: long text → head75 + marker + tail25", () => {
  const s = "a".repeat(4000)
  const out = truncateToolOutput(s)
  const headChars = Math.floor(2000 * 0.75) // 1500
  const tailChars = 2000 - headChars // 500
  assert.ok(out.startsWith("a".repeat(headChars)))
  assert.ok(out.endsWith("a".repeat(tailChars)))
  assert.match(out, /\[mcode: replay budget — omitted 2000 chars/)
  assert.ok(out.length < 3000) // вмещает маркер
})

test("truncate: marker честно показывает omitted count", () => {
  const out = truncateToolOutput("a".repeat(5000))
  // 5000 - 1500 - 500 = 3000 omitted
  assert.match(out, /omitted 3000 chars/)
})

// --- pruneToolInput ---
test("prune: длинное поле режется", () => {
  const input = { secret: "y".repeat(200), note: "short" }
  pruneToolInput(input)
  assert.equal(input.secret, "[200 characters cleared]")
  assert.equal(input.note, "short")
})

test("prune: keep-поле переживает", () => {
  const input = { filePath: "f".repeat(500) }
  pruneToolInput(input)
  assert.equal(input.filePath, "f".repeat(500))
})

test("prune: вложенные объекты и массивы", () => {
  const input = { args: [{ cmd: "c".repeat(300) }] }
  pruneToolInput(input)
  assert.equal(input.args[0].cmd, "[300 characters cleared]")
})

test("prune: не-строки и null безопасны", () => {
  const input = { n: 42, b: true, x: null }
  pruneToolInput(input)
  assert.equal(input.n, 42)
  assert.equal(input.b, true)
  assert.equal(input.x, null)
})

// --- clearImagePart ---
test("clear image: file part → text маркер", () => {
  const part = { type: "file", mime: "image/png", url: "u", filename: "f" }
  clearImagePart(part)
  assert.equal(part.type, "text")
  assert.equal(part.url, undefined)
  assert.match(part.text, /Image omitted/)
})

// --- applyReplayBudget orchestration ---
test("protected budget: последние 40KB не режутся", () => {
  const big = "b".repeat(2000)
  // два tool-результата по 1000 симв → под 40KB, не режутся
  const messages = [
    { info: { role: "user" }, parts: [] },
    { info: { role: "assistant" }, parts: [] },
    {
      info: { role: "assistant" },
      parts: [
        { type: "tool", state: { status: "completed", input: {}, output: "x".repeat(1000), time: {} } },
        { type: "tool", state: { status: "completed", input: {}, output: "y".repeat(1000), time: {} } },
      ],
    },
  ]
  applyReplayBudget(messages)
  assert.equal(messages[2].parts[0].state.output.length, 1000)
  assert.equal(messages[2].parts[1].state.output.length, 1000)
})

test("old tool output beyond budget → capped", () => {
  // 40KB защитный бюджет + ещё 5000 симв превышают лимит → старый режется.
  // Один output 50000 > бюджет тратится целиком на последний (это текущий ход —
  // semantics защиты последнего, не капится), поэтому бьём двумя: старый + текущий.
  const messages = [
    {
      info: { role: "assistant" },
      parts: [
        { type: "tool", state: { status: "completed", input: {}, output: "o".repeat(50000), time: {} } },
      ],
    },
    {
      info: { role: "user" },
      parts: [],
    },
    {
      info: { role: "assistant" },
      parts: [
        { type: "tool", state: { status: "completed", input: {}, output: "n".repeat(50000), time: {} } },
      ],
    },
  ]
  applyReplayBudget(messages)
  const older = messages[0].parts[0].state.output
  const current = messages[2].parts[0].state.output
  assert.ok(older.length < 3000) // старый капнут до 2000 + маркер
  assert.match(older, /omitted/)
  assert.equal(current.length, 50000) // текущий защищён бюджетом
})

test("reasoning старых ходов дропается, текущий — живёт", () => {
  const messages = [
    { info: { role: "assistant" }, parts: [{ type: "reasoning", text: "old-think" }] },
    { info: { role: "user" }, parts: [] },
    { info: { role: "assistant" }, parts: [{ type: "reasoning", text: "new-think" }] },
  ]
  applyReplayBudget(messages)
  assert.equal(messages[0].parts[0].text, "")
  assert.equal(messages[2].parts[0].text, "new-think")
})

test("image budget: >5 картинок гасятся", () => {
  const parts = Array.from({ length: 7 }, () => ({ type: "file", mime: "image/png", url: "u" }))
  const messages = [{ info: { role: "user" }, parts }]
  applyReplayBudget(messages)
  const stillImages = messages[0].parts.filter((p) => p.type === "file").length
  const cleared = messages[0].parts.filter((p) => p.type === "text").length
  assert.equal(stillImages, 5)
  assert.equal(cleared, 2)
})

test("пустой/неполный input безопасен", () => {
  assert.doesNotThrow(() => applyReplayBudget(undefined))
  assert.doesNotThrow(() => applyReplayBudget(null))
  assert.doesNotThrow(() => applyReplayBudget([{}]))
})

// Summary
console.log(`\n${passed} passed, ${failed} failed`)
console.log(`\nNote: smoke test imports the actual plugin helpers (replay-budget-helpers.js),`)
console.log(`testing real port-логику, not a copy. Hook wiring проверяется в live-сессии TUI.`)
process.exit(failed > 0 ? 1 : 0)