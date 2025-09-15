import uuid
import numpy as np
import os
from Components.loaders import SavedColors, SavedGlyphs

# --- Utility Functions ---
def uuid_to_heightmap(uuid_str, rows=3, cols=8):
    """
    Convert a UUID string to a heightmap array of shape (rows, cols).
    If not enough values, fill with random 0-9.
    """
    import random
    parts = str(uuid_str).split('-')
    chars = ''.join(parts[1:])
    vals = []
    for c in chars:
        if c.isdigit():
            vals.append(int(c))
        else:
            v = ord(c.upper()) - ord('A') + 10
            vals.append(v - 7 if v >= 10 else v)
    total = rows * cols
    if len(vals) < total:
        seed_val = sum([ord(x) for x in str(uuid_str)])
        random.seed(seed_val)
        vals += [random.randint(0,9) for _ in range(total - len(vals))]
    vals = vals[:total]
    arr = np.array(vals).reshape((rows, cols))
    return arr

# ANSI color helpers for terminal output
def ansi_color(rgb):
    """Return ANSI escape code for background color from hex string."""
    if rgb.startswith('#'):
        rgb = rgb[1:]
    r, g, b = int(rgb[0:2],16), int(rgb[2:4],16), int(rgb[4:6],16)
    return f"\033[48;2;{r};{g};{b}m"

def reset_color():
    return "\033[0m"

# --- Glyph Grid Construction ---
def build_glyph_grid(arr, glyphs, glyph_values=None):
    """
    Build a grid of glyphs for the pattern.
    If glyph_values is provided, use base16 chars to select glyph indices.
    """
    import random
    rows, cols = arr.shape
    grid = np.empty((rows, cols), dtype=str)
    if glyph_values:
        values = [c for c in glyph_values if c.isalnum()]
        for i in range(rows * cols):
            if i < len(values):
                v = values[i]
                if v.isdigit():
                    idx = int(v)
                else:
                    idx = 10 + ord(v.upper()) - ord('A')
                idx = idx % len(glyphs)
                grid.flat[i] = glyphs[idx]
            else:
                grid.flat[i] = random.choice(glyphs)
    else:
        for i in range(rows):
            for j in range(cols):
                idx = arr[i, j] % len(glyphs)
                grid[i, j] = glyphs[idx]
    return grid

# --- Color Assignment ---
def assign_glyph_colors(glyphs, color_list, color_values=None, seed=None):
    """
    Assign a color to each glyph, optionally using color_values string.
    """
    import random
    available_colors = color_list.copy()
    glyph_color_map = {}
    if color_values:
        values = [c for c in color_values if c.isalnum()]
        for i, glyph in enumerate(glyphs):
            if i < len(values):
                v = values[i]
                if v.isdigit():
                    idx = int(v) % len(available_colors)
                else:
                    idx = (ord(v.upper()) - ord('A') + 10 - 7) % len(available_colors)
                    if idx < 0: idx = 0
                glyph_color_map[glyph] = available_colors[idx]
            else:
                if seed is not None:
                    random.seed(seed + i)
                random.shuffle(available_colors)
                glyph_color_map[glyph] = available_colors[i % len(available_colors)]
    else:
        if seed is not None:
            random.seed(seed)
        random.shuffle(available_colors)
        for i, glyph in enumerate(glyphs):
            glyph_color_map[glyph] = available_colors[i % len(available_colors)]
    return glyph_color_map

# --- Terminal Output ---
def print_pattern(arr_glyphs, glyph_color_map, colors, uuid_str, just_glyphs=False):
    """
    Print the glyph grid to the terminal with colored backgrounds.
    """
    if not just_glyphs:
        print("\nGenerated Pattern:")
    else:
        print('\n')
    for i in range(arr_glyphs.shape[0]):
        row = ""
        for j in range(arr_glyphs.shape[1]):
            symbol = arr_glyphs[i, j]
            color = glyph_color_map[symbol]
            row += f"{ansi_color(color)}\033[30m {symbol}  {reset_color()}"
        print(row)
    print(f"\nUUID: {uuid_str}\n")

# --- PNG Export ---
def export_png(arr_glyphs, font_path, font_size, colors, uuid_str, glyph_color_map, out_path):
    """
    Export the glyph grid as a PNG image with transparent background.
    """
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import matplotlib.font_manager as fm
    rows, cols = arr_glyphs.shape
    fig, ax = plt.subplots(figsize=(cols, rows+1))
    fig.patch.set_alpha(0)
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows+1)
    ax.axis('off')
    ax.set_facecolor('none')
    font_properties = fm.FontProperties(fname=font_path) if font_path else None
    # Draw colored rectangles and glyphs
    for i in range(rows):
        for j in range(cols):
            symbol = arr_glyphs[i, j]
            color = glyph_color_map[symbol]
            rect = mpatches.Rectangle((j, rows-i-0.5), 1, 1, color=color)
            ax.add_patch(rect)
            ax.text(j+0.5, rows-i, symbol, ha='center', va='center', color='black', fontsize=font_size, fontproperties=font_properties)
    # Add UUID at the bottom
    ax.text(cols/2, 0.15, uuid_str, ha='center', va='center', color='gray', fontsize=18)
    plt.savefig(out_path, bbox_inches='tight', dpi=150, transparent=True)
    plt.close(fig)

# --- Main Execution ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate a colored glyph pattern from UUID.")
    parser.add_argument('--glyphtable', type=str, help='Name of glyphtable to use')
    parser.add_argument('--cmap', type=str, help='Name of colormap to use')
    parser.add_argument('--seed', type=int, help='Seed for random color assignment')
    parser.add_argument('--rows', type=int, default=3, help='Number of rows in the grid (default: 3)')
    parser.add_argument('--cols', type=int, default=8, help='Number of columns in the grid (default: 8)')
    parser.add_argument('--just-glyphtable', action='store_true', help='Print only the glyphtable')
    parser.add_argument('--out', type=str, help='Export pattern as PNG to this path')
    parser.add_argument('--uuid', type=str, help='Specify the UUID4 to use for reproducible results')
    parser.add_argument('--shorten_uuid', type=int, help='Shorten the displayed UUID to this length, prefix with U-')
    parser.add_argument('--fsize', type=int, help='Manually specify the font size of the glyphs for PNG export')
    parser.add_argument('--glyph_values', type=str, help='String of base16 values to control which glyph is used in each cell')
    parser.add_argument('--color_values', type=str, help='String of values (0-9, A-F) to control glyph colors')
    args = parser.parse_args()

    # Load resources
    saved_colors = SavedColors().maps
    saved_glyphs = SavedGlyphs().maps

    # Glyphtable selection
    if args.glyphtable and args.glyphtable in saved_glyphs:
        glyph_name = args.glyphtable
    else:
        glyph_name = list(saved_glyphs.keys())[0]
    glyphs, font_path, default_font_size = saved_glyphs[glyph_name]

    # Colormap selection
    if args.cmap and args.cmap in saved_colors:
        color_name = args.cmap
    else:
        color_name = list(saved_colors.keys())[0]
    color_list = saved_colors[color_name]

    # UUID handling
    if args.uuid:
        uuid_full = args.uuid
    else:
        uuid_full = str(uuid.uuid4())
    if args.shorten_uuid:
        uuid_str = 'U-' + ''.join([c.upper() for c in uuid_full if c.isalnum()])[:args.shorten_uuid]
    else:
        uuid_str = uuid_full

    # Build heightmap and glyph grid
    arr = uuid_to_heightmap(uuid_full, rows=args.rows, cols=args.cols)
    arr_glyphs = build_glyph_grid(arr, glyphs, glyph_values=args.glyph_values)

    # Assign colors to glyphs
    glyph_color_map = assign_glyph_colors(glyphs, color_list, color_values=args.color_values, seed=args.seed)

    # Print only glyphtable if requested
    if args.just_glyphtable:
        print_pattern(arr_glyphs, glyph_color_map, color_list, uuid_str, just_glyphs=True)
    else:
        print_pattern(arr_glyphs, glyph_color_map, color_list, uuid_str)

    # Export PNG if requested
    if args.out:
        font_size = args.fsize if args.fsize else default_font_size
        export_png(arr_glyphs, font_path, font_size, color_list, uuid_str, glyph_color_map, args.out)

def generate_glyph_png(
    glyphtable,
    cmap,
    seed=None,
    rows=3,
    cols=8,
    uuid=None,
    shorten_uuid=None,
    fsize=None,
    glyph_values=None,
    color_values=None,
    out_path=None
):
    """
    Generate a PNG image using the same logic as CLI, for Discord bot integration.
    Returns the path to the generated PNG file.
    """
    saved_colors = SavedColors().maps
    saved_glyphs = SavedGlyphs().maps

    # Glyphtable selection
    if glyphtable and glyphtable in saved_glyphs:
        glyph_name = glyphtable
    else:
        glyph_name = list(saved_glyphs.keys())[0]
    glyphs, font_path, default_font_size = saved_glyphs[glyph_name]

    # Colormap selection
    if cmap and cmap in saved_colors:
        color_name = cmap
    else:
        color_name = list(saved_colors.keys())[0]
    color_list = saved_colors[color_name]

    # UUID handling
    if uuid:
        uuid_full = uuid
    else:
        uuid_full = str(uuid.uuid4())
    if shorten_uuid:
        uuid_str = 'U-' + ''.join([c.upper() for c in uuid_full if c.isalnum()])[:shorten_uuid]
    else:
        uuid_str = uuid_full

    # Build heightmap and glyph grid
    arr = uuid_to_heightmap(uuid_full, rows=rows, cols=cols)
    arr_glyphs = build_glyph_grid(arr, glyphs, glyph_values=glyph_values)

    # Assign colors to glyphs
    glyph_color_map = assign_glyph_colors(glyphs, color_list, color_values=color_values, seed=seed)

    # Font size
    font_size = fsize if fsize else default_font_size

    # Output path
    if not out_path:
        out_path = f"/tmp/glyph_{uuid_str}.png"
    export_png(arr_glyphs, font_path, font_size, color_list, uuid_str, glyph_color_map, out_path)
    return out_path
