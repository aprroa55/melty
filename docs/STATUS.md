# What is done and what blocks gameplay

The approved game design is recorded in README.md and the seven sheets. Tools for
read-only game discovery, archive index inspection, sheet preflight and guarded
C# row generation are implemented. Twenty-one development-tool tests passed using
synthetic data. These tests do not exercise a Gungeon plugin or real Isaac data.

Current full preflight covers **142 cells**: **75 verified, 67 unresolved**.
All cross-sheet references resolve. The unresolved cells are explicit missing
or unverified values, not silently substituted defaults. Mod generation/build
was correctly blocked and no generated runtime records were emitted.

`python -m tools.probe_games` returned `missing_game_access`: no Gungeon or Isaac
Steam installs and no Managed assemblies are available in this cloud instance.
The user agreed to continue in Codex on the gaming PC. The cloud has no active
game desktop or access to that PC. Game-file inspection and real gameplay/media
cannot proceed until that session is opened.

## Required work before the first playable

- Read the installed host Unity/.NET version and targeted assemblies. Verify
  source signatures before implementing hooks; do not guess them.
- Verify/decode real Isaac sprites and `animations.b`, including the exact
  Attack Fly variant and Brimstone beam mapping. Decide the licensed packed
  resource reader and bundle its allowed runtime dependencies automatically.
- Fill and verify numeric balance/timing fields from original behavior and host
  scaling. Implement Brimstone charge/release/ammo/damage, enemy actors and Monstro.
- Implement room progression, pedestal placement, missing-content in-game UI,
  and restart/death/floor/plugin-disable cleanup.
- Fill `systems.*.implementationRef` with actual source paths and focused test
  evidence. Confirm `hooks.*.signatureVerified` against the installed assembly.
  Do not confuse source-cell verification with later in-game proof.
- Run full preflight, generate records and compile. Build references must point
  at the player's installation and must never be copied to output.

## In-game acceptance checks — all UNRUN

1. With both games installed, launch the modded Gungeon successfully and record
   loader/plugin versions and logs. No manual player extractor/dependency step.
2. Starting a normal solo run preserves initial Gungeon behavior. A reachable
   Isaac Brimstone pickup appears in the opening eligible room.
3. Pickup transforms the current gun. Remapped fire/aim works; partial charge
   cancels correctly; full charge fires a beam with real Isaac art, bounded ammo
   use, host wall collision and enemy damage.
4. In the next eligible combat room, both Gapers and Attack Flies use verified
   original sprites/frames, take damage, navigate appropriately and die normally.
5. Monstro spawns in a valid boss arena, telegraphs and attacks, takes damage,
   and its death unseals/completes the room without corrupting the run.
6. Death/restart/floor transitions do not duplicate pickups/callbacks, retain
   transformations, or leak actors. Repeat a fresh run.
7. Missing Isaac or unsupported assets produce the agreed in-game message;
   base Gungeon remains playable and no substitute guest artwork is used.
8. Test the final Melty install itself. Capture a real screenshot/clip showing
   distinctive behavior, not a source preview or mockup.

## Required publishing work — all UNRUN

Keep it a draft until the playable version and real media are verified. There is
currently no Melty modId, no listing, no ZIP release and no upload.

After gameplay: propose title/tagline/description based on the actual build, and
ask one focused question at a time for missing credits, project content license
and remix permission. Do not infer a project license from dependency licenses.

Package only the mod and licensed dependencies, retain required notices, list
every archive entry, and run `inspect_package`, `validate_recipe`, then
`one_click_check` with the actual recipe, entries and README feature list. Fix
all blockers before upload. This is solo; do not invent multiplayer settings.

Use `create_mod` with agreed metadata and `githubRepo: "aprroa55/melty"`, or reuse
an unmistakable project draft returned by `list_my_mods`; record its modId. Upload
real packages with byte size/SHA-256 and the returned upload headers, complete
uploads, then submit the validated release. Upload and finish real gameplay media.
Save the validated root `melty.json` only when it describes the actual package;
commit it once the user agrees. Do not use a guessed recipe as a published claim.

Present the concrete release summary and ask for publication approval. Only then
call `publish`, complete the user's Melty Play-to-publish requirement, call
`mod_status`, and report live only on server confirmation. The original brief
contains the detailed tool flow; credentials belong only in Melty authorization.
