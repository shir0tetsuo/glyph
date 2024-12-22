import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.colors as mcolors
import random
import noise
import os
import uuid

# inspiration & compatible bits
# https://terrafans.xyz/antenna/
# https://terraforms.oolong.lol/terraform
# https://unicode-explorer.com/b/13000

class SavedMaps:

    def __init__(self):

        path = os.getcwd()

        self.path = os.path.join(path, 'heightmaps')

        self.items = [item for item in next(os.walk(self.path))[2]]

        pass
    
    def read_file_as_string(self, file_path):
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            return f"Error: The file at {file_path} was not found."
        except Exception as e:
            return f"Error: {e}"
    
    @property
    def maps(self):
        return {item:self.read_file_as_string(os.path.join(self.path, item)) for item in self.items}

if "saved_maps" not in st.session_state:
    st.session_state.saved_maps = SavedMaps().maps

saved_maps = st.session_state.saved_maps

class SavedColors:

    def __init__(self):

        path = os.getcwd()

        self.path = os.path.join(path, 'colors')

        self.items = [item for item in next(os.walk(self.path))[2]]

        pass

    def read_file_as_list(self, file_path):
        '''Returns list of lines from file (UTF-8).'''
        with open(file_path, 'r', encoding='UTF-8') as file:
            return [line.strip() for line in file]
    
    @property
    def maps(self):
        return {item:self.read_file_as_list(os.path.join(self.path, item)) for item in self.items}

if "saved_colors" not in st.session_state:
    st.session_state.saved_colors = SavedColors().maps

saved_colors = st.session_state.saved_colors

# Display the heightmap in a text area for editing
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

# Create a function to generate the heatmap and overlay symbols
def create_heatmap_with_symbols(
        array,                     
        glyphs, 
        seed=None, 
        font_path=None, 
        figsize=(16, 16), 
        dpi=300, 
        text=None, 
        cmap='viridis',
        save:bool=True,
        save_name='heatmap_with_symbols_shifted.png',
        display_zone:bool=False,
        custom_cmap:bool=False,
        fontsz:int=16):
    np.random.seed(seed)  # Ensure reproducibility with seed

    # Create a colormap for the heatmap
    cmap = (cmap if custom_cmap else plt.get_cmap(cmap))
    norm = mcolors.Normalize(vmin=0, vmax=9)

    # Calculate the shift based on the seed (to make the symbols shift predictably)
    shift = seed % len(glyphs)  # Calculate the shift based on the seed

    # Create the plot with a larger figsize
    fig, ax = plt.subplots(figsize=figsize)  # Adjusted figsize for better clarity
    
    # Display the heatmap
    cax = ax.imshow(array, cmap=cmap, norm=norm)

    # Overlay symbols based on the array values and the shift from the seed
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            symbol_idx = (array[i, j] + shift) % len(glyphs)  # Apply the shift to the array value
            symbol = Symbol(glyphs[symbol_idx], font_path=font_path)  # Pick symbol based on the shifted index
            symbol.draw(ax, j, i, fontsz)

    # Remove axis labels for a clean view
    ax.axis('off')

    if text:
        ax.text(.94, -0.01, text, ha='center', va='center', fontsize=12, color='gray', transform=ax.transAxes)
    
    if display_zone:
        #ax.text(.1, -0.01, f'{"".join(glyphs)}', ha='center', va='center', fontsize=12, color='gray', fontproperties=(fm.FontProperties(fname=font_path) if font_path else None), transform=ax.transAxes)
        ax.text(.2, -0.01, f'{save_name.replace(".png","")}', ha='center', va='center', fontsize=12, color='gray', transform=ax.transAxes)

    if save:
        # Save the figure with high resolution (higher dpi)
        plt.savefig('output/'+save_name, dpi=dpi, bbox_inches='tight')  # Save image with larger resolution
    
    # Show the plot
    #plt.show()
    st.pyplot(plt)

    plt.close()

# Function to generate a 32x32 array of random values between 0 and 9
def generate_array(seed=None):
    np.random.seed(seed)  # Ensure reproducibility with seed
    return np.random.randint(0, 10, size=(32, 32))

# Define the Symbol class
class Symbol:
    def __init__(self, symbol, font_path=None):
        self.symbol = symbol
        self.font_path = font_path

    def draw(self, ax, x, y, size=16):  # Reduced font size to 10
        # If a font path is provided, use it; otherwise, default to system font
        font_properties = fm.FontProperties(fname=self.font_path) if self.font_path else None
        ax.text(x, y, self.symbol, fontsize=size, ha='center', va='center', color='black', fontproperties=font_properties)

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


tab1, tab2, tab3, tab4 = st.sidebar.tabs(['Glyphs & Font', 'Heightmap', 'Seed', 'Saving'])

show_info = tab1.toggle('Show Info', False)

manual_glyphs = tab1.toggle('Manual Glyphs', False)

fontdir = '/usr/share/fonts/truetype/noto/'
SET_hieroglyphs = fontdir+'NotoSansEgyptianHieroglyphs-Regular.ttf'
SET_LinearA = fontdir+'NotoSansLinearA-Regular.ttf'
SET_Kharoshthi = fontdir+'NotoSansKharoshthi-Regular.ttf'
SET_Osmanya = fontdir+'NotoSansOsmanya-Regular.ttf'
SET_Runic = fontdir+'NotoSansRunic-Regular.ttf'
SET_Brahmi = fontdir+'NotoSansBrahmi-Regular.ttf'
SET_Coptic = fontdir+'NotoSansCoptic-Regular.ttf'
SET_Georgian = fontdir+'NotoSansGeorgian-Regular.ttf'
SET_Glagolitic = fontdir+'NotoSansGlagolitic-Regular.ttf'
SET_Lepcha = fontdir+'NotoSansLepcha-Regular.ttf'
SET_Lycian = fontdir+'NotoSansLycian-Regular.ttf'
SET_PhagsPa = fontdir+'NotoSansPhagsPa-Regular.ttf'
SET_Tifinagh = fontdir+'NotoSansTifinagh-Regular.ttf'
SET_Yi = fontdir+'NotoSansYi-Regular.ttf'
SET_Japanese = fontdir+'NotoSansJP-Regular.ttf'
SET_Korean = fontdir+'NotoSansKR-Regular.ttf'
SET_barcode39 = fontdir+'LibreBarcode39-Regular.ttf'
SET_barcode128 = fontdir+'LibreBarcode128-Regular.ttf'
SET_Yarndings = fontdir+'Yarndings12-Regular.ttf'
SET_RegEmoji = fontdir+'NotoEmoji-Regular.ttf'
SET_Myanmar = fontdir+'NotoSansMyanmar-Regular.ttf'

if manual_glyphs:
    glyph_raw = tab1.text_input('Glyphs', '𓋴𓇋𓆗𓅱𓆉𓎡𓍯𓃥𓃣𓈖𓇋𓃢𓃦')
    glyphs_select = "Manual"
    glyphs = [i for i in glyph_raw]
else:
    glyph_table = {
        'Egyptian1': ['𓂧𓆑𓏏𓎛𓋴𓇋𓌳𓃀𓆗𓆀𓅱𓆠𓆈𓆉𓎡𓍯𓃥𓃣𓈖𓇋𓃢𓃦', SET_hieroglyphs],
        'Egyptian2': ['𓆝𓍝𓇋𓃣𓍚𓏢𓐤𓌬𓆣𓆥𓆗𓆏𓆋𓄇𓃕𓆉𓅱', SET_hieroglyphs],
        'Egyptian3': ['𓆗𓃾𓄁𓄂𓄃𓄝𓅜𓆈𓆤', SET_hieroglyphs],
        'Egyptian4': ['𓋾𓋴𓍝𓋹𓋿𓌀𓋻𓋘𓌏𓌪𓍃𓎸𓎶𓏋𓏢', SET_hieroglyphs],
        'Jackals1': ['𓃢𓃦𓃥𓃣𓁢𓃤𓃧𓃨', SET_hieroglyphs],
        'Jackals2': ['𓃢𓃦𓃥𓃣𓇌', SET_hieroglyphs],
        'Reptiles': ['𓆈𓆉𓆊𓆌𓆏𓆇𓆑𓆓𓆗𓆙𓆚𓆘', SET_hieroglyphs],
        'Egyptian5': ['𓁴𓁢𓊽𓎸𓂀𓃠𓃬𓃭𓃮𓄂𓆞𓉈𓄇', SET_hieroglyphs],
        'Egyptian6': ['𓀫𓁀𓁛𓃗𓃯𓃰𓅐𓆈𓆏𓆗𓆝𓊝𓍝𓆧', SET_hieroglyphs],
        'EmojiStars': ['💫⭐🌟✨', SET_RegEmoji],
        'EmojiHearts': ['💘💕💝🤍💗🧡❤💜💛🖤💞💓🤎💙💚', SET_RegEmoji],
        'EmojiEyeskull': ['👁︎🦴🩸💔☠︎💀🪦', SET_RegEmoji],
        'EmojiWeWantYou': ['🫵💪👍👁︎🖖👋🫱🙏🫴', SET_RegEmoji],
        'EmojiNature1': ['🥀🌺🌱🍄💮🍀☀︎🍃🪵🍁', SET_RegEmoji],
        'EmojiMoon': ['🌑🌒🌓🌔🌕⭐🌖🌗✨🌘',SET_RegEmoji],
        'EmojiKeys': ['🔒🗝︎🔑🟪', SET_RegEmoji],
        'EmojiSea': ['🦐🦞🛥︎🪝🪸🦀🛟🛶🦑🦩🐟⛵🐙🦈🐠🐋', SET_RegEmoji],
        'EmojiExcl': ['❕‼︎❗🔶⁉︎❔❓', SET_RegEmoji],
        'EmojiBetterWorld': ['♻︎🚯🌐⚕︎☮︎♥︎🔆🚭☯︎💲🎼📴', SET_RegEmoji],
        'EmojiScience': ['🧲📡🗜︎🛰︎🔬⛏︎⚗︎💎🕶︎📖📗📏', SET_RegEmoji],
        'EmojiUnbox': ['📦📰✉︎🎋💽🎫📖⚖︎🧾', SET_RegEmoji],
        'EmojiSpiritual': ['🌨︎⭐🔥🍂✨🌕⚕︎🎋🍄🗡︎🪄🔮🪦🪬📿🧿🐾', SET_RegEmoji],
        'Fish': ['𓆛𓆜𓆝𓆞𓆟𓆡𓆠𓅻𓈖𓆢', SET_hieroglyphs],
        'Birds': ['𓄿𓅀𓅱𓅷𓅾𓅟𓅮𓅙𓅰𓅚𓅞𓅪𓅜𓅛𓅘𓅓𓅔𓅃𓅂', SET_hieroglyphs],
        'Deities': ['𓁛𓁠𓁦𓁥𓁮𓁭𓁤𓁩𓁳𓁴𓁧𓁨𓁱𓁣𓁚𓁫𓁟𓁢𓁵𓁜', SET_hieroglyphs],
        'Yd1': ['oapsnteylqr', SET_Yarndings],
        'Barcode39': ['abcdefghijklmnopqrstuvwxyz123456789', SET_barcode39],
        'Barcode128': ['abcdefghijklmnopqrstuvwxyz123456789', SET_barcode128],
        'Dots': ['𓃉𓃊𓃋𓃌𓃍𓃎𓃏𓃐𓃑', SET_hieroglyphs],
        'LinearA1': ['𐘁𐘂𐘃𐚬𐚝𐛽𐜥𐚟𐛭𐛰𐛉𐛎𐜎𐝡𐘄𐛊𐛬𐛼𐝦𐛸𐛿𐚣𐛻𐘅𐘇𐝠𐘈𐘉𐝧𐘋𐛪𐚷𐘌𐚞𐛍𐙈𐚽𐘖𐛋𐘍𐘎𐘏𐘑𐘕𐘓𐘝𐘮𐚲𐙳𐙍𐙽𐙻𐘔𐘐𐚓𐙇', SET_LinearA],
        'LinearA2': ['𐚟𐚳𐛞𐘝𐛒𐘋𐚅𐙈𐝧𐛃𐙟𐙳', SET_LinearA],
        'LinearA3': ['𐚁𐘋𐛊𐘑𐚷𐘠𐛞𐘥𐚚𐛤𐙽𐙰𐛂𐙲𐙶𐚌', SET_LinearA],
        'K1': ['𐨲𐨒𐨱𐨜𐨖𐨳𐨫𐨕𐨀𐨓𐨥', SET_Kharoshthi],
        'Osmanyan1': ['𐒁𐒂𐒌𐒍𐒋𐒄𐒎𐒝𐒐𐒙𐒑𐒒𐒊𐒕𐒈𐒓𐒉𐒛𐒗𐒏𐒅',SET_Osmanya],
        'Runic1': ['ᚠᚤᚧᚿᚡᛥᛯᛟᚨᛰᚥᛜᛩᚩᛮᛵᛢᚭᛳᛄᛎᛞᛤᛖᛉᛸᚾᛒᛏᚮᚺᚦᛗᚻᛃᛈᛅᛴᛇᚯᚰᚱᛱᚼᚴᚵᚷᚢᚹᚶᚬᚲᚳ',SET_Runic],
        'Brahmi1': ['𑀀𑀁𑀂𑀃𑀄𑀅𑀆𑀇𑀈𑀉𑀊𑀋𑀌𑀍𑀎𑀏𑀐𑀑𑀒𑀓𑀔𑀕𑀖𑀗𑀘𑀙𑀚𑀛𑀜𑀝𑀞𑀟𑀠𑀡𑀢𑀣𑀤𑀥𑀦𑀧𑀨𑀩𑀪𑀫𑀬𑀭𑀮𑀯𑀰𑀱𑀲𑀳𑀴𑀵𑀶𑀷𑀸𑀹𑀺𑀻𑀼𑀽𑀾𑀿𑁀𑁁𑁂𑁃𑁄𑁅𑁆𑁇𑁈', SET_Brahmi],
        'Coptic1': ['ⲀⲁⲂⲃⲄⲅⲆⲇⲈⲉⲊⲋⲌⲍⲎⲏⲐⲑⲒⲓⲔⲕⲖⲗⲘⲙⲚⲛⲜⲝⲞⲟⲠⲡⲢⲣⲤⲥⲦⲧⲨⲩⲪⲫⲬⲭⲮⲯⲰⲱⲲⲳⲴⲵⲶⲷⲸⲹⲺⲻⲼⲽⲾⲿⳀⳁⳂⳃⳄⳅⳆⳇⳈⳉⳊⳋⳌⳍⳎⳏⳐⳑⳒⳓⳔⳕⳖⳗⳘⳙⳚⳛⳜⳝⳞⳟⳠⳡⳢⳣⳤ⳥⳦⳧⳨⳩⳪', SET_Coptic],
        'Coptic2': ['ⲺⲻⲼⲽⲾⲿⳀⳁⳂⳃⳄⳅⳆⳇⳈⳉⳊⳋⳌⳍⳎⳏⳐⳑⳒⳓⳔⳕⳖⳗⳘⳙⳚⳛⳜⳝⳞⳟⳠⳡⳢⳣⳤ⳥⳦⳧⳨⳩⳪', SET_Coptic],
        'Coptic3': ['ⲀⲁⲂⲃⲄⲅⲆⲇⲈⲉⲊⲋⲌⲍⲎⲏⲐⲑⲒⲓⲔⲕⲖⲗⲘⲙⲚⲛⲜⲝⲞⲟⲠⲡⲢⲣⲤⲥⲦⲧⲨⲩⲪⲫⲬⲭⲮⲯⲰⲱⲲⲳⲴⲵⲶⲷⲸⲹ', SET_Coptic],
        'Georgian1': ['ႠႡႢႣႤႥႦႧႨႩႪႫႬႭႮႯႰႱႲႳႴႵႶႷႸႹႺႻႼႽႾႿჀჁჂჃჄჅაბგდევზთიკლმნოპჟრსტუფქღყშჩცძწჭხჯჰჱჲჳჴჵჶჷჸჹჺ჻ჼ', SET_Georgian],
        'Glagolitic1': ['ⰀⰁⰂⰃⰄⰅⰆⰇⰈⰉⰊⰋⰌⰍⰎⰏⰐⰑⰒⰓⰔⰕⰖⰗⰘⰙⰚⰛⰜⰝⰞⰟⰠⰡⰢⰣⰤⰥⰦⰧⰨⰩⰪⰫⰬⰭⰮⰰⰱⰲⰳⰴⰵⰶⰷⰸⰹⰺⰻⰼⰽⰾⰿⱀⱁⱂⱃⱄⱅⱆⱇⱈⱉⱊⱋⱌⱍⱎⱏ', SET_Glagolitic],
        'Glagolitic2': ['ⰀⰁⰂⰃⰄⰅⰆⰇⰈⰉⰊⰋⰌⰍⰎⰏⰐⰑⰒⰓⰔⰕⰖⰗⰘⰙⰚⰛⰜⰝⰞⰟⰠⰡⰢⰣⰤⰥⰦⰧⰨⰩⰪⰫⰬⰭⰮ', SET_Glagolitic],
        'Glagolitic3': ['ⰰⰱⰲⰳⰴⰵⰶⰷⰸⰹⰺⰻⰼⰽⰾⰿⱀⱁⱂⱃⱄⱅⱆⱇⱈⱉⱊⱋⱌⱍⱎⱏ', SET_Glagolitic],
        'Lepcha1': ['ᰀᰁᰂᰃᰄᰅᰆᰇᰈᰉᰊᰋᰌᰍᰎᰏᰐᰑᰒᰓᰔᰕᰖᰗᰘᰙᰚᰛᰜᰝᰞᰟᰠᰡᰢ', SET_Lepcha],
        'Lepcha2': ['᰻᰼᰽᰾᰿᱀᱁᱂᱃᱄᱅᱆᱇᱈᱉ᱍᱎᱏ', SET_Lepcha],
        'Lycian1': ['𐊀𐊁𐊂𐊃𐊄𐊅𐊆𐊇𐊈𐊉𐊊𐊋𐊌𐊍𐊎𐊏𐊐𐊑𐊒𐊓𐊔𐊕𐊖𐊗𐊘𐊙𐊚𐊛𐊜', SET_Lycian],
        'Phags-Pa1': ['ꡀꡁꡂꡃꡄꡅꡆꡇꡈꡉꡊꡋꡌꡍꡎꡏꡐꡑꡒꡓꡔꡕꡖꡗꡘꡙꡚꡛꡜꡝꡞꡟꡠꡡꡢꡣꡤꡥꡦꡧꡨꡩꡪꡫꡬꡭꡮꡯꡰꡱꡲꡳ꡴꡵꡶ꡟ꡷', SET_PhagsPa],
        'Tif1': ['ⴰⴱⴲⴳⴴⴵⴶⴷⴸⴹⴺⴻⴼⴽⴾⴿⵀⵁⵂⵃⵄⵅⵆⵇⵈⵉⵊⵋⵌⵯ⵰ⵍⵎⵏⵐⵑⵒⵓⵔⵕⵖⵗⵘⵙⵚⵛⵜⵝⵞⵟⵠⵡⵢⵣⵤⵥⵦⵧ', SET_Tifinagh],
        'Yi1': ['ꀀꀁꀂꀃꀄꀅꀆꀇꀈꀉꀊꀋꀌꀍꀎꀏ', SET_Yi],
        'Yi2': ['ꀐꀑꀒꀓꀔꀕꀖꀗꀘꀙꀚꀛꀜꀝ', SET_Yi],
        'Yi3': ['ꀞꀟꀠꀡꀢꀣꀤꀥꀦꀧꀨꀩꀪꀫ', SET_Yi],
        'JpBasic': ['あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん', SET_Japanese],
        'JpV_sVHir': ['がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ', SET_Japanese],
        'JpPronounciations': ['ぁぃぅぇぉっゃゅょ', SET_Japanese],
        'JpKanji1': ['日月山川人学車家本大愛海食心書', SET_Japanese],
        'JpPunctuation': ['、。〆〤「」『』♪★♨〒', SET_Japanese],
        'JpCJK1': ['青年水火木金土天月生川石', SET_Japanese],
        'JpFamilyTimeDir': ['道手信力大天国母父子女名時明心', SET_Japanese],
        'JpNatureGeography': ['山川海島森林花鳥動物風雨雷', SET_Japanese],
        'JpActionsVerbs': ['行見る書話食飲買歩話教学遊', SET_Japanese],
        'JpAbstractEmotion': ['愛怒悲楽幸不安恐怖希望悲痛悲惨', SET_Japanese],
        'JpTimeAndSpace': ['昼夜朝晩月年分秒速遅間前後', SET_Japanese],
        'JpPolitical': ['政府国民議会法政民主共産資本', SET_Japanese],
        'JpBodyHealth': ['体心眼耳口鼻手足頭命病', SET_Japanese],
        'JpSeas': ['海潮波深海海底漁海岸', SET_Japanese],
        'JpSeasVerbs': ['漁る浮かぶ泳ぐ',SET_Japanese],
        'JpSeasCombined': ['海潮波漁る浮かぶ泳ぐ深海海底漁海岸',SET_Japanese],
        'JpSoulSpirit': ['魂宵頭霊体光話白川命闇名土天月心後水法幸火信森海楽風林愛間怒銀悲波銅金星', SET_Japanese],
        'Kr1': ['기다로동픈템랍쪽찬셨충맞완', SET_Korean],
        'Myanmar1': ['ꧦꧩꩲꩳꩡဝ꩸꩹ႀၹꩭꧪꧫဋကꧣꧨၮꧠ', SET_Myanmar],
        'Myanmar2': ['ဪဩႀꩲၹꩭꩺ', SET_Myanmar]

    }
    glyph_opts = [k for k in sorted(glyph_table.keys())]
    glyphs_select = tab1.selectbox('Glyph Table', glyph_opts, 8)
    glyphs = [i for i in glyph_table[glyphs_select][0]]
    tab1.code("".join(glyphs))

# FONT CONTROL
font_path = (tab1.text_input('Fonts',SET_hieroglyphs) if manual_glyphs else glyph_table[glyphs_select][1])

font_size = tab1.number_input('Glyph Size', 10,36,16)

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
    create_heatmap_with_symbols(Heightmap, glyphs, seed=(random.randint(0,100000) if more_noise else seed), font_path=font_path, figsize=(16, 16), dpi=300, text=text_input, cmap=selected_cmap, save=save_image, save_name=image_name, display_zone=show_info, custom_cmap=custom_colors, fontsz=font_size)