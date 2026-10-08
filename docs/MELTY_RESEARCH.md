# Confirmed Melty research

Read-only authenticated calls succeeded during this cloud session. No credential
is stored here. The account has no existing mashups/drafts to reuse.

## Games

`search_games` / `game_info` confirmed:

- `enter-the-gungeon`: Unity host, BepInEx 5 (`bepinex-5`) auto-installed by Melty
  at **v5.4.23.5**. Plugin folder `{game}/BepInEx/plugins`, patchers
  `{game}/BepInEx/patchers`, config `{game}/BepInEx/config`. Base files including
  `Assembly-CSharp.dll`, `Assembly-CSharp-firstpass.dll`, `UnityPlayer.dll` and
  `EtG.exe` must not be shipped. No account-risk finding was returned.
- `custom-the-binding-of-isaac-rebirth`: Steam app **250900**, not in Melty's
  install catalog. It cannot be primary or have its path passed as a catalog
  companion. Melty specifically instructs `secondary` for this exception, while
  the mod discovers and reads the real local content itself and reports absence
  in-game. No Isaac loader is required because Gungeon is the host.

Game versions and engine/runtime versions are not established until the local
game files are inspected. Gungeon Steam app **311690** is used for discovery;
confirm it against the local manifest during the handoff.

## Prior projects

`search_mashups` found **no live Gungeon mashup**. Isaac mashups exist on other
hosts, including The Binding of Terraria, Hollow Isaac, The Binding of Rain,
and Isaac's Brimstone in TF2. None returned an exact Gungeon/Isaac combination.

`mashup_info("the-binding-of-rain")` was read as a launched recipe example:

- Unity/BepInEx host Risk of Rain 2; local Isaac content guest.
- One main ZIP maps `BindingOfRain/` to a BepInEx plugins subfolder.
- Requirement `{kind:"loader", id:"bepinex-5"}` and launch `{kind:"game"}`.
- Isaac is listed `secondary` under the catalog exception.
- Melty reports one-click **yes**, and 47 launches in its recent aggregate.
- Its source is not public in the returned metadata; its implementation was
  neither copied nor independently tested here. This project's one-click status
  remains **unverified** until the actual release passes Melty's checks and install.

## Toolkit/community research

- universal-modder: https://github.com/rehan-remade/universal-modder
  `skills/mod-any-game/SKILL.md`; cloned and its CLI executed in cloud. Scanner
  found no installed games. Knowledge-base searches found no Gungeon/Isaac notes.
- MTG API: https://github.com/SpecialAPI/ModTheGungeonAPI
  inspected at `ffbe2c72e89c9939517b31882451622ef253fb59`, source version **1.9.2**,
  target .NET Framework **3.5**, MIT. Item/loot-table API and GameManager readiness
  hook exist. Patcher and additional dependencies need local compatibility and
  packaging inspection before using it. Melty only guarantees BepInEx itself.
- Isaac archive/animation tool: https://github.com/gibbed/Gibbed.Rebirth
  inspected at `8454c449cc60d680d57e3edb27ea9e56009c024a`, zlib license. It documents
  `ARCH000` indexes, filename hashes, archive modes 0/1/2/5, and conversion of
  `animations.b`. Candidate asset names in the sheets come from its file lists;
  exact local existence, decoded contents and frame mappings are **not verified**.

The code in tools/isaac_index.py is an explicitly altered index/hash adaptation,
not a complete resource loader. The original license notice is retained.
