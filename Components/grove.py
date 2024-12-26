
# Biome <- floor
import os
import json
from . import engine
from . import generators
from . import loaders
import numpy as np
import io

def Px(percent, prefix):
    return loaders.print_progress_bar(percent, 100, prefix=prefix)

class Biome:
    '''Biome class, contains the weights for heightmaps, colormaps, glyphs, and settings for quirks.'''

    def __init__(
            self,
            path:str=os.getcwd(),
            biome_ID:str='DEFAULT',
        ):

        self.biome_ID = biome_ID

        self.path = os.path.join(path, 'biomes', biome_ID+'.json')
        self.DB = self.load_file()

        pass

    @property
    def Glyphs(self) -> dict[str, float]:
        '''dictionary of glyphtable weights for the biome.'''
        return self.DB.get('glyphs', ValueError('No glyphs found in biome.'))
    
    @property
    def Heightmaps(self) -> dict[str, float]:
        '''dictionary of heightmap weights for the biome.'''
        return self.DB.get('heightmaps', ValueError('No heightmaps found in biome.'))
    
    @property
    def Colormaps(self) -> dict[str, float]:
        '''dictionary of colormap weights for the biome, 
        gradient or specific is set by the quirk 'gradient' in quirks.'''
        return self.DB.get('colormaps', ValueError('No colormaps found in biome.'))
    
    @property
    def Quirks(self) -> dict[str, any]:
        return self.DB.get('quirks', ValueError('No quirks found in biome.'))

    def load_file(self):
        if (os.path.exists(self.path)):
            with open(self.path, 'r') as file:
                return json.load(file)
        return {}
    
    def save_file(self):
        with open(self.path, 'w') as file:
            json.dump(self.DB, file)
        return

    def overwrite(self, biome_data:dict):
        '''
        ## `biome_data` example:

        {
            'heightmaps': { 'heightmap1': 0.5, 'heightmap2': 0.5 },
            'colormaps': { 'colormap1': 1.0 },
            'glyphs': { 'glyph1': 0.5, 'glyph2': 0.5 },
            'quirks': { 'invert_heightmap': 0.5, 'invert_glyphs': False, 'alpha_glyphs': False, 'noise': 0.5, 'gradient': 0.0 }
        }
        '''
        self.DB.update(biome_data)
        self.save_file()
        return

# 'floors': [{'biome1':0.5,'biome2':0.5}]
# database of generations -> uuid, owner, floor, seed -> GENERATION DATA
class GroveFloors:
    '''Outlines the floors to pull and use'''

    def __init__(self, path=os.getcwd(), floorfile='floors.json'):

        self.path = path
        self.db_path = os.path.join(path, floorfile)

        self.DB:dict[str, list[dict]] = self.load_file() # with biome weights for each floor
        self.biomes = self.load_biomes()
        '''# Biomes, 
        `name` (Biome_ID+'.json'), containing combination of `weights` for heightmaps, colormaps, glyphs, and settings for quirks.
        Each floor contains a different biome.'''

        pass

    def get_floor_data(self, level:int):
        return self.DB['floors'][int(level)]

    def load_file(self):
        if (os.path.exists(self.db_path)):
            with open(self.db_path, 'r') as file:
                return json.load(file)
        return {}
    
    def save_file(self):
        with open(self.db_path, 'w') as file:
            json.dump(self.DB, file)

    def load_biomes(self):
        biome_files = [os.path.splitext(biome)[0] for biome in os.listdir(os.path.join(self.path, 'biomes'))]
        return {
            biome_ID: Biome(self.path, biome_ID)
            for biome_ID in biome_files
        }
    
    def new_floor(self, biome_weights:dict[str, float]):
        floors = self.DB.get('floors', [])
        floors.append(biome_weights)
        self.DB.update({'floors':floors})
        return self.save_file()
    
def FromSeed(Gf:GroveFloors, level:int, seed, saved_maps:dict[str, int], saved_colors:dict[str, int], saved_glyphs:dict[str, int]):
    '''Return generator details from a given level and seed'''
    Px(5, f'SEEDx{seed}')
    
    biome_weights = Gf.get_floor_data(level) # floor.json biome weights
    selected_biome = Gf.biomes[engine.WeightedDictRandomizer(biome_weights, seed).result()]
    noise = generators.generate_perlin_noise(32, 32, seed=seed)

    Px(15, f'SEEDx{seed}')

    # strings of selections to use to generate the image
    selected_heightmap = engine.WeightedDictRandomizer(selected_biome.Heightmaps, seed).result()
    selected_colormap = engine.WeightedDictRandomizer(selected_biome.Colormaps, seed).result()
    selected_glyphtable = engine.WeightedDictRandomizer(selected_biome.Glyphs, seed).result()

    Heightmap = generators.string_to_heightmap(saved_maps[selected_heightmap])

    Px(30, f'SEEDx{seed}')

    # settings
    biome_settings = selected_biome.Quirks

    InvertHeightmap = engine.BooleanFromSeedWeight(seed, biome_settings.get('invert_heightmap', 0.5))
    AddNoise = engine.BooleanFromSeedWeight(seed, biome_settings.get('noise', 0.5))
    # heightmap modifiers
    if (InvertHeightmap != np.False_):
        Heightmap = generators.invert_values(Heightmap)
    if (AddNoise != np.False_):
        Heightmap = generators.blend_noise(Heightmap, noise, 0)

    Px(40, f'SEEDx{seed}')

    # glyph modifiers
    do_glyph_invert = biome_settings.get('invert_glyphs', False)
    do_glyph_alpha = biome_settings.get('alpha_glyphs', False)

    IS_CUSTOM = (True if selected_colormap in saved_colors.keys() else False)

    # Determine if custom color is gradient or specific
    if (IS_CUSTOM and engine.BooleanFromSeedWeight(seed, biome_settings.get('gradient', 0.5))):
        do_gradient = True
    else:
        do_gradient = False

    Px(50, f'SEEDx{seed}')

    #Heightmap = saved_maps[selected_heightmap]
    Glyphs = [g for g in saved_glyphs[selected_glyphtable][0]]
    Glyphs_fontpath = saved_glyphs[selected_glyphtable][1]
    Glyphs_fontsize = saved_glyphs[selected_glyphtable][2]

    if (IS_CUSTOM == True):
        selected_cmap = (generators.custom_colormap(saved_colors[selected_colormap], 'Gradient') if do_gradient else generators.custom_colormap(saved_colors[selected_colormap], 'Specified'))
    else:
        selected_cmap = selected_colormap

    GenerationName = [
        # .cg = gradient
        # .cs = specific
        # .m  = matplotlib cmap
        selected_colormap+(('.cg' if do_gradient else '.cs') if IS_CUSTOM else '.m'),
        # .i  = invert heightmap
        # .n  = add noise
        selected_heightmap+('.i' if InvertHeightmap else '')+('.n' if AddNoise else ''),
        # .i  = invert glyph
        # .a  = add alpha
        selected_glyphtable+(('.i' if do_glyph_invert else '')+('.a' if do_glyph_alpha else '')),
        str(seed)
    ]

    GENERATION_NAME = '_'.join(GenerationName)

    Px(60, GENERATION_NAME)

    dpi=300

    #print('\n'.join([' '.join(map(str, row)) for row in Heightmap]))
    #print(Glyphs)
    #print(seed)
    #print(Glyphs_fontpath)
    #print(dpi)
    #print(selected_cmap)
    #print(IS_CUSTOM)
    #print(Glyphs_fontsize)
    #print(do_glyph_invert)
    #print(do_glyph_alpha)

    State = generators.create_heatmap_with_symbols(
        array=Heightmap,
        glyphs=Glyphs,
        seed=seed,
        font_path=Glyphs_fontpath,
        figsize=(16, 16),
        dpi=dpi,
        text=f'Level {level}',
        cmap=selected_cmap,
        save=True,
        save_name=GENERATION_NAME,
        display_zone=True,
        custom_cmap=IS_CUSTOM,
        fontsz=Glyphs_fontsize,
        symbol_invert_color=do_glyph_invert,
        symbol_semi_transparent=do_glyph_alpha,
        base_directory=Gf.path
    )

    Px(80, GENERATION_NAME)

    # write png to IO buffer
    png_buffer = io.BytesIO()
    State.savefig(png_buffer, format='PNG', dpi=dpi, bbox_inches='tight')

    Px(95, GENERATION_NAME)
    State.close()

    return (GENERATION_NAME, png_buffer)