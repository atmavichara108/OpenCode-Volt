---
type: handoff
kind: task
title: Remove DoomOne remnants and enforce crypto-cyber-solarpunk visual contract
status: handoff
owner: dotfiles-agent
spec-home: /home/rudra/dotfiles/docs/specs/
timestamp: 2026-09-25
---

# Dotfiles Handoff: Remove DoomOne

> This is a handoff for the dotfiles agent. The Pip-Boy session does **not**
> edit `/home/rudra/dotfiles` and must not commit dotfiles changes.
>
> This Vault copy is a draft handoff, not the canonical dotfiles spec. The
> dotfiles agent must adopt or revise it in `/home/rudra/dotfiles/docs/specs/`
> rather than treating this file as an already-applied dotfiles change.

## Goal

Remove every DoomOne/Doom One remnant and make the visual contract explicit:
**crypto-cyber-solarpunk** across qtile, rofi, terminal-facing surfaces and
related launcher configuration.

## Required Audit

Search the complete dotfiles repository, including tracked and untracked config
surfaces, for:

- `DoomOne`, `Doom One`, `doomone`, `doom-one`;
- legacy DoomOne fallback names and comments;
- hardcoded DoomOne palette values such as `#282c34`, `#bbc2cf`, `#1c1f24`,
  `#ff6c6b`, `#98be65`, `#da8548`, `#51afef`, `#c678dd` when they are used as
  the old fallback rather than as intentional solar/cyber colors;
- stale references to the removed theme in documentation and scripts.

The audit must distinguish an intentional current color from a legacy theme
fallback. Do not replace unrelated application data blindly.

## Required Changes

1. Remove the DoomOne name from code, comments, docs and theme selectors.
2. Replace the qtile fallback palette with a crypto-cyber-solarpunk palette:
   deep botanical/navy background, translucent surfaces, cyan/teal navigation,
   electric-lime active state, amber warnings, coral errors and violet secondary
   links.
3. Remove hardcoded legacy background values where dynamic wal colors already
   exist; use the palette source of truth instead.
4. Keep pywal/wallust integration working and preserve the existing launcher,
   qtile and tmux behavior.
5. Add a deterministic denylist check (read-only by default) that fails when
   DoomOne names or known legacy fallback markers return.
6. Document the resulting palette contract and the evidence paths.

## Safety and Scope

- No root, sudo, permission experiments, system mutation or bridge activity.
- No secrets, auth files or provider credentials.
- Preserve user keybindings and layout semantics unless a separate approved
  change explicitly says otherwise.
- Do not touch Pip-Boy files from this handoff.
- Do not rewrite Git history, remove or rewrite vendored/plugin repositories, or
  modify their contents as part of the theme cleanup.
- Do not perform blind palette-value replacement. Each legacy-looking color
  must be traced to its source and classified as a DoomOne fallback or an
  intentional current color before any edit.

## Hotkey Handoff

The companion Vault audit at
`docs/specs/pipboy-hotkey-conflict-audit.md` is evidence for the dotfiles agent,
not permission to edit dotfiles from this session. The current evidence is:

- Qtile owns `Alt+Tab` and `Alt+Right`; `Super+Left` is the previous-group
  binding. tmux owns `Ctrl+A` and `Ctrl+H/J/K/L`.
- Alacritty has an empty keyboard binding list; the audited Rofi and Zsh files
  add no desktop-level Alt bindings.
- `Alt+Space`, `Alt+F`, `Alt+H`, and `Alt+T` have browser/desktop menu risks;
  `Alt+Tab` and Alt-arrows are omitted from any new Pip-Boy contract.
- The conservative proposed focus mapping is `Alt+Shift+H/J/K/L`. Bare
  `Alt+H/J/K/L` is only a page-focused alias with explicit `preventDefault()`
  and remains pending a live browser/runtime test.

Adopt the mapping in the canonical dotfiles spec only after checking the actual
runtime and preserving existing Qtile/tmux behavior. This handoff does not
authorize keybinding changes here.

## Acceptance

- Repository-wide denylist search returns no DoomOne/Doom One references in
  active configuration and documentation.
- qtile imports/config validation pass.
- rofi config parses and remains launchable.
- pywal/wallust fallback and generated palette paths are verified.
- Existing tmux and qtile hotkeys are unchanged.
- No blind replacement of palette values was performed; each changed color has
  an evidence path and classification.
- No Git history was rewritten and no vendored/plugin repository was modified.
- The hotkey recommendation is recorded in the canonical dotfiles spec as a
  draft with a live browser/desktop runtime-test requirement.
- Independent verifier reports PASS with the exact search/test commands.
