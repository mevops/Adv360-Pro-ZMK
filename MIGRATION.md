# V2.0 → V3.0 migration — record and flashing reference

Completed 2026-09-28. Branch `mev360_v3`, based on `upstream/V3.0`.

`CLAUDE.md` has the day-to-day working notes. This file is the record of what the
migration changed and why, and the flashing procedure, which is durable.

---

## 1. Clique vs. home row mods

Clique is Kinesis's browser-based configurator, built on the ZMK Studio framework.
The assumption going in was that adopting it meant giving up home row mods. That is
half right, and the useful half is the other way round:

- **You do not have to choose.** `V3.0`'s CI builds two artifacts from the *same*
  config — `firmware-clique` and `firmware-no-clique`. The Clique build is the same
  keymap compiled with `-S studio-rpc-usb-uart -DCONFIG_ZMK_STUDIO=y`. Custom
  hold-taps compile in and run either way.
- **Clique cannot edit them.** Kinesis list Home-row Mods, Tap Dance and Mod Morph
  as unmodifiable, along with anything in the config files.

Verified in the ZMK source rather than taken from the marketing page:
`zmk_keymap_save_bindings()` persists every binding as
`{behavior_local_id, param1, param2}`, so a Clique edit elsewhere on the board does
not drop `&hml`/`&hmr` bindings. The `d93499b "Fallback to trans if possible"`
commit is a runtime guard for bindings whose behaviour id no longer resolves, not
Studio rewriting the keymap.

**The trap is two sources of truth.** `ZMK_STUDIO_RPC` selects
`ZMK_KEYMAP_SETTINGS_STORAGE` (confirmed in a real build's Kconfig output), and
`keymap_handle_set()` loads the stored keymap *over* the compiled one, per binding.
After any Clique edit, a later change to `adv360.keymap` plus a reflash will appear
not to take effect until `settings-reset.uf2` is flashed.

**Decision: pure ZMK, GitHub authoritative.** The branch still builds the Clique
artifact, so the option is open; it is just not the source of truth.

## 2. Why the upgrade was worth doing

The V2 config carried two commented-out lines with the note
*"safety layer bc old firmware version apparently"*. The V3 base
(`refil/zmk @ adv360-z3.5-2`) adds exactly what they needed:

| Property | `adv360-z3` (V2) | `adv360-z3.5-2` (V3) |
|---|---|---|
| `global-quick-tap` | yes | yes, but deprecated |
| `require-prior-idle-ms` | **no** | **yes** |
| `hold-trigger-on-release` | **no** | **yes** |
| `hold-while-undecided` | **no** | **yes** |

`global-quick-tap` was never a missing feature — in `behavior_hold_tap.c` it is
implemented as `require_prior_idle_ms = quick_tap_ms`, so it was already doing the
job, pinned to 175 ms. Setting `require-prior-idle-ms = 150` explicitly decouples
the two. `hold-trigger-on-release` is the genuine gain: without it, a second mod on
the same hand collapses the first to a letter.

## 3. What actually broke: the matrix renumbering

V3 removed 8 unused keys from the matrix transform, renumbering **every position
from 52 upward** (0–51 unchanged). `config/adv360_keys.h` still held V2 numbers.

Its only consumers are the two `hold-trigger-key-positions` settings. Left as-is,
`RIGHT_KEYS` would have contained 60–64 — which under V3 are the bottom-**left**
row — putting left-hand keys on the left-hand mods' allow-list and inverting the
same-hand guard, plus referencing 76–81 which no longer exist.

**This compiles cleanly and mostly works.** The symptom would have been occasional
phantom modifiers with no obvious cause.

Upstream's `UPGRADE.md` says to delete 8 `&none` per layer and merge, taking your
side of every conflict. That resolves the *textual* conflict and leaves this one
in place. **The migration was done by reconstructing on a clean `V3.0` base
instead**, re-applying a 13-slot delta by hand.

## 4. The commits

```
004c216  fix(keymap): renumber key position aliases for the V3 matrix
5363649  feat(keymap): add hml/hmr home row mods to the base layer
9cc1f8b  feat(keymap): adopt timeless homerow mod timings
0f0ae41  feat(keymap): swap Caps Lock for Caps Word, keep Caps Lock on Fn
c16711f  refactor(keymap): use display-name instead of deprecated label on hml/hmr
9b7f8d8  style(keymap): reflow the mod layer onto the key grid
d77c11c  feat(keymap): add USB/Bluetooth output toggle to the mod layer
0b4b814  feat(keymap): add a no-home-row-mods safety layer on extra1
512b32d  feat(keymap): bind Ctrl+Alt on Fn + End for Wispr Flow
bf1c7c9  fix(keymap): send LGUI on Fn+End, as Ctrl vs Cmd is OS-dependent
288ed92  tooling: add keymap-tool.py for inspecting and re-aligning the keymap
```

Each message carries its own reasoning; that is the primary documentation.

### Decisions taken along the way

- **`macros.dtsi` taken from upstream unchanged.** The V2 delta was pure GUI
  reformatting from `adv360proapp[bot]`, no semantic content. V3 adds ~25 new
  `Win_*`/`Mac_*` macros as a free gain.
- **Upstream's `hm` stub left alone.** Never bound in the repo's history.
- **`keymap.json` and `info.json` left stale**, to keep divergence at zero. See the
  warning in `CLAUDE.md` — the tool that reads them would destroy the keymap.
- **`&rgb_ug RGB_MEFS_CMD 5` not restored** after upstream dropped it. Unused.
- **Safety layer is a full copy, not transparents.** Reasoning in `CLAUDE.md`.

## 5. How it was verified

Compiling proves very little here, so most claims were checked against the
generated devicetree or on the hardware:

| Claim | Evidence |
|---|---|
| Key aliases cover exactly 0–75, once each | script over the header |
| `hml`/`hmr` trigger arrays correct per hand | compiled `zephyr.dts` — 44 entries each, no wrong-hand leakage, none above 75 |
| Timings 300 / 175 / 150 + `hold-trigger-on-release` | compiled `zephyr.dts` |
| `extra1` populated, no `status`, `extra2`–`4` untouched | compiled `zephyr.dts` |
| Studio selects keymap settings storage | Kconfig output of a real build |
| Builds, Clique variant | local Docker, both halves |
| Builds, non-Clique variant | CI |
| Same-hand guard works | **on hardware** — hold `F` tap `D` gives `fd` |
| Safety layer genuinely disables the mods | **on hardware** — `&tog 4` silences them |

The last two could not be established by building. The safety-layer test matters
particularly: it ran on the **non-Clique** firmware, which is the build where a
leftover `status = "reserved"` would have produced an empty, transparent layer.

---

## 6. Flashing

Source: Kinesis, *Installing Firmware on the Advantage360 with the ZMK Engine
(KB360-PRO)*, v9/5/2024.

**A settings reset is not a prerequisite.** It is the fallback if a normal update
misbehaves. Kinesis's order: update normally → power-cycle several times → only
then reset both modules and start again.

### Before starting

- Have another keyboard to hand; the Adv360 is unusable during the update.
- Locate the Bootloader Button on each module (User Manual §2.7 p.9). Paperclip.
- Record the current version: hold `Mod`, press `V`. It types date, branch, commit.
- Have `settings-reset.uf2` from this branch available in case of the fallback.

### The update

1. Connect the **LEFT** module by USB. **Disconnect and power down the RIGHT.**
2. Paperclip, **double-click** the Bootloader Button on the LEFT. LEDs flash white
   then solid green; an `ADV360PRO` drive appears. The timing is fussy.
3. Copy the **left** `.uf2`. On macOS use Terminal, not Finder, so extended
   attributes are not written to the drive:
   ```sh
   cp -X firmware/ci/<timestamp>-<commit>-left.uf2 /Volumes/ADV360PRO/
   ```
   `cp` will report `fcopyfile failed: Input/output error`. **That is success** —
   the bootloader pulls the drive out mid-write. Confirm with `ls /Volumes/`; the
   drive disappearing is the signal.
4. Turn the LEFT module's **battery switch ON**, then disconnect it.
5. **Move quickly.** The left module sleeps after 30 seconds and the right must not
   lose track of it. Tap `Fn` on the left to reset the timer.
6. Connect the **RIGHT** module and repeat steps 2–3 with the **right** `.uf2`.
7. Once the right stops flashing blue, **hold `Mod`** — both Layer LEDs should be
   green. That is Kinesis's confirmation.
8. `Mod`+`V` to confirm the new commit.

### Kinesis's rules of thumb

- **Always power on the LEFT first and power it down last.** Never let the RIGHT
  lose track of the LEFT — that is what makes it flash red.
- Do not open both virtual drives at once; you will not tell them apart.
- Never unplug while the LEDs are flashing blue.
- Left and right files are a matched set; install both on the correct modules.
- Keystrokes and bootloader chords are disabled while a drive is open, **and after
  a settings reset** — only the physical button works then.
- OS file-transfer errors can be ignored. macOS eject warnings are called out
  specifically as safe.

### If it does not work

1. Power-cycle both several times: disconnect and power both down, wait 5 s,
   connect the LEFT, wait 5 s, connect the RIGHT.
2. Still broken — right module flashing red means the halves are not talking. Now
   flash `settings-reset.uf2` to **both** modules, then start again at step 1.
   A reset wipes the firmware and disables the keyboard until new firmware is
   installed, so only the physical Bootloader Button will work.

### Reference

- [Firmware Update Instructions (PDF, 9/5/2024)](https://kinesis-ergo.com/wp-content/uploads/Advantage360-Professional-Firmware-Update-Instructions-9.5.24-KB360-PRO.pdf)
- [Settings Reset Instructions (PDF, 11/22/2023)](https://kinesis-ergo.com/wp-content/uploads/Advantage360-Professional-Settings-Reset-Instructions-11.22.23-KB360-PRO-GBR.pdf)
- [Firmware updates hub](https://kinesis-ergo.com/support/kb360pro/#firmware-updates)
- [User Manual (Clique edition)](https://kinesis-ergo.com/wp-content/uploads/Advantage360-ZMK-KB360-PRO-Users-Manual-v2-5-25-Clique.pdf)
- [Clique upgrade](https://kinesis-ergo.com/360p-clique-upgrade/)
