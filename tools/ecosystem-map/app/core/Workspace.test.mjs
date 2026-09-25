import assert from "node:assert/strict";
import test from "node:test";
import { PROFILES, Workspace } from "./Workspace.js";

class FakeClassList {
  constructor() { this.values = new Set(); }
  add(...names) { names.forEach(name => this.values.add(name)); }
  remove(...names) { names.forEach(name => this.values.delete(name)); }
  toggle(name, force) {
    const next = force === undefined ? !this.values.has(name) : force;
    next ? this.values.add(name) : this.values.delete(name);
    return next;
  }
  contains(name) { return this.values.has(name); }
}

class FakeElement {
  constructor(tag = "div") {
    this.tagName = tag.toUpperCase();
    this.children = [];
    this.dataset = {};
    this.classList = new FakeClassList();
    this.style = { display: "", setProperty: (key, value) => { this.style[key] = value; } };
    this.hidden = false;
    this.parentElement = null;
    this._nodes = new Map();
  }
  set className(value) { this._className = value; value.split(/\s+/).filter(Boolean).forEach(name => this.classList.add(name)); }
  get className() { return this._className || ""; }
  set innerHTML(value) {
    this._html = value;
    for (const selector of [".tile-head", ".tile-body", "[data-close]", "[data-full]", "[data-size]"]) {
      const node = new FakeElement(selector === ".tile-head" ? "header" : "div");
      node.dataset = {};
      node.parentElement = this;
      if (selector.includes("close")) node.dataset.close = "1";
      if (selector.includes("full")) node.dataset.full = "1";
      if (selector.includes("size")) node.dataset.size = "1";
      this._nodes.set(selector, node);
    }
  }
  get innerHTML() { return this._html || ""; }
  appendChild(node) { this.children.push(node); node.parentElement = this; return node; }
  remove() { this.parentElement?.children.splice(this.parentElement.children.indexOf(this), 1); }
  querySelector(selector) { return this._nodes.get(selector) || null; }
  querySelectorAll(selector) {
    if (selector === ".tile") return this.children.filter(node => node.classList.contains("tile"));
    if (selector === ".tile-head") return this.children.map(node => node.querySelector(".tile-head")).filter(Boolean);
    if (selector === ".tile-focused") return this.children.filter(node => node.classList.contains("tile-focused"));
    return [];
  }
  addEventListener() {}
  setAttribute() {}
  scrollIntoView() {}
  getBoundingClientRect() { return { top: 0, bottom: 100, left: 0 }; }
}

function installDom() {
  const storage = new Map();
  globalThis.localStorage = { getItem: key => storage.get(key) ?? null, setItem: (key, value) => storage.set(key, String(value)) };
  globalThis.document = { body: new FakeElement("body"), createElement: tag => new FakeElement(tag) };
}

function module(id) {
  return { id, title: id, mounted: 0, mount(body) { this.mounted++; this.container = body; }, unmount() {} };
}

test("profiles hide tiles without remounting module instances", () => {
  installDom();
  const root = new FakeElement("main");
  const workspace = new Workspace(root);
  const terminal = module("terminal");
  const browser = module("browser");
  workspace.addTile("project", terminal);
  workspace.addTile("project", browser);

  assert.equal(PROFILES.build.layout, "monad3");
  assert.equal(workspace.setProfile("build"), true);
  assert.equal(terminal.mounted, 1);
  assert.equal(browser.mounted, 1);
  const terminalEl = workspace.tiles.get("project:terminal").el;

  workspace.setProfile("models");
  assert.equal(workspace.tiles.get("project:terminal").el.hidden, true);
  assert.equal(browser.mounted, 1);
  workspace.setProfile("all");
  assert.equal(workspace.tiles.get("project:terminal").el, terminalEl);
  assert.equal(terminal.mounted, 1);

  workspace.focusTile(terminalEl);
  assert.equal(workspace.moveFocused("right"), workspace.tiles.get("project:browser").el);
  assert.equal(workspace.profile, "all");
});

test("profile, ratio and compact state persist per project", () => {
  installDom();
  const root = new FakeElement("main");
  const workspace = new Workspace(root);
  workspace.setActiveProject("one");
  workspace.setProfile("capture");
  workspace.adjustRatio(0.25);
  workspace.setCompact(true);

  const restored = new Workspace(new FakeElement("main"));
  restored.setActiveProject("one");
  assert.equal(restored.profile, "capture");
  assert.equal(restored.ratio, 1.25);
  assert.equal(restored.compact, true);
});
