# glyph
Numpy, Streamlit, Matplotlib Image Generation Kit
![Template_man_Reptiles_Lasersand_70012](https://github.com/user-attachments/assets/272816b5-ec4c-4ab9-a065-03ee68601a94)

# Usage
- This was built and tested on a Linux environment through venv.
- Heightmaps txt contain 1024 integers `(32x32)`
- SavedGlyphs can have `fontdir:str='/usr/fonts/noto'` (example) passed to it to match your installation, see `Components/loaders.py` or existing examples in the `glyphtables` directory.

## Biomes

Biomes must be formatted in the following manner:

```json
{
    # Weight float sum to 1.0
    "heightmaps": {
        "man": 0.5, 
        "A": 0.5
        }, 
    # Weight float sum to 1.0
    "colormaps": {
        "cividis": 1.0
        }, 
    # Weight float sum to 1.0
    "glyphs": {
        "EgyptDots": 0.5, 
        "EgyptReptiles": 0.5
        }, 
    "quirks": {
        "invert_heightmap": 0.1, # 0.0 - 1.0 -> bool
        "invert_glyphs": false,  # true|false
        "alpha_glyphs": false,   # true|false
        "noise": 0.5,            # 0.0 - 1.0 -> bool
        "gradient": 0.0,         # 0.0 - 1.0 -> bool
    }
}

```

### Adding to Floors

Each floor can have multiple biomes, each with its own weight. The total weight of all biomes must sum to 1.0. Each biome can have its own heightmap, colormap, glyph, and quirks. The bot will randomly select a biome based on the weight of each biome given the seed, and determine the corresponding heightmap, colormap, glyph, and quirks; That information is used to generate an image to give back to the Discord user.

## Running

- The bot has different requirements than the Streamlit `bitstream.py` application.

#### Dependencies
- `numpy`
- `streamlit`
- `matplotlib`
- `noise`

### Linux
(Ubuntu 24.04.1 LTS)

If you haven't already:
```bash
python3 -m venv venv
source venv/bin/activate
pip install streamlit numpy matplotlib noise
```
Otherwise, to run:
```bash
source venv/bin/activate
streamlit run bitstream.py
```

### Windows
It should be fairly straight forward (with typical Python 3.12.3 installations) to get this going, but I no longer own a Windows installation.

## Web Application

Intended to be intuitive, but broken apart to be used in other applications.