# Sound Packs

A sound pack is simply a set of 36 MP3 files — one for each letter (a–z) and digit (0–9).

## Creating a Sound Pack

### File naming

Every file must be named exactly as its key, lowercase:

```
a.mp3  b.mp3  c.mp3  ... z.mp3
0.mp3  1.mp3  2.mp3  ... 9.mp3
```

### Recommendations

- **Duration**: 0.1–0.5 seconds per clip works best. Longer clips will overlap at high typing speeds.
- **File size**: Under 100KB per file keeps things snappy.
- **Format**: MP3 (pygame handles most bitrates and sample rates).
- **Normalization**: Try to keep all 36 files at roughly the same volume level. RageType handles volume scaling based on rage level.

### Sound pack ideas

| Pack | Description |
|------|-------------|
| Piano | Each key = a different note (chromatic scale) |
| Cat meows | 36 cat sounds pitched differently |
| Drum kit | Mix of kicks, snares, hats, toms |
| Retro game | 8-bit bleeps and bloops |
| Typewriter | Classic mechanical keyboard sounds |
| Voice clips | Short syllables or exclamations |
| Nature | Birds, rain, wind, leaves |
| Fighting game | Punches, kicks, impacts |

## Installing a Sound Pack

### Method 1: Replace defaults

Copy all 36 files into `sounds/default/`, overwriting the existing ones.

### Method 2: Use custom overrides

Copy files into `sounds/custom/`. These take priority over defaults, so you can override just a few keys while keeping the rest.

### Method 3: Use the dashboard

1. Run `python3 dashboard.py`
2. Open `http://localhost:8000`
3. Click on each key and upload an MP3

## Sharing Sound Packs

Want to share your sound pack with the community?

1. Create a zip file with all 36 MP3s
2. Open a GitHub issue with the title "Sound Pack: [Your Pack Name]"
3. Include a description and optionally a short demo video
4. Attach the zip or link to it

We may feature popular sound packs in the README!