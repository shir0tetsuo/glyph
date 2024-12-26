import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.colors as mcolors
import noise
from PIL import Image
import os

# Define the Symbol class
class Symbol:
    def __init__(self, symbol, font_path=None):
        self.symbol = symbol
        self.font_path = font_path

    def draw(self, ax, x, y, size=16, cell_value=None, cmap=None, norm=None, invert_color=False, alpha=1.0):  # Reduced font size to 10
        # If a font path is provided, use it; otherwise, default to system font
        font_properties = fm.FontProperties(fname=self.font_path) if self.font_path else None
        
        if invert_color and cell_value is not None and cmap is not None and norm is not None:
            color = cmap(norm(cell_value))
            inverted_color = [1 - c for c in color[:3]] + [color[3]]
            color = inverted_color
        else:
            color = 'black'

        ax.text(x, y, self.symbol, fontsize=size, ha='center', va='center', color=color, fontproperties=font_properties, alpha=alpha)

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
        fontsz:int=16,
        symbol_invert_color=False,
        symbol_semi_transparent=False,
        base_directory = os.getcwd()
    ):

    array = (string_to_heightmap(array) if type(array) == str else array)

    np.random.seed(seed)  # Ensure reproducibility with seed

    # Create a colormap for the heatmap
    if isinstance(cmap, mcolors.ListedColormap):
        cmap = cmap
    else:
        cmap = plt.get_cmap(cmap)
    #cmap = (cmap if custom_cmap else plt.get_cmap(cmap))
    norm = mcolors.Normalize(vmin=0, vmax=9)

    # Calculate the shift based on the seed (to make the symbols shift predictably)
    shift = seed % len(glyphs)  # Calculate the shift based on the seed

    # Create the plot with a larger figsize
    fig, ax = plt.subplots(figsize=figsize)  # Adjusted figsize for better clarity
    
    cax = ax.imshow(array, cmap=cmap, norm=norm)

    # alpha control for symbol
    alpha = 0.7 if symbol_semi_transparent else 1.0

    # Overlay symbols based on the array values and the shift from the seed
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            symbol_idx = (array[i, j] + shift) % len(glyphs)  # Apply the shift to the array value
            symbol = Symbol(glyphs[symbol_idx], font_path=font_path)  # Pick symbol based on the shifted index
            symbol.draw(ax, j, i, fontsz, array[i,j], cmap, norm, symbol_invert_color, alpha)

    # Remove axis labels for a clean view
    ax.axis('off')

    if text:
        ax.text(.94, -0.01, text, ha='center', va='center', fontsize=12, color='gray', transform=ax.transAxes)
    
    if display_zone:
        #ax.text(.1, -0.01, f'{"".join(glyphs)}', ha='center', va='center', fontsize=12, color='gray', fontproperties=(fm.FontProperties(fname=font_path) if font_path else None), transform=ax.transAxes)
        ax.text(.2, -0.01, f'{save_name.replace(".png","")}', ha='center', va='center', fontsize=12, color='gray', transform=ax.transAxes)

    if save:
        output_dir = os.path.join(base_directory, 'output', save_name + ('.png' if not save_name.endswith('.png') else ''))
        # Save the figure with high resolution (higher dpi)
        plt.savefig(output_dir, dpi=dpi, bbox_inches='tight')  # Save image with larger resolution
        print(f"Image saved to: {output_dir}")
    
    return plt


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

def invert_values(heightmap):
    '''Assuming heightmap values range from 0 to 9'''
    heightmap = 9 - heightmap
    return heightmap

def blend_noise(heightmap, noisemap, flagged_int:int):
    return np.where(heightmap == flagged_int, noisemap, heightmap)

def image_to_integer_string(image_path):
    # Open the image
    img = Image.open(image_path)
    
    # Convert the image to grayscale
    img = img.convert('L')
    
    # Resize the image to 32x32
    img = img.resize((32, 32))
    
    # Normalize pixel values to a range of 0-9
    pixel_values = np.array(img)
    normalized_values = (pixel_values / 255 * 9).astype(int)
    
    # Convert the array to a single string of integers
    integer_string = ''.join(map(str, normalized_values.flatten()))
    
    return integer_string