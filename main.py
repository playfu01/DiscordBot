import discord
from dotenv import load_dotenv
import os
from discord.ext import commands
from discord import app_commands


load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # Required to read message content
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

class VoteKickView(discord.ui.View):
    def __init__(self, target_user: discord.User):
        super().__init__(timeout=60)
        self.target_user = target_user
        self.yes_votes = 0
        self.no_votes = 0

    @discord.ui.button(label="✅ KICKEN", style=discord.ButtonStyle.danger)
    async def kick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.yes_votes += 1
        await interaction.response.send_message("✅ Stimme für KICKEN wurde gezählt!", ephemeral=True)
    
    @discord.ui.button(label="❌ NICHT KICKEN", style=discord.ButtonStyle.success)
    async def dont_kick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.no_votes += 1
        await interaction.response.send_message("❌ Stimme für NICHT KICKEN wurde gezählt!", ephemeral=True)




@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.name}!")

@bot.command()
async def ping(ctx):
    await ctx.send("pong!")

@bot.command()
async def dm(ctx, *, msg):
    try:
        await ctx.author.send(f"du hast gesagt {msg}")
    except discord.Forbidden:
        await ctx.send("konnte keine dm senden")

@bot.command()
async def antworten(ctx):
  
    await ctx.reply("das ist eine antwort")



@bot.event
async def on_message(message):

    # das der bot sich nicht selber antwortet
    if message.author == bot.user:
        return
    # wenn man hallo antwortet er
    if message.content.lower() == "hallo":
        await message.channel.send(f"hallo wie gehts {message.author.name}")
    # wenn in der nachricht wie gehts dir ist antwortet er
    elif "wie geht dir" in message.content.lower():
        await message.channel.send("bottastisch")

        #wichtig das die andere commands noch funktionieren
    await bot.process_commands(message)

# Slash command /hallo
@tree.command(name="hallo", description="sag hallo zurück!")
async def hallo(interaction: discord.Interaction):
    await interaction.response.send_message(f"hallo {interaction.user.name}")


@tree.command(name="votekick", description="votekicke eine person")
@app_commands.describe(user="Wähle den User, den du kicken willst")
async def votekick(interaction: discord.Interaction, user: discord.User):
    await interaction.response.send_message(f"Du hast für einen Kick von {user.mention} abgestimmt!")

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Bot is ready. Logged in as {bot.user}.")







        

bot.run(DISCORD_TOKEN)

