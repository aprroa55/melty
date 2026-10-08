# Gungeon × Isaac — development handoff

**Source preparation only. There is no playable mod or release yet.**

The approved first playable is a **solo Enter the Gungeon mod**. Start a normal
run, discover Brimstone in the opening room, and transform the current gun into
a charged beam. Gapers and Attack Flies appear in the following eligible combat
room. A Monstro encounter is part of the first playable, not a later extra.

Gungeon remains the real host game. Isaac artwork and animation data must be
loaded from the player's own installation of **The Binding of Isaac: Rebirth**.
Both games are required by the design; no Isaac game content belongs in the
release or source repository. Isaac does not have to run simultaneously.
No DLC requirement has been established; test base Rebirth first and inspect
additional installed resource variants before claiming compatibility.

## Continue on the gaming PC

Open this folder in Codex on the PC with both games installed and use
[CONTINUE_ON_PC.md](CONTINUE_ON_PC.md). The agent handles finding the game folders,
installing development dependencies, completing the mod, building, and testing.

## What is implemented here

- Read-only Steam discovery, including other Steam libraries and Windows/WSL paths.
- Isaac `ARCH000` archive **index** inspection for selected resource paths. This
  does not yet extract or decode sprites or animation data.
- Seven JSON sheets covering items, weapons, enemies, bosses, assets, systems,
  and host hooks, with a checkbox and evidence for every cell.
- Whole-project preflight and one C# definition per completed sheet row. Generation
  refuses to run while any value or verification is missing.
- Tests of those development tools using synthetic fixtures, not retail game data.

No Gungeon plugin, enemy integration, Brimstone gameplay, or Monstro gameplay has
been implemented or tested. No screenshot or installable package exists yet.

## Development checks

Python 3.10+ is sufficient for these tools; the later plugin needs a C# toolchain.
Run from this folder:

```sh
python -m unittest discover -s tests -v
python -m tools.probe_games --output .local/game-probe.json
python -m tools.sheets --report .local/preflight.json --generate generated
```

The tests currently pass. Probe and preflight exit **2** when prerequisites are
missing. Current preflight deliberately blocks game generation/builds: game
signatures, resources, animation decoding, balance values, and runtime source
implementations still need verification. See [docs/STATUS.md](docs/STATUS.md).

Edit the sheets first. Do not hand-edit generated records or mark unknown cells
verified just to pass preflight. A successful preflight is not proof of gameplay.

## Publishing

Melty confirmed BepInEx 5 **v5.4.23.5** installs automatically for Gungeon. Isaac
is outside its catalog: the mod must locate Isaac itself and display an in-game
message when it is missing or unreadable. Melty's instructed recipe roles are
Gungeon `primary`, Isaac `secondary`; the latter is the catalog exception and
must still contribute actual installed content.

See [docs/MELTY_RESEARCH.md](docs/MELTY_RESEARCH.md). No listing, upload, recipe
submission, or publication was performed. Title, credits, project license, and
remix choice still need the user's agreement after a playable build exists.

The project source license has **not been selected**. The adapted archive-index
code retains its upstream zlib notice in `third_party/`.
