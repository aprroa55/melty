# Continue this project in Codex on the gaming PC

Open the extracted project folder in a Codex session that can access the local
filesystem and launch the installed games. Paste this instruction:

> Continue the approved solo Gungeon × Isaac mashup in this folder. Read README.md,
> MODLOG.md, docs/CONTRACT.md, docs/STATUS.md, and sheets/*.json first. The user
> approved: normal Gungeon start → discover Brimstone → current gun becomes a
> charged beam → Gaper and Attack Fly encounter → Monstro boss. Both games are
> installed on this PC; find their folders yourself using Steam libraries. Use
> universal-modder's mod-any-game workflow. Complete the real Gungeon BepInEx 5
> mod, test it in the game, and capture real gameplay. Sheets are the source of
> truth: verify every cell, resolve references, and run preflight before each
> build. Never replace Isaac content with stand-ins or bundle game assets. Use
> Melty's tools for publishing, but keep the release unpublished until all
> required tests and media exist and I approve publication. Do not ask me to
> repeat the design choices already recorded here. See docs/STATUS.md for the
> exact pending work and docs/MELTY_RESEARCH.md for the confirmed loader route.

The original Melty credential was intentionally left out of this folder. If this
new session has neither working Melty tools nor injected authentication, ask for
a fresh **Publish prompt from Melty Studio → Coding agents**. Keep its credential
out of project files, commits, screenshots and responses. Do not request a secret
value as an ordinary chat answer.

Do not initialize a new standalone/browser game. This is a real host-game mod.
Use the existing folder; a new Git worktree is unnecessary unless the user asks.

## First local actions for the agent

1. Find local instructions and preserve existing changes. Install Python only if
   unavailable, using its official distribution. Run the existing tool tests.
2. Run `python -m tools.probe_games --output .local/game-probe.json`. If a game is
   from GOG rather than Steam, locate its launcher metadata or ask only for the
   missing path, then use `--gungeon` / `--isaac`. These overrides are development
   tools; the player-facing mod must find Isaac without asking for a path.
3. Clone universal-modder outside the project if it is missing and follow
   `skills/mod-any-game/SKILL.md`; its command is `bin/um`. Read only the relevant
   game code and resources. Do not use paid asset generation without permission.
4. Inspect the actual Gungeon Managed assemblies and Unity version. Do not use
   a publicized third-party game DLL instead of the player's own game reference.
   Match its .NET framework (the current MTG API targets 3.5; confirm locally).
5. Confirm SDK/API releases and dependencies. Melty auto-installs BepInEx, **not
   automatically every community API**. Any extra redistributable dependencies
   must be bundled with license notices, patcher mappings and load order. Inspect
   the MTG API 1.9.2 source and patcher as candidates before deciding to depend on it.
6. Back up the discovered saves/configs before the first modified launch. Make
   the approved modification concrete, then obtain permission before installing
   a loader into the game's folder or changing graphics/registry settings, per
   the toolkit's user-machine instruction. Existing authorization to build/test
   should be reused for actions it already covers; do not ask repeatedly.
7. Decode the handful of needed Isaac resources locally using a licensed reader.
   Plain Rebirth's animation cache is `resources/animations.b`, not necessarily
   loose `.anm2` files. Verify the exact Attack Fly and Brimstone beam mapping.
   Test checksum verification and keep decoded game content in a private cache
   outside this checkout. Do not require a player to run an extractor manually.
8. Implement the source hooks and gameplay from completed sheets. A cell's
   verification can come from actual files, API source and focused tests;
   runtime gameplay checks are recorded separately in docs/STATUS.md. Do not
   create a circular requirement that gameplay must run before the first build.
9. Run full preflight, generate one C# definition per row, compile against local
   game references with copy-local disabled, then launch the real game and verify
   Brimstone pickup, charging/ammo/collision, both enemies, Monstro, normal death,
   restart cleanup and the missing-Isaac in-game message.
10. Capture only the game window with distinctive gameplay. Do not substitute
    mockup media. Then finish the Melty packaging and approval flow recorded in
    docs/STATUS.md. Do not commit/push a recipe until the user agrees.
