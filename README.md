# glyph
Numpy, Streamlit, Matplotlib Image Generation Kit
![Template_man_Reptiles_Lasersand_70012](https://github.com/user-attachments/assets/272816b5-ec4c-4ab9-a065-03ee68601a94)

# Usage
- This was built and tested on a Linux environment through venv.
- Heightmaps txt contain 1024 integers `(32x32)`
- SavedGlyphs can have `fontdir:str='/usr/fonts/noto'` (example) passed to it to match your installation, see `Components/loaders.py` or existing examples in the `glyphtables` directory.

## Running

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