# Terminal pattern generator from UUID
import uuid
import numpy as np
import os
from Components.loaders import SavedColors, SavedGlyphs

def uuid_to_heightmap(uuid_str, rows=3, cols=8):
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
	# If not enough values, fill with random 0-9
	if len(vals) < total:
		# Use a seed based on uuid for reproducibility
		seed_val = sum([ord(x) for x in str(uuid_str)])
		random.seed(seed_val)
		vals += [random.randint(0,9) for _ in range(total - len(vals))]
	vals = vals[:total]
	arr = np.array(vals).reshape((rows, cols))
	return arr

def ansi_color(rgb):
	# Convert hex color to ANSI escape code for background
	if rgb.startswith('#'):
		rgb = rgb[1:]
	r, g, b = int(rgb[0:2],16), int(rgb[2:4],16), int(rgb[4:6],16)
	return f"\033[48;2;{r};{g};{b}m"

def reset_color():
	return "\033[0m"

def print_pattern(arr, glyphs, colors, uuid_str, just_glyphs=False):
	if not just_glyphs:
		print("\nGenerated Pattern:")
	else:
		print('\n')
	for i in range(arr.shape[0]):
		row = ""
		for j in range(arr.shape[1]):
			idx = arr[i,j] % len(glyphs)
			symbol = glyphs[idx]
			color = glyph_color_map[symbol]
			# Black glyph on colored background, space also colored
			row += f"{ansi_color(color)}\033[30m {symbol}  {reset_color()}"
		print(row)
	print(f"\nUUID: {uuid_str}\n")

def export_png(arr, glyphs, colors, uuid_str, glyph_color_map, out_path):
	import matplotlib.pyplot as plt
	import matplotlib.patches as mpatches
	import matplotlib.font_manager as fm
	rows, cols = arr.shape
	fig, ax = plt.subplots(figsize=(cols, rows+1))
	fig.patch.set_alpha(0)
	ax.set_xlim(0, cols)
	ax.set_ylim(0, rows+1)
	ax.axis('off')
	ax.set_facecolor('none')
	# Use font from glyphtable
	font_path = None
	font_size = 32
	if hasattr(export_png, 'font_path'):
		font_path = export_png.font_path
	if hasattr(export_png, 'font_size'):
		font_size = export_png.font_size
	font_properties = fm.FontProperties(fname=font_path) if font_path else None
	# Draw colored rectangles and glyphs
	for i in range(rows):
		for j in range(cols):
			idx = arr[i, j] % len(glyphs)
			symbol = glyphs[idx]
			color = glyph_color_map[symbol]
			rect = mpatches.Rectangle((j, rows-i-0.5), 1, 1, color=color)
			ax.add_patch(rect)
			ax.text(
				# Symbol X
				j+0.5,
				# Symbol Y 
				rows-i, 
				symbol, ha='center', va='center', color='black', fontsize=font_size, fontproperties=font_properties)
	# Add UUID at the bottom
	ax.text(cols/2, 0.15, uuid_str, ha='center', va='center', color='gray', fontsize=18)
	plt.savefig(out_path, bbox_inches='tight', dpi=150, transparent=True)
	plt.close(fig)

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
	args = parser.parse_args()

	saved_colors = SavedColors().maps
	saved_glyphs = SavedGlyphs().maps

	# Glyphtable selection
	if args.glyphtable and args.glyphtable in saved_glyphs:
		glyph_name = args.glyphtable
	else:
		glyph_name = list(saved_glyphs.keys())[0]
	glyphs, font_path, font_size = saved_glyphs[glyph_name]

	# Colormap selection
	if args.cmap and args.cmap in saved_colors:
		color_name = args.cmap
	else:
		color_name = list(saved_colors.keys())[0]
	color_list = saved_colors[color_name]

	import random
	if args.uuid:
		uuid_full = args.uuid
	else:
		uuid_full = str(uuid.uuid4())
	# Shorten UUID if requested
	if args.shorten_uuid:
		# Remove dashes, take first N chars, prefix with U-
		uuid_str = 'U-' + ''.join([c.upper() for c in uuid_full if c.isalnum()])[:args.shorten_uuid]
	else:
		uuid_str = uuid_full
	arr = uuid_to_heightmap(uuid_full, rows=args.rows, cols=args.cols)
	# Assign a random color to each glyph for this run, using seed if provided
	glyph_color_map = {}
	available_colors = color_list.copy()
	if args.seed is not None:
		random.seed(args.seed)
	random.shuffle(available_colors)
	for i, glyph in enumerate(glyphs):
		glyph_color_map[glyph] = available_colors[i % len(available_colors)]

	# Print only glyphtable if requested
	if args.just_glyphtable:
		print_pattern(arr, glyphs, color_list, uuid_str, just_glyphs=True)
	else:
		print_pattern(arr, glyphs, color_list, uuid_str)

	# Export PNG if requested
	if args.out:
		# Pass font_path and font_size from glyphtable to export_png
		export_png.font_path = font_path
		if args.fsize:
			export_png.font_size = args.fsize
		else:
			export_png.font_size = font_size
		export_png(arr, glyphs, color_list, uuid_str, glyph_color_map, args.out)
