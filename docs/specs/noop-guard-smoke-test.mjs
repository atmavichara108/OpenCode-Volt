#!/usr/bin/env node
// Smoke test: no-op turn guard pure helpers (T-136 порт M Code no-op guard).
// Tests: countOutputTokens (текст), hasToolActivity, isNoOpTurn (порог 200),
// buildNudgeParts, retry-limit константы.
// No live OpenCode runtime required — imports the actual plugin helpers.

import { strict as assert } from "assert"
import { createRequire } from "module"
import { fileURLToPath } from "url"
import { dirname, join } from "path"

const require = createRequire(import.meta.url)
const here = dirname(fileURLToPath(import.meta.url))

const helpersPath = join(
  here, "..", "..", "..", "..", "dotfiles",
  "opencode-global", ".config", "opencode", "plugins", "noop-guard-helpers.js",
)
const {
  NO_OP_OUTPUT_THRESHOLD,
  NO_OP_RETRY_LIMIT,
  NO_OP_NUDGE,
  countOutputTokens,
  hasToolActivity,
  isNoOpTurn,
  buildNudgeParts,
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

// --- константы M Code ---
test("constants match M Code no-op guard", () => {
  assert.equal(NO_OP_OUTPUT_THRESHOLD, 200)
  assert.equal(NO_OP_RETRY_LIMIT, 3)
  assert.match(NO_OP_NUDGE, /one sentence/)
})

// --- countOutputTokens ---
test("countOutputTokens: только text-части, 1 tok ≈ 4 симв", () => {
  const parts = [
    { type: "text", text: "a".repeat(400) }, // 100 tokens
    { type: "reasoning", text: "b".repeat(400) }, // не считаем
    { type: "tool", state: {} },
  ]
  assert.equal(countOutputTokens(parts), 100)
})

test("countOutputTokens: пустой/неполный безопасен", () => {
  assert.equal(countOutputTokens([]), 0)
  assert.equal(countOutputTokens(undefined), 0)
})

// --- hasToolActivity ---
test("hasToolActivity: tool-часть = деятельность", () => {
  assert.equal(hasToolActivity([{ type: "tool" }]), true)
  assert.equal(hasToolActivity([{ type: "text" }]), false)
  assert.equal(hasToolActivity([]), false)
})

// --- isNoOpTurn ---
test("isNoOpTurn: без тула + <200 токенов → no-op", () => {
  // 100 симв. текста = 25 токенов < 200
  assert.equal(isNoOpTurn([{ type: "text", text: "x".repeat(100) }]), true)
})

test("isNoOpTurn: пустой assistant (0 токенов) → no-op", () => {
  assert.equal(isNoOpTurn([]), true)
})

test("isNoOpTurn: есть тул → работа, не no-op", () => {
  assert.equal(isNoOpTurn([{ type: "tool", state: {} }]), false)
})

test("isNoOpTurn: много текста (>=200 токенов) → не no-op", () => {
  // 800 симв. текста = 200 токенов
  assert.equal(isNoOpTurn([{ type: "text", text: "x".repeat(800) }]), false)
})

// --- buildNudgeParts ---
test("buildNudgeParts: synthetic user text part", () => {
  const parts = buildNudgeParts()
  assert.equal(parts.length, 1)
  assert.equal(parts[0].type, "text")
  assert.equal(parts[0].text, NO_OP_NUDGE)
  assert.equal(parts[0].synthetic, true)
})

// Summary
console.log(`\n${passed} passed, ${failed} failed`)
console.log(`\nNote: smoke test imports actual plugin helpers (noop-guard-helpers.js).`)
console.log(`Hook wiring (event session.idle → messages → promptAsync) проверяется в live-сессии TUI.`)
process.exit(failed > 0 ? 1 : 0)