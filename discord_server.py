import discord
from discord import app_commands
from discord.ext import commands
import os
import tempfile
import to_terminal

# Load available glyphtables and colors
saved_colors = to_terminal.SavedColors().maps
saved_glyphs = to_terminal.SavedGlyphs().maps

glyphtable_options = list(saved_glyphs.keys())
color_options = list(saved_colors.keys())

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

class AddressView(discord.ui.View):
    def __init__(self, ctx, params):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.params = params
        self.glyphtable = None
        self.color = None
        self.done = False
        self.add_item(discord.ui.Select(
            placeholder="Select glyphtable",
            options=[discord.SelectOption(label=k) for k in glyphtable_options],
            custom_id="glyphtable_select"
        ))
        self.add_item(discord.ui.Select(
            placeholder="Select color",
            options=[discord.SelectOption(label=k) for k in color_options],
            custom_id="color_select"
        ))
    async def interaction_check(self, interaction):
        return interaction.user == self.ctx.author
    async def on_select_option(self, interaction):
        if interaction.data['custom_id'] == "glyphtable_select":
            self.glyphtable = interaction.data['values'][0]
        elif interaction.data['custom_id'] == "color_select":
            self.color = interaction.data['values'][0]
        if self.glyphtable and self.color:
            self.done = True
            await interaction.response.defer()
            await self.ctx.send(f"Generating image with glyphtable: {self.glyphtable}, color: {self.color} ...")
            # Generate PNG
            out_path = to_terminal.generate_glyph_png(
                glyphtable=self.glyphtable,
                cmap=self.color,
                seed=self.params.get('seed'),
                rows=self.params.get('rows', 3),
                cols=self.params.get('cols', 8),
                uuid=self.params.get('uuid'),
                shorten_uuid=self.params.get('shorten_uuid'),
                fsize=self.params.get('fsize'),
                glyph_values=self.params.get('glyph_values'),
                color_values=self.params.get('color_values'),
                out_path=None
            )
            await self.ctx.send(file=discord.File(out_path, filename="glyph.png"))
            os.remove(out_path)

@bot.tree.command(name="address", description="Generate a glyph PNG with full control over parameters.")
@app_commands.describe(
    glyphtable="Glyphtable to use",
    cmap="Colormap to use",
    seed="Seed for randomness",
    rows="Number of rows",
    cols="Number of columns",
    uuid="UUID to use",
    shorten_uuid="Shorten UUID length",
    fsize="Font size",
    glyph_values="Base16 string for glyphs",
    color_values="Base16 string for colors"
)
async def address(
    interaction: discord.Interaction,
    glyphtable: str = None,
    cmap: str = None,
    seed: int = None,
    rows: int = 3,
    cols: int = 8,
    uuid: str = None,
    shorten_uuid: int = None,
    fsize: int = None,
    glyph_values: str = None,
    color_values: str = None
):
    params = {
        'seed': seed,
        'rows': rows,
        'cols': cols,
        'uuid': uuid,
        'shorten_uuid': shorten_uuid,
        'fsize': fsize,
        'glyph_values': glyph_values,
        'color_values': color_values
    }
    # Show dropdowns for glyphtable and color
    view = AddressView(interaction, params)
    await interaction.response.send_message("Select glyphtable and color:", view=view)

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if not TOKEN:
        print("Please set DISCORD_BOT_TOKEN environment variable.")
    else:
        bot.run(TOKEN)
