# Adv360-Pro-ZMK — working notes

Personal fork of `KinesisCorporation/Adv360-Pro-ZMK` for a Kinesis Advantage 360
Professional. Working branch `mev360_v3`, based on `upstream/V3.0`.

`upstream` → `https://github.com/KinesisCorporation/Adv360-Pro-ZMK.git`
`origin` → `git@github.com:mevops/Adv360-Pro-ZMK.git`

The V2.0 → V3.0 migration is **done**. See `MIGRATION.md` for the record of what
changed and why, and for the flashing procedure.

---

## Read this before touching anything

**Stay close to upstream.** Divergence is deliberately minimal — every line not
changed is a line that cannot conflict on the next pull from Kinesis. Don't tidy
upstream's code, don't "fix" its formatting, don't modify nodes that aren't in
the way. The four customisations below are the whole delta.

**Never suggest Kinesis's Adv360-Pro-GUI** (`kinesiscorporation.github.io/Adv360-Pro-GUI/`).
It reads `config/keymap.json` and regenerates `adv360.keymap` and `macros.dtsi`
from it. `keymap.json` is **deliberately stale** — it still holds upstream's
four-layer V3 content. Opening that tool would silently wipe the entire keymap.
Commit `6499e89` is prior evidence of the bot doing exactly that. Safe editors:
Nick Coutsos's keymap-editor (parses `.keymap` directly), or edit by hand.

**Ctrl and Cmd are swapped on macOS, on purpose.** The same keyboard is used on a
Mac and a Windows machine; Windows uses Ctrl where macOS uses Cmd, so a per-device
swap in System Settings makes the same finger do copy/paste on both. Consequence:

| Connection | USB ID | macOS remap |
|---|---|---|
| USB cable | `0x29EA / 0x0362` (Kinesis) | none |
| Bluetooth | `0x1D50 / 0x615E` (ZMK default) | **Ctrl ↔ Cmd swapped** |

Kinesis overrode the USB descriptor but not the BLE PnP ID, so macOS sees two
devices. **A Ctrl or Cmd binding means different things over USB and Bluetooth.**
Home row `A` (`LGUI`) gives Cmd on USB and Ctrl on Bluetooth; `D` (`LCTRL`) the
reverse. Always ask which transport before reasoning about a modifier.

**Clique/ZMK Studio shadows the firmware keymap.** `ZMK_STUDIO_RPC` selects
`ZMK_KEYMAP_SETTINGS_STORAGE`, and `keymap_handle_set()` loads stored bindings
over compiled ones per key position. After *any* Clique edit, changes to
`adv360.keymap` won't appear until `settings-reset.uf2` is flashed. GitHub is
authoritative. (Custom behaviours survive a Clique edit — bindings persist by
`behavior_local_id` — Clique just can't *edit* hold-taps.)

---

## The customisations

Everything else is upstream. All in `config/adv360.keymap` unless noted.

| What | Where |
|---|---|
| `hml` / `hmr` home row mods on `ASDF` / `JKL;` | behaviours + `default_layer` |
| No-home-row-mods safety layer | `extra1`, layer 4, reached by `&tog 4` |
| Caps Word on base, real Caps Lock on Fn | slot 62 of each |
| USB/Bluetooth output toggle `&out OUT_TOG` | `mod` layer slot 68 |
| Ctrl+Alt for Wispr Flow dictation | `fn` layer slot 67 |
| `config/adv360_keys.h` | key position aliases (new file) |

Upstream's `hm` hold-tap stub is left untouched — it has never been bound to a key
in the repo's history and exists only as an example.

### Layers

`default_layer` 0 · `keypad` 1 · `fn` 2 · `mod` 3 · `extra1` 4 (safety) ·
`extra2`–`extra4` 5–7 (still `status = "reserved"`).

`extra1` has **no `status` property, deliberately.** `reserved` is not `okay`, and
`keymap.c` only initialises all layer children when `CONFIG_ZMK_STUDIO` is set,
falling back to `STATUS_OKAY` children otherwise. Restoring `status = "reserved"`
would make the layer work in the Clique build and be silently empty in the
non-Clique one. Don't put it back.

The safety layer is a **full copy** of the base layer, not transparents. That's
intentional: `&trans` would fall through to the keypad layer and force `J K L ;`
back to letters over the numpad. The trade-off is that while the safety layer is
on, the Fn and Mod layers are masked — acceptable for an escape hatch, and
`&tog 4` is present on the layer itself so it can always be toggled off.

### `adv360_keys.h`

Maps every physical key to a matrix position. Its **only** consumers are the two
`hold-trigger-key-positions` settings on `hml`/`hmr`, which stop home row mods
firing on same-hand rolls. Numbers come from `assets/key-positions.md`.

V3 renumbered everything from position 52 upward. If these ever look wrong, the
invariant is: **the defines must cover exactly 0–75, each once.**

---

## Editing the keymap

Bindings are a column grid matching the physical keyboard. There are 76 per layer
and no labels, so the columns are the only thing making a slot identifiable by
eye. Any edit that changes a binding's width breaks the grid.

```sh
bin/keymap-tool.py show fn            # slot numbers + grid positions + bindings
bin/keymap-tool.py find 'LG\(LALT\)'  # locate a binding across all layers
# ...edit the file...
bin/keymap-tool.py check              # 76 bindings per layer, columns consistent
bin/keymap-tool.py fix                # re-align (whitespace only, broken layers only)
```

`fix` asserts the binding sequence is unchanged and aborts otherwise, so it cannot
silently alter a keymap. Always run `check` before committing.

**No verbose comments in the keymap.** Reasoning goes in the commit message, which
can't go stale. Keep source comments short and conventional.

---

## Building

`make` and `make left` use `docker run -it`, which needs a TTY. Without one, drive
Docker directly with the same arguments:

```sh
bin/get_version_local.sh clique >/dev/null
docker build --tag zmk --file Dockerfile .
docker run --rm --name zmk \
  -v "$PWD/firmware:/app/firmware" -v "$PWD/config:/app/config:ro" \
  -e TIMESTAMP="$(date -u +%Y%m%d%H%M)" -e COMMIT="$(git rev-parse --short HEAD)" \
  -e BUILD_RIGHT=true zmk
git checkout -- config/version.dtsi     # the build rewrites it; Makefile does this too
```

Roughly 2–3 minutes once the image is cached. Works on Apple Silicon — the README's
"force x86_64 under colima" advice is stale for Docker Desktop.

**Local builds are always the Clique variant** — `bin/build.sh` hardcodes
`-S studio-rpc-usb-uart -DCONFIG_ZMK_STUDIO=y`. The non-Clique artifact only comes
from CI. That matters when testing anything that behaves differently under Studio.

CI (on push) produces both: `firmware-clique` and `firmware-no-clique`.

```sh
gh run list --repo mevops/Adv360-Pro-ZMK --branch mev360_v3 --limit 3
gh run download <id> --repo mevops/Adv360-Pro-ZMK --name firmware-no-clique --dir firmware/ci
```

### Verifying beyond "it compiled"

Compiling proves little — a wrong `hold-trigger-key-positions` list compiles
happily. To check what was actually generated, pull the devicetree out:

```sh
docker run --rm -v "$PWD/config:/app/config:ro" -v "$PWD/.dtsout:/out" zmk bash -c \
  'west build -s zmk/app -p -d /tmp/b -b adv360_left -S studio-rpc-usb-uart -- \
   -DZMK_CONFIG=/app/config -DCONFIG_ZMK_STUDIO=y >/dev/null 2>&1; cp /tmp/b/zephyr/zephyr.dts /out/'
```

`zephyr.dts` shows each layer's resolved bindings and the expanded position arrays.
For `hml` the list must be right-hand keys plus thumbs only; for `hmr`, left-hand
plus thumbs; 44 entries each, nothing above 75.

Eight expected deprecation warnings, all on upstream-owned nodes, all deliberate:
`label` on the unused `hm` stub and the six original macros, and `quick_tap_ms` on
the `hm` stub. Our own `hml`/`hmr` are clean. A warning naming any other node is new.

---

## Flashing

Full procedure in `MIGRATION.md`. In short: a settings reset is **not** a
prerequisite, only a fallback. Left module first with the right disconnected,
paperclip double-click the Bootloader Button, `cp -X` the file (Terminal, not
Finder), battery on, then the right within 30 seconds.

`cp` reporting `fcopyfile failed: Input/output error` is **success** — the
bootloader pulls the drive out mid-write. Confirm with `ls /Volumes/`; the drive
disappearing is the signal.

`Mod` + `V` types the running firmware's date, branch and commit. Use it before
and after to confirm a flash took.

---

## Commits

Commit messages explain **why**, not just what — this keyboard gets picked up
every few months and `git log` is the only documentation. State the reason and the
consequence of getting it wrong. Long is fine. One commit per logical change, and
split whitespace re-flows from semantic changes so the real diff stays legible.
