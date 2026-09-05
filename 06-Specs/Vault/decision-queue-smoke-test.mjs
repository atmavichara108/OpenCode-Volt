#!/usr/bin/env node
// Smoke test: decision-queue-hook pure functions
// Tests: sanitization, card shape, risk inference, no-content
// No live OpenCode runtime required.

import { strict as assert } from "assert"

// Inline pure functions from plugin (no runtime dependencies)
function inferRisk(tool, permission) {
  const toolLower = (tool || "").toLowerCase()
  const permLower = (permission || "").toLowerCase()

  if (
    toolLower.includes("push") ||
    toolLower.includes("force") ||
    toolLower.includes("reset") ||
    toolLower.includes("clean") ||
    (permLower.includes("bash") && (permLower.includes("sudo") || permLower.includes("rm")))
  ) {
    return "critical"
  }

  if (
    toolLower.includes("git") ||
    toolLower.includes("edit") ||
    toolLower.includes("write") ||
    permLower.includes("edit") ||
    permLower.includes("external_directory")
  ) {
    return "high"
  }

  if (
    toolLower.includes("task") ||
    toolLower.includes("webfetch") ||
    toolLower.includes("websearch") ||
    permLower.includes("task")
  ) {
    return "medium"
  }

  return "low"
}

function sanitizeReason(reason) {
  if (!reason) return "Permission event captured"

  let sanitized = reason.slice(0, 200)

  sanitized = sanitized
    .replace(/(?:api[_-]?key|token|password|secret|auth)[\s:=]+[^\s,;]+/gi, "[REDACTED]")
    .replace(/(?:sk-|ghp_|github_pat_)[a-z0-9]{10,}/gi, "[REDACTED]")
    .replace(/Bearer\s+[^\s]+/gi, "[REDACTED]")

  sanitized = sanitized.replace(/\/home\/[^\s]+/g, "[PATH]")
  sanitized = sanitized.replace(/\/Users\/[^\s]+/g, "[PATH]")

  return sanitized.trim() || "Permission event captured"
}

function generateCardId(tool, permission) {
  const now = new Date()
  const dateStr = now.toISOString().split("T")[0]
  const timeStr = now.toTimeString().split(" ")[0].replace(/:/g, "")

  const slug = (tool || permission || "permission")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 30)

  return `${dateStr}-${timeStr}-${slug}`
}

function createCard(event) {
  const tool = event.tool || "unknown"
  const permission = event.permission || "unknown"
  const agent = event.agent || "unknown"
  const session = event.session || "unknown"
  const directory = event.directory || "unknown"
  const reason = sanitizeReason(event.reason)
  const risk = inferRisk(tool, permission)

  const title = `Permission event: ${tool}`
  const context = `Agent ${agent} triggered ${permission} for tool ${tool}`

  const options = [
    {
      id: "A",
      label: "Allow this time",
      pros: ["Unblocks current operation"],
      cons: ["May not align with policy"]
    },
    {
      id: "B",
      label: "Deny and review",
      pros: ["Safe default", "Requires policy review"],
      cons: ["Blocks operation"]
    },
    {
      id: "C",
      label: "Update policy",
      pros: ["Permanent fix"],
      cons: ["Requires config change"]
    }
  ]

  return {
    id: generateCardId(tool, permission),
    created: new Date().toISOString(),
    status: "pending",
    risk,
    source: {
      agent,
      session,
      trigger: "permission.asked",
      tool,
      permission,
      directory
    },
    dilemma: {
      title,
      context,
      options,
      recommendation: null,
      reason
    },
    resolution: {
      choice: null,
      approved_by: null,
      approved_at: null,
      evidence: null
    },
    stop_condition: "after user decision via /decisions command"
  }
}

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
  assert.equal(inferRisk("git push", "bash"), "critical")
})

test("inferRisk: git reset → critical", () => {
  assert.equal(inferRisk("git reset", "bash"), "critical")
})

test("inferRisk: bash sudo → critical", () => {
  assert.equal(inferRisk("bash", "bash sudo"), "critical")
})

// Test 2: Risk inference — high
test("inferRisk: git commit → high", () => {
  assert.equal(inferRisk("git commit", "bash"), "high")
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
test("sanitizeReason: strips API keys", () => {
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

// Test 6: Card shape — required fields
test("createCard: has all required fields", () => {
  const card = createCard({
    tool: "git push",
    permission: "bash",
    agent: "meta",
    session: "abc123",
    directory: "/home/user/project",
    reason: "Push to remote"
  })

  assert.ok(card.id)
  assert.ok(card.created)
  assert.equal(card.status, "pending")
  assert.ok(["low", "medium", "high", "critical"].includes(card.risk))
  assert.ok(card.source.agent)
  assert.ok(card.source.session)
  assert.ok(card.source.trigger)
  assert.ok(card.dilemma.title)
  assert.ok(card.dilemma.context)
  assert.ok(Array.isArray(card.dilemma.options))
  assert.ok(card.dilemma.options.length >= 2)
  assert.equal(card.resolution.choice, null)
  assert.equal(card.resolution.approved_by, null)
})

// Test 7: Card shape — no content leakage
test("createCard: no prompt content in card", () => {
  const card = createCard({
    tool: "bash",
    permission: "bash",
    agent: "meta",
    session: "abc123",
    directory: "/home/user/project",
    reason: "User asked to run git push --force to deploy secret API key sk-1234567890abcdef"
  })

  const cardStr = JSON.stringify(card)
  // Secrets must be redacted
  assert.ok(!cardStr.includes("sk-1234567890abcdef"))
  // Reason is metadata and can be preserved (after sanitization)
  assert.ok(card.dilemma.reason.includes("[REDACTED]"))
})

test("createCard: no tool output in card", () => {
  const card = createCard({
    tool: "bash",
    permission: "bash",
    agent: "meta",
    session: "abc123",
    directory: "/home/user/project",
    reason: "Command output: password=secret123 token=ghp_abcdefghijklmnopqrstuvwxyz"
  })

  const cardStr = JSON.stringify(card)
  assert.ok(!cardStr.includes("secret123"))
  assert.ok(!cardStr.includes("ghp_abcdefghijklmnopqrstuvwxyz"))
})

// Test 8: Card ID generation
test("generateCardId: includes date", () => {
  const id = generateCardId("git push", "bash")
  const today = new Date().toISOString().split("T")[0]
  assert.ok(id.startsWith(today))
})

test("generateCardId: includes tool slug", () => {
  const id = generateCardId("git push", "bash")
  assert.ok(id.includes("git-push"))
})

test("generateCardId: handles missing tool", () => {
  const id = generateCardId(undefined, "bash")
  assert.ok(id.includes("bash"))
})

// Test 9: Options structure
test("createCard: options have required fields", () => {
  const card = createCard({
    tool: "git push",
    permission: "bash",
    agent: "meta",
    session: "abc123",
    directory: "/home/user/project",
    reason: "Push to remote"
  })

  for (const option of card.dilemma.options) {
    assert.ok(option.id)
    assert.ok(option.label)
    assert.ok(Array.isArray(option.pros))
    assert.ok(Array.isArray(option.cons))
  }
})

// Test 10: No auto-recommendation
test("createCard: recommendation is null (no auto-recommendation)", () => {
  const card = createCard({
    tool: "git push",
    permission: "bash",
    agent: "meta",
    session: "abc123",
    directory: "/home/user/project",
    reason: "Push to remote"
  })

  assert.equal(card.dilemma.recommendation, null)
})

// Summary
console.log(`\n${passed} passed, ${failed} failed`)
process.exit(failed > 0 ? 1 : 0)
