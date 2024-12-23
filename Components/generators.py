import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.colors as mcolors
import random
import noise
import os
import uuid


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
        symbol_semi_transparent=False
    ):
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
        # Save the figure with high resolution (higher dpi)
        plt.savefig('output/'+save_name, dpi=dpi, bbox_inches='tight')  # Save image with larger resolution
    
    return plt
