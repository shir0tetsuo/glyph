import discord
from discord.ext import commands
from discord import app_commands
import json
import sys
import os
from datetime import datetime

import Components
import Components.loaders
import Components.generators

__version__ = 'v1.0.0'

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
    },
    "fields": [
        {
            "name": "",
            "value": ""
        },
        {
            "name": "",
            "value": ""
        }
    ]
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

client.run(TOKEN)