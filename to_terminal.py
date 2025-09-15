
# Terminal pattern generator from UUID
import uuid
import numpy as np
import os
from Components.loaders import SavedColors, SavedGlyphs

def uuid_to_heightmap(uuid_str):
	parts = str(uuid_str).split('-')
	# Use middle three and last part for more chars: 4+4+4+12 = 24
	chars = ''.join(parts[1:])  # 4,4,4,12 = 24 chars
	vals = []
	for c in chars:
		if c.isdigit():
			vals.append(int(c))
		else:
			v = ord(c.upper()) - ord('A') + 10
			vals.append(v - 7 if v >= 10 else v)
	vals = (vals + [0]*24)[:24]
	arr = np.array(vals).reshape((3,8))  # 3 rows, 8 columns
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
	arr = uuid_to_heightmap(uuid_str)
	# Assign a random color to each glyph for this run, using seed if provided
	glyph_color_map = {}
	available_colors = color_list.copy()
	if args.seed is not None:
		random.seed(args.seed)
	random.shuffle(available_colors)
	for i, glyph in enumerate(glyphs):
		glyph_color_map[glyph] = available_colors[i % len(available_colors)]
	print_pattern(arr, glyphs, color_list, uuid_str)
