# Third-Party Asset Notices

The root MIT license covers project-owned contributions. Third-party source
assets retain their original licenses; they are not relicensed under MIT.

## Fonts

- `game/gui/fonts/Inconsolata-Regular.ttf`: Inconsolata Project Authors,
  SIL Open Font License 1.1; see `licenses/Inconsolata-OFL.txt`.
- `game/gui/fonts/JetBrainsMono-Regular.ttf`: JetBrains Mono Project Authors,
  SIL Open Font License 1.1; see `licenses/JetBrainsMono-OFL.txt`.

## Music Samples

Music incorporates CC0 material from the
[Versilian Community Sample Library](https://github.com/sgossner/VCSL) and
[VSCO 2 Community Edition](https://github.com/sgossner/VSCO-2-CE).
Their license texts are retained in `licenses/`.

## Title Theme

`game/audio/music/title/eot_title_long_night.ogg`. Title theme: composed
in-house from the game's own palette (procedural station tones and warm bass,
ElevenLabs sound-effect auditions, VSCO-2-CE piano, CC0). Build source:
`experiments/echoes_music_v46_title` (private provenance records).

## Aurora Ending Cue

`game/audio/music/codas_v44/eot_ending_aurora_still_array.ogg`. Composed
in-house from the game's own palette (procedural warm bass and station tones,
VSCO-2-CE cello, ElevenLabs air pad audition; CC0 sample library). Build
source: `experiments/echoes_music_v46_title` (private provenance records). It
replaces the earlier v44 Aurora coda.

## Recorded Sound Sources

The sound-effect build records these Freesound sources as CC0 1.0:

- [Wind by kyles](https://freesound.org/people/kyles/sounds/450143/).
- [Lab ambience by SoundDesignForYou](https://freesound.org/people/SoundDesignForYou/sounds/646682/).
- [Keyboard by Breviceps](https://freesound.org/people/Breviceps/sounds/447909/).
- [Mug by squidge316](https://freesound.org/people/squidge316/sounds/404922/).
- [Generator by qubodup](https://freesound.org/people/qubodup/sounds/189896/).
- [Metal by squarfington](https://freesound.org/people/squarfington/sounds/815606/).
- [Rope by vestibule-door](https://freesound.org/people/vestibule-door/sounds/664929/).

Recordings were edited, mixed, and encoded for the game.
[CC0 legal text](https://creativecommons.org/publicdomain/zero/1.0/legalcode.en).
These credits do not imply endorsement.

## Provenance

Original procedural samples, including the synthesized industrial timbres,
were generated with ChatGPT 5.6 Sol. Original synthesis is distinct from the
third-party recordings and sample-library material credited above; a model
credit does not replace source-sample attribution.

Some music and wind assets use ElevenLabs-generated material obtained under a
commercial plan. The MIT grant applies to project-owned contributions; it does
not relicense third-party source samples or expand upstream rights, and
standalone redistribution rights for source samples have not been
independently reviewed.

Every shipped audio file maps to a retained output or a build-source reference
in the project's records. That is a provenance trail, not a reproducible-build
proof or a legal audit.
