---
type: contract
kind: contract
title: Pip-Boy hotkey conflict audit and safe keyboard contract
status: review
timestamp: 2026-09-25
---

# Pip-Boy Hotkey Contract

## Sources Audited

- qtile: `/home/rudra/dotfiles/qtile/.config/qtile/keys.py`
- tmux: `/home/rudra/dotfiles/tmux/.tmux.conf`
- Alacritty: `/home/rudra/dotfiles/alacritty/.config/alacritty/alacritty.toml`
- Rofi: `/home/rudra/dotfiles/rofi/.config/rofi/config.rasi`
- Zsh: `/home/rudra/dotfiles/zsh/.zshrc`
- Pip-Boy: `tools/ecosystem-map/app/core/App.js`

## Evidence

- Qtile binds `Alt+Tab` to last-group toggle and `Alt+Right` to next group.
- Qtile binds `Super+Left` to the previous group; it is not an `Alt+Left`
  binding. Qtile also owns `Super+H/J/K/L`, `Super+Space`, `Super+F`, and
  `Super+Shift+H/J/K/L`.
- tmux uses `Ctrl+A` as its prefix and unconditionally owns `Ctrl+H/J/K/L`;
  no Alt bindings were found.
- Alacritty declares an empty keyboard binding list. Rofi and Zsh expose no
  desktop-level Alt binding in the audited configuration files.
- Pip-Boy currently handles `Alt+1..9`, `Alt+0`, and `Alt+T`, plus unmodified
  `F`, arrows, `Tab`, `N`, `X`, `R`, and `L` in `App.js`.

## Reserved and Omitted

Do not assign Pip-Boy actions to these combinations:

- `Alt+Tab`: occupied by Qtile.
- `Alt+Right`: occupied by Qtile. `Alt+Left` is not evidenced as a Qtile
  binding, but both Alt-arrow directions remain omitted because desktop/runtime
  ownership is not established.
- `Alt+Space`: desktop/window-environment reservation.
- `Alt+F`: browser/application menu risk.
- `Alt+H`: browser history/menu risk; do not promise it globally.
- `Alt+T`: browser tools risk and currently a Pip-Boy theme action.
- Bare Alt-arrow navigation and unmodified browser/menu keys generally remain
  outside the contract.

## Proposed Pip-Boy Mapping

This is the safe proposal for a dotfiles/app implementation; it is not a
request to edit dotfiles in this repository:

- `Alt+Shift+H/J/K/L`: focus tile left/down/up/right.
- `Alt+Shift+U/O/I/P`: reorder the focused tile left/right/up/down, subject to
  the app's layout semantics. If the implementation cannot provide a stable
  physical direction mapping, leave reorder unbound rather than reusing a
  reserved key.
- `Alt+Shift+Z`: toggle fullscreen for the focused tile.
- `Alt+Shift+X`: close the focused tile.
- `Alt+Shift+N`: normalize layout/ratio.
- `Alt+Shift+R`: refresh mounted modules.
- `Alt+Shift+P`: open the Pip-Boy palette.
- `Alt+1..9` and `Alt+0`: retain existing project selection only after the
  browser/runtime test confirms those combinations are not intercepted.

The parent-preferred `Alt+H/J/K/L` focus path may be offered only while the
Pip-Boy page has focus, with an explicit `keydown` `preventDefault()` for the
handled combination and a guard that skips editable controls and embedded
terminal/browser content. It is an opt-in ergonomic alias, not the safe global
contract, until live browser testing proves that it does not trigger browser
history/menu behavior. Bare `Alt+H/J/K/L` cannot be promised safe from static
dotfile evidence alone.

Do not use `Alt+Tab`, `Alt+Space`, Alt-arrows, `Alt+F`, `Alt+H`, or `Alt+T` for
new Pip-Boy actions. Existing unmodified Pip-Boy keys remain an app-level
compatibility concern and must not be described as desktop-safe bindings.

## Verification

The audit is rerun whenever qtile, tmux, Alacritty, Rofi, Zsh, or Pip-Boy
keymaps change. A live test is required in each supported browser and desktop
session: test a normal page, focused text input, embedded terminal/browser tile,
and the desktop with `Alt+Tab`, `Alt+Space`, `Alt+Left/Right`, `Alt+F`,
`Alt+H`, and `Alt+T`. Confirm both that reserved actions still work and that
Pip-Boy handles only the proposed page-focused combinations. Static evidence
cannot certify desktop runtime ownership.
