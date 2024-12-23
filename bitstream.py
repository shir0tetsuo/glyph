import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.colors as mcolors
import random
import noise
import os
import uuid

import Components
import Components.loaders
import Components.generators

SavedMaps = Components.loaders.SavedMaps
SavedColors = Components.loaders.SavedColors
SavedGlyphs = Components.loaders.SavedGlyphs

# inspiration & compatible bits
# https://terrafans.xyz/antenna/
# https://terraforms.oolong.lol/terraform
# https://unicode-explorer.com/b/13000

# Cache Resources in Streamlit

if not (os.path.exists('output')):
    os.makedirs('output/')

if "saved_maps" not in st.session_state:
    st.session_state.saved_maps = SavedMaps().maps

saved_maps = st.session_state.saved_maps

if "saved_colors" not in st.session_state:
    st.session_state.saved_colors = SavedColors().maps

saved_colors = st.session_state.saved_colors

if "saved_glyphs" not in st.session_state:
    st.session_state.saved_glyphs = SavedGlyphs().maps

saved_glyphs = st.session_state.saved_glyphs

# Display the heightmap in a text area for editing (Streamlit)
def edit_heightmap(heightmap):
    heightmap_str = '\n'.join([' '.join(map(str, row)) for row in heightmap])
    edited_str = st.text_area('Edit Heightmap', heightmap_str, height=300)

    try:
        # Convert the edited string back to a NumPy array
        edited_heightmap = np.array(
            [list(map(int, row.split())) for row in edited_str.split('\n')]
        )
        if edited_heightmap.shape == heightmap.shape:
            return edited_heightmap
        else:
            st.error(f"Edited heightmap shape must match original: {heightmap.shape}")
            return heightmap
    except Exception as e:
        st.error(f"Error parsing heightmap: {e}")
        return heightmap

# Function to create a preview of the selected colormap
def show_cmap_preview(cmap_name):
    # Create a gradient image to show the colormap
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    gradient = np.vstack((gradient, gradient))

    fig, ax = plt.subplots(figsize=(6, 1))  # Preview size
    ax.set_title(f"Colormap: {cmap_name}")
    ax.imshow(gradient, aspect='auto', cmap=cmap_name)
    ax.set_axis_off()  # Hide axis
    st.sidebar.pyplot(fig)


# Function to generate a 32x32 array of random values between 0 and 9
def generate_array(seed=None):
    np.random.seed(seed)  # Ensure reproducibility with seed
    return np.random.randint(0, 10, size=(32, 32))

def generate_perlin_noise(width, height, scale=10.0, octaves=6, seed=None):
    """Generates a heightmap using Perlin noise with integer values between 0 and 9."""
    shape = (width, height)
    world = np.zeros(shape)

    # Generate Perlin noise and scale it to values between 0 and 9
    for i in range(width):
        for j in range(height):
            # Generate noise value between -1 and 1
            value = noise.pnoise2(i / scale,
                                  j / scale,
                                  octaves=octaves,
                                  persistence=0.5,
                                  lacunarity=2.0,
                                  repeatx=1024,
                                  repeaty=1024,
                                  base=seed)
            # Scale the value to between 0 and 9 and ensure it's an integer
            value = (value + 1) * 4.5  # Maps -1,1 to 0,9
            value = int(value)  # Ensure it's an integer
            
            # Ensure the value is within bounds (0 to 9)
            world[i][j] = max(0, min(9, value))

    return world.astype(np.int32)  # Ensuring the array type is integer (0-9)

# Custom colormap from a list of colors
def custom_colormap(colorHex:list, colorName):
    return mcolors.ListedColormap(colorHex, name=colorName)

# Alternatively, for a gradient
def gradient_colormap(colorHex:list, colorName):
    return mcolors.LinearSegmentedColormap.from_list(colorName, colorHex)

def string_to_heightmap(input_string, height=32, width=32, value_range=(0, 9)):
    """
    Converts a long string into a heightmap (2D array) based on character ASCII values.
    
    Parameters:
    - input_string (str): The input string to convert into a heightmap.
    - height (int): The height (rows) of the output heightmap.
    - width (int): The width (columns) of the output heightmap.
    - value_range (tuple): The range of integer values (min, max) for the heightmap (default is 0-9).
    
    Returns:
    - np.ndarray: A 2D array representing the heightmap with integer values.
    """
    
    # Convert the string to a list of ASCII values (or Unicode code points)
    ascii_values = [ord(c) for c in input_string]
    
    # If the string is too short, repeat it to fill the heightmap
    while len(ascii_values) < height * width:
        ascii_values.extend(ascii_values)  # Repeat the list until it's long enough
    
    # Trim to fit the heightmap size
    ascii_values = ascii_values[:height * width]
    
    # Convert the list of ASCII values into a 2D array (height x width)
    heightmap = np.array(ascii_values).reshape((height, width))
    
    # Map ASCII values to the specified value range (0-9 or other)
    min_val, max_val = value_range
    heightmap = (heightmap - heightmap.min()) / (heightmap.max() - heightmap.min()) * (max_val - min_val)
    heightmap = heightmap.astype(int)  # Ensure the values are integers
    
    return heightmap

color_modes = ['cmap', 'Specified', 'Gradient']
color_mode = st.sidebar.selectbox('Select Coloring Mode', color_modes, index=0)

custom_colors = (True if color_mode != color_modes[0] else False)

if custom_colors:
    color_list = sorted([i for i in saved_colors.keys()])
    selected_custom_color = st.sidebar.selectbox("Choose a custom color file", color_list)

if (color_mode == color_modes[0]):
    cmap_list = ['viridis', 'cividis', 'Reds', 'PuBu', 'Greys', 'Purples', 'Blues', 'Greens', 'YlOrBr', 'YlOrRd', 'YlGnBu', 'BuGn', 'YlGn', 'PuRd', 'bone', 'pink', 'spring', 'summer', 'autumn', 'cool', 'Wistia', 'hot', 'afmhot', 'copper', 'PiYg', 'PRGn', 'Spectral', 'twilight', 'hsv', 'Dark2', 'Pastel1', 'Pastel2', 'plasma', 'inferno', 'magma', 'jet', 'coolwarm', 'YlGnBu', 'tab20c']
    selected_cmap = st.sidebar.selectbox("Choose a colormap", cmap_list)

if (color_mode == color_modes[1]):
    selected_cmap = custom_colormap(saved_colors[selected_custom_color], 'Defined')

if (color_mode == color_modes[2]):
    selected_cmap = gradient_colormap(saved_colors[selected_custom_color], 'Gradient')

show_cmap_preview(selected_cmap)

# TAB DEFINITIONS
tab1, tab2, tab3, tab4 = st.sidebar.tabs(['Glyphs & Font', 'Heightmap', 'Seed', 'Saving'])

show_info = tab1.toggle('Generation Information on Image', False)

glyph_table = saved_glyphs
glyph_opts = [k for k in sorted(glyph_table.keys())]
glyphs_select = tab1.selectbox('Glyph Table', glyph_opts, 8)
glyphs = [i for i in glyph_table[glyphs_select][0]]
tab1.code("".join(glyphs))

# FONT CONTROL
font_path = glyph_table[glyphs_select][1]

font_size = tab1.number_input('Glyph Size', 10,36,glyph_table[glyphs_select][2])

invert_font_colors = tab1.toggle('Invert Glyph Colors', False)

apply_alpha = tab1.toggle('Apply Alpha to Glyphs', False)

hm_opts = ['Unorganized', 'Noise', 'String', 'Template']

hm_select = tab2.selectbox('Heightmap', hm_opts, index=3)

randomize_seed = tab3.toggle('Randomize Seed', True)

more_noise = tab3.toggle('Shift Glyphs', False)

random_seed = random.randint(0,100000)

seed = tab3.number_input('Seed',0,100000, (random_seed if randomize_seed else 42), disabled=(True if randomize_seed else False))

save_image = tab4.toggle('Save Image', False)

name_encode = tab4.toggle('Encode Details as Name', True)

text_input = tab4.text_input('Custom Label', None)

hm_inversion = tab2.toggle('Inversion', False)

hm_blend_noise = tab2.toggle('Blend Noise', False, disabled=(True if hm_select == hm_opts[1] else False))

hm_edit_mode = tab2.toggle('Editor', False)

noise_map = generate_perlin_noise(32, 32, seed=seed)

if (hm_select == hm_opts[0]):
    Heightmap = generate_array(seed)
if (hm_select == hm_opts[1]):
    Heightmap = noise_map
if (hm_select == hm_opts[2]):
    to_height = tab2.text_input('Enter String to convert to Heightmap').strip()
    Heightmap = None
    if len(to_height) != 1024:
        tab2.info('String must be 1024 characters encoded 0-9')
    else:
        Heightmap = string_to_heightmap(to_height)
if (hm_select == hm_opts[3]):
    template_select = tab2.selectbox('Select a template to use', sorted(saved_maps.keys()))
    Heightmap = string_to_heightmap(saved_maps[template_select])

if hm_inversion:
    Heightmap = 9 - Heightmap  # Assuming heightmap values range from 0 to 9

if hm_blend_noise:
    Heightmap = np.where(Heightmap == 0, noise_map, Heightmap)

with st.expander('Data', icon='🛂'):
    if hm_edit_mode:
        Heightmap = edit_heightmap(Heightmap)
    else:
        st.code('\n'.join([' '.join(map(str, row)) for row in Heightmap]))

st.sidebar.markdown('---')
if hm_select == hm_opts[3]:
    selected_template = template_select.replace('.txt','')
else:
    selected_template = 'seed'
cmap_name = (selected_custom_color.replace('.txt','') if custom_colors else selected_cmap)
image_name = tab4.text_input('Image Name', (f'{hm_select}_{selected_template}_{glyphs_select}_{cmap_name}_{seed}.png' if name_encode else 'heatmap_with_symbols_shifted.png'), disabled=(False if save_image and not name_encode else True))

st.sidebar.write(f'Saving is {"Enabled" if save_image else "Disabled"}')

if st.sidebar.button('Stream', icon='🐠'):
    toast = st.toast(f'Generating {seed}..', icon='🐠')
    st.pyplot(Components.generators.create_heatmap_with_symbols(Heightmap, glyphs, seed=(random.randint(0,100000) if more_noise else seed), font_path=font_path, figsize=(16, 16), dpi=300, text=text_input, cmap=selected_cmap, save=save_image, save_name=image_name, display_zone=show_info, custom_cmap=custom_colors, fontsz=font_size, symbol_invert_color=invert_font_colors, symbol_semi_transparent=apply_alpha))
    if save_image:
        toast = st.toast(f'{image_name}', icon='💾️')
    else:
        toast = st.toast(f'Success {seed}', icon='🐠')
    plt.close()