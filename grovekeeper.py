import discord
from discord.ext import commands
from discord import app_commands
import json
import sys
import os
from datetime import datetime

import Components
import Components.engine
import Components.loaders
import Components.generators
import Components.grove

saved_maps = Components.loaders.SavedMaps().maps
saved_colors = Components.loaders.SavedColors().maps
saved_glyphs = Components.loaders.SavedGlyphs().maps

GROVEFLOORS = Components.grove.GroveFloors()

__version__ = 'v1.0.1'

# useful
# https://message.style/app/tools/colored-text

def read_token_from_config():
    try:
        with open('.token', 'r') as file:
            token = file.read().strip()  # Read the token value and remove any leading/trailing whitespaces
        return token
    except FileNotFoundError:
        print("Error: File '.token' not found.")
        return None
    
TOKEN = read_token_from_config()

bot_name = 'Grovekeeper'
bot_oper = '303309686264954881'

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="/", intents=intents)


reply_embed_json = {
    "title": "Floor #X",
    "color": 10217450,
    "timestamp": (datetime.now()).isoformat(),
    #"url": "https://github.com/shir0tetsuo",
    "footer": {
        "text": f"v{__version__}",
    }
}
def_reply_embed = reply_embed = discord.Embed().from_dict(reply_embed_json)

@client.event
async def on_ready():
    print(f'✨ [{__version__}] {bot_name} Ready')
    await client.tree.sync()

@client.hybrid_command(description="Developer Test Command")
@app_commands.describe(passing_number="Callback Test")
async def dtc1(ctx:commands.context.Context, passing_number):
    print(ctx)
    await ctx.send(f'{ctx.message.author.mention} {passing_number}', ephemeral=True)
@client.hybrid_command(description="Developer Test Command (Dream Test)")
async def dtc2(ctx:commands.context.Context):
    Components.loaders.print_progress_bar(0, 100, 'Dream Test', 'Starting...')
    
    # Send a placeholder message
    await ctx.send(f"Generating image... this might take a moment!", ephemeral=True)

    seed = Components.engine.NewRandomSeed()
    level = 0

    GENERATION_NAME, png_buffer = Components.grove.FromSeed(
        Gf=GROVEFLOORS,
        level=level,
        seed=seed,
        saved_maps=saved_maps,
        saved_colors=saved_colors,
        saved_glyphs=saved_glyphs
    )
    Components.loaders.print_progress_bar(98, 100, GENERATION_NAME, str(len(png_buffer.getvalue())))

    with png_buffer as buffer:
        buffer.seek(0)
        discord_buffer = discord.File(fp=buffer, filename=GENERATION_NAME+'.png')

    embed = def_reply_embed.copy()
    embed.title = GENERATION_NAME
    # add a field to the embed
    embed.add_field(name="❔", value=f"`{level}|{seed}`", inline=True)

    # Edit the placeholder message to include the image
    await ctx.send(embed=embed, file=discord_buffer, ephemeral=True)

    Components.loaders.print_progress_bar(100, 100, GENERATION_NAME, 'Sent to Discord')

client.run(TOKEN)