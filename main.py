import discord
from dotenv import load_dotenv
import os
from discord.ext import commands
from discord import app_commands


load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # Required to read message content

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Bot is ready. Logged in as {bot.user}.")

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.name}!")

@bot.command()
async def ping(ctx):
    await ctx.send("pong!")

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




        

bot.run(DISCORD_TOKEN)

