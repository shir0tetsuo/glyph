import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.colors as mcolors
import random
import os

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
    selected_cmap = Components.generators.custom_colormap(saved_colors[selected_custom_color], 'Defined')

if (color_mode == color_modes[2]):
    selected_cmap = Components.generators.gradient_colormap(saved_colors[selected_custom_color], 'Gradient')

Components.generators.show_cmap_preview(selected_cmap)

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

noise_map = Components.generators.generate_perlin_noise(32, 32, seed=seed)

if (hm_select == hm_opts[0]):
    Heightmap = Components.generators.generate_array(seed)
if (hm_select == hm_opts[1]):
    Heightmap = noise_map
if (hm_select == hm_opts[2]):
    to_height = tab2.text_input('Enter String to convert to Heightmap').strip()
    Heightmap = None
    if len(to_height) != 1024:
        tab2.info('String must be 1024 characters encoded 0-9')
    else:
        Heightmap = Components.generators.string_to_heightmap(to_height)
if (hm_select == hm_opts[3]):
    template_select = tab2.selectbox('Select a template to use', sorted(saved_maps.keys()))
    Heightmap = Components.generators.string_to_heightmap(saved_maps[template_select])

if hm_inversion:
    Heightmap = Components.generators.invert_values(Heightmap) # 9 - Heightmap 

if hm_blend_noise:
    Heightmap = Components.generators.blend_noise(Heightmap, noise_map, 0)

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