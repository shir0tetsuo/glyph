
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

def print_pattern(arr, glyphs, colors, uuid_str):
	# Print 4x3 pattern with colored backgrounds and black glyphs
	print("\nGenerated Pattern:")
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

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description="Generate a colored glyph pattern from UUID.")
	parser.add_argument('--glyphtable', type=str, help='Name of glyphtable to use')
	parser.add_argument('--cmap', type=str, help='Name of colormap to use')
	parser.add_argument('--seed', type=int, help='Seed for random color assignment')
	parser.add_argument('--rows', type=int, default=3, help='Number of rows in the grid (default: 3)')
	parser.add_argument('--cols', type=int, default=8, help='Number of columns in the grid (default: 8)')
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
	uuid_str = str(uuid.uuid4())
	arr = uuid_to_heightmap(uuid_str, rows=args.rows, cols=args.cols)
	# Assign a random color to each glyph for this run, using seed if provided
	glyph_color_map = {}
	available_colors = color_list.copy()
	if args.seed is not None:
		random.seed(args.seed)
	random.shuffle(available_colors)
	for i, glyph in enumerate(glyphs):
		glyph_color_map[glyph] = available_colors[i % len(available_colors)]
	print_pattern(arr, glyphs, color_list, uuid_str)
