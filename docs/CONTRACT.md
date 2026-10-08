# Host/content contract

- **Host and player:** Gungeon owns movement, configured controls, camera, physics,
  damage resolution, room sealing, save state and the run. This is solo play.
- **Guest contribution:** Isaac's actual sprites and animation data come from the
  player's installed copy. Adapt its enemy/boss behavior to host-native actors
  after checking the original behavior; do not claim the entire Isaac engine runs.
- **Launch:** only Gungeon launches. There is no IPC or companion process.
- **Discovery:** query Windows Steam registry/install roots and Steam
  `libraryfolders.vdf` / appmanifest `250900`. Support multiple libraries. Do not
  ask the player to locate the folder. Non-Steam discovery remains unimplemented.
- **Readiness:** verify required sprites/animation data before registering the
  crossover. Missing or unsupported content gives an in-game explanation and
  leaves normal Gungeon working. No look-alike fallback is acceptable.
- **Content:** read only the selected original resources; decoding is read-only
  and may use a private per-user cache keyed by file identity. No copyrighted
  game data is in the repository, package or source handoff.
- **Units and timing:** host room coordinates, navigation, firing and combat are
  authoritative. Isaac-to-Gungeon scaling, speeds, frame durations and damage
  values remain unfilled until inspected/tested; do not invent them as facts.
- **Threads:** Unity objects are touched on the main thread. File decoding, hashes
  and cache work happen before gameplay/on a worker, never blocking every frame.
- **Lifecycle:** spawn/pickup callbacks must be once-per-run, scene safe, and
  removable. Restore only changes owned by this mod. Death, restart and plugin
  disable must not retain a beam or duplicate encounters.
- **Controls:** reuse Gungeon's configured fire/aim actions; no hard-coded keyboard
  bindings. Confirm the actual native input API in the installed assembly.
- **Packaging:** game references are compile-only and never copied to release.
  Extra community libraries need verified compatibility, permission to redistribute
  and license notices. A manual dependency install fails the one-click target.
