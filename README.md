# Echoes of Tomorrow

An original Ren'Py visual novel created as a sample game for
[vnflight](https://github.com/vnflight/vnflight).

## Contents

- `game/`: game source and assets.
- `tools/`: asset generation tools.
- `game_briefing.md`: spoiler-free briefing.
- `LICENSE`: MIT license for project-owned contributions.
- `THIRD_PARTY_NOTICES.md`: asset exceptions and provenance status.

Compatibility adapters are maintained exclusively in the separate mods repository.
This repository does not ship adapters, installed shims, compiled scripts, or saves.

## Using With vnflight

Get vnflight, a Ren'Py SDK, and a checkout of the separate mods repository.
Set the top-level `mods_manifest` in your `vnflight.json` and add this game
under `games` (merge these keys into your existing configuration):

```json
{
  "mods_manifest": "path/to/mods/manifest.json",
  "games": {
    "echoes_of_tomorrow": {
      "name": "Echoes of Tomorrow",
      "launch": "path/to/renpy-sdk/renpy.exe path/to/echoes_of_tomorrow",
      "briefing": "path/to/echoes_of_tomorrow/game_briefing.md",
      "multi_instance": true
    }
  }
}
```

Leave the game's `mods` key absent to use the manifest; `"mods": []` disables
adapters. The installer verifies adapter bytes against manifest SHA-256 hashes.
A hash checks integrity, not publisher identity; use a trusted checkout.

```text
python vnflight.py --yes install-shim echoes_of_tomorrow
python vnflight.py launch echoes_of_tomorrow
```

See vnflight's `docs/USER.md` for the full walkthrough.

## Assets

Regenerate the station map, dome highlight mask, navigation icons, and Marcus
marker from this repository with Python and Pillow:

```sh
python -m pip install Pillow
python tools/render_map.py
```

The renderer resolves input and output paths relative to its own location, so
it also works when invoked from another directory. When changing room geometry,
keep `tools/render_map.py` and `game/screens_game.rpy` in sync.

Artwork was generated with AI tools, including ComfyUI, and selected and edited
for this project. The MIT grant covers project-owned contributions, not a
relicensing of third-party source material. See the third-party notices before
redistributing assets.
