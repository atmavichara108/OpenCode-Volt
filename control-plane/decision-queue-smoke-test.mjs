#!/usr/bin/env node
// Smoke test: decision-queue-hook pure functions
// Tests: sanitization, card shape, risk inference, no-content
// No live OpenCode runtime required.
// Imports pure helpers from shared module to test actual plugin logic, not copy.

import { strict as assert } from "assert"
import { inferRisk, sanitizeReason, generateCardId } from "../../../../dotfiles/opencode-global/.config/opencode/plugins/decision-queue-helpers.js"

// Test suite
console.log("Running decision-queue-hook smoke tests...\n")

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

// Test 1: Risk inference — critical
test("inferRisk: git push → critical", () => {
  assert.equal(inferRisk("bash", "git push"), "critical")
})

test("inferRisk: git reset → critical", () => {
  assert.equal(inferRisk("bash", "git reset"), "critical")
})

test("inferRisk: bash sudo → critical", () => {
  assert.equal(inferRisk("bash", "bash sudo"), "critical")
})

// Test 2: Risk inference — high
test("inferRisk: git commit → high", () => {
  assert.equal(inferRisk("bash", "git commit"), "high")
})

test("inferRisk: edit → high", () => {
  assert.equal(inferRisk("edit", "edit"), "high")
})

test("inferRisk: write → high", () => {
  assert.equal(inferRisk("write", "edit"), "high")
})

// Test 3: Risk inference — medium
test("inferRisk: task → medium", () => {
  assert.equal(inferRisk("task", "task"), "medium")
})

test("inferRisk: webfetch → medium", () => {
  assert.equal(inferRisk("webfetch", "webfetch"), "medium")
})

// Test 4: Risk inference — low
test("inferRisk: read → low", () => {
  assert.equal(inferRisk("read", "read"), "low")
})

test("inferRisk: grep → low", () => {
  assert.equal(inferRisk("grep", "read"), "low")
})

// Test 5: Sanitization — no secrets
test("sanitizeReason: strips API keys (api_key=)", () => {
  const input = "Failed with api_key=sk-1234567890abcdef"
  const output = sanitizeReason(input)
  assert.ok(!output.includes("sk-1234567890abcdef"))
  assert.ok(output.includes("[REDACTED]"))
})

test("sanitizeReason: strips tokens", () => {
  const input = "Auth failed: token=ghp_abcdefghijklmnopqrstuvwxyz"
  const output = sanitizeReason(input)
  assert.ok(!output.includes("ghp_abcdefghijklmnopqrstuvwxyz"))
  assert.ok(output.includes("[REDACTED]"))
})

test("sanitizeReason: strips Bearer tokens", () => {
  const input = "Request with Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
  const output = sanitizeReason(input)
  assert.ok(!output.includes("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"))
  assert.ok(output.includes("[REDACTED]"))
})

test("sanitizeReason: strips home paths", () => {
  const input = "File not found: /home/user/secret/project/file.txt"
  const output = sanitizeReason(input)
  assert.ok(!output.includes("/home/user/secret/project/file.txt"))
  assert.ok(output.includes("[PATH]"))
})

test("sanitizeReason: truncates long reasons", () => {
  const input = "A".repeat(500)
  const output = sanitizeReason(input)
  assert.ok(output.length <= 200)
})

test("sanitizeReason: handles empty input", () => {
  const output = sanitizeReason("")
  assert.equal(output, "Permission event captured")
})

test("sanitizeReason: handles null input", () => {
  const output = sanitizeReason(null)
  assert.equal(output, "Permission event captured")
})

// Test 6: Sanitization — "api key" with space (blocker 6)
test("sanitizeReason: strips 'api key' with space", () => {
  const input = "Failed with api key sk-1234567890abcdef"
  const output = sanitizeReason(input)
  assert.ok(!output.includes("sk-1234567890abcdef"))
  assert.ok(output.includes("[REDACTED]"))
})

test("sanitizeReason: strips 'api-key' with dash", () => {
  const input = "Failed with api-key=sk-1234567890abcdef"
  const output = sanitizeReason(input)
  assert.ok(!output.includes("sk-1234567890abcdef"))
  assert.ok(output.includes("[REDACTED]"))
})

// Test 7: Card ID generation
test("generateCardId: includes date", () => {
  const id = generateCardId("bash", "git push")
  const today = new Date().toISOString().split("T")[0]
  assert.ok(id.startsWith(today))
})

test("generateCardId: includes type slug", () => {
  const id = generateCardId("bash", "git push")
  assert.ok(id.includes("bash"))
})

test("generateCardId: handles missing type", () => {
  const id = generateCardId(undefined, "bash")
  assert.ok(id.includes("bash"))
})

// Summary
console.log(`\n${passed} passed, ${failed} failed`)
console.log(`\nNote: smoke test imports pure helpers from shared module (decision-queue-helpers.js),`)
console.log(`testing actual plugin logic, not copy. createCard() not tested here (requires runtime types).`)
process.exit(failed > 0 ? 1 : 0)
