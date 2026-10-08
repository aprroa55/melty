# Project journal

## Approved design

New project in aprroa55/melty, initially an empty unborn checkout. User approved
combining Isaac-powered guns with invading Isaac enemies/bosses, **solo**, with
discovery during a normal Gungeon run. First playable must include the boss.
The approved concrete proposal is Brimstone, Gapers, Attack Flies and Monstro.
Building was approved; publication and recipe commits have not been approved.
The user subsequently approved uploading the prepared source files to
aprroa55/melty on GitHub so the Windows Codex app can open the project. This
permission covers the source handoff; the Melty release still needs its final
publication approval after the required build, gameplay tests and media.

## Chosen route

Content port into the real Gungeon host through Melty's BepInEx 5 route. Read
Isaac resources from the player's installed copy and adapt enemy behavior to
host actors. No simultaneous second process, no standalone/browser game, no
replacement artwork, no redistribution of game content. Candidate MTG API and
Gibbed archive reader are documented in docs/MELTY_RESEARCH.md; their precise
runtime dependency set needs inspection on the gaming PC.

## Cloud work

Melty initially failed at the network proxy before authentication. A draft
network addition for melty.gg was saved; later authenticated read-only RPC calls
succeeded. List_my_mods returned no projects. Search and game_info results plus
a launched example recipe were inspected. No Melty mutating calls were made.

Installed outside this repository: universal-modder with its Python dependencies,
and official .NET SDK 8.0.425, verified against Microsoft's SHA-512 metadata.
SDK installation does not establish a game-compatible plugin build. Community
source clones live outside the checkout and are not part of the handoff ZIP.
The complete tested cloud install_script and tool activation/start_skill were
saved to the environment configuration draft. That save does not publish the
cloud environment or this mashup; cloud publication remains a user UI action.

Implemented seven design sheets, per-cell evidence, guarded generator and
preflight, read-only Steam locator, bounded ARCH000 index inspector and their
tests. Local reports live in ignored .local/. Whole-project preflight blocks
game builds because actual files/signatures/timings/implementations are missing.
No placeholder plugin or playable demo is offered as this mashup.

## Next step

User answered **yes** to continuing in Codex on the gaming PC. Open the source
handoff there, follow CONTINUE_ON_PC.md, inspect the installed games, complete
and verify the missing sheet cells and implementations, then build/test/capture.
Do not ask the user to repeat settled design choices. No game save/config paths
have been inspected or changed. Perform local backups before the first modded run.
