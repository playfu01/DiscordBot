import random
import discord
from dotenv import load_dotenv
import os
from discord.ext import commands
from discord import Button, app_commands
import asyncio
import requests


load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not DISCORD_TOKEN or not WEATHER_API_KEY:
    raise ValueError("Missing required environment variables")

intents = discord.Intents.default()
intents.message_content = True  # Required to read message content
intents.members = True

bot = commands.Bot(command_prefix="!",help_command=None, intents=intents)
tree = bot.tree
timer = 30

# region votekick
class VoteKickView(discord.ui.View):
    def __init__(self, target_user: discord.Member, guild: discord.Guild):
        super().__init__(timeout=timer)
        self.target_user = target_user
        self.guild = guild
        self.yes_votes = 0
        self.no_votes = 0
        self.message = None
        self.timer = timer 
        self.voted = []
        self.executed = False # check so it doesn't run twice
    @discord.ui.button(label="KICKEN", style=discord.ButtonStyle.green)
    async def kick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in self.voted:
             self.yes_votes += 1
             self.voted.append(interaction.user.id)
             await interaction.response.send_message("✅ Your vote to kick has been counted!", ephemeral=True, delete_after= 30)
        else:
            await interaction.response.send_message("You have already voted!", ephemeral=True, delete_after= 30)

    @discord.ui.button(label="NICHT KICKEN", style=discord.ButtonStyle.red)
    async def dont_kick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in self.voted:
             self.no_votes += 1
             self.voted.append(interaction.user.id)
             await interaction.response.send_message("❌ Your vote against kicking has been counted!", ephemeral=True, delete_after= 30)
        else:
            await interaction.response.send_message("You have already voted!", ephemeral=True, delete_after= 30)

    # update the timer every second and count the votes and display everything
    async def update_timer(self):
        if self.message is not None:
            while self.timer > 0 and not self.executed:
                await asyncio.sleep(1)
                self.timer -= 1
                try:
                    await self.message.edit(
                        content=f"🗳️ Votekick against {self.target_user.mention}! Time: {self.timer}s remaining. Vote now:\n\n✅ {self.yes_votes} votes\n❌ {self.no_votes} votes",
                        view=self)
                except discord.NotFound:
                    break
        else:
            print("no message")

        await self.on_timeout()

    async def on_timeout(self):
        if self.executed:  # if already executed don't run again
            return
        self.executed = True
        # When time is up, the bot evaluates
        result = f"🗳️ Voting ended: ✅ {self.yes_votes} | ❌ {self.no_votes}\n"
        # here the votes are counted
        if self.yes_votes > self.no_votes:
            if self.target_user.voice is not None: # checks if the user is in a voice channel at all
                try:
                    result += f"🚨 Majority wants to kick {self.target_user.mention}!"
                    await self.target_user.move_to(None) # attempts to kick from voice channel
                except discord.Forbidden:
                    result += f"❌ Could not remove {self.target_user.mention} from voice channel (missing permissions)." # happens if bot lacks kick permissions
            else:
                result += f"ℹ️ {self.target_user.mention} is not in a voice channel" # if not in any voice channel
        else:
            result += f" {self.target_user.mention} may stay." # votes were in favor of staying in voice channel

        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True # disable buttons

        # Update message
        if self.message is not None:
            await self.message.edit(content=result, view=self)
        else:
            print("message is none")

    async def start_timer(self, message):
        self.message = message
        # start timer process in a separate task
        asyncio.create_task(self.update_timer())

@tree.command(name="votekick", description="Start a vote to kick someone.")
@app_commands.describe(user="Select the user you want to kick")
async def votekick(interaction: discord.Interaction, user: discord.Member):
    view = VoteKickView(target_user=user, guild=interaction.guild) # type: ignore
    # Ensure command is used in a guild
    if interaction.guild is None:
        await interaction.response.send_message(
            "❌ This command can only be used in a server!",
            ephemeral=True
        )
        return
    
    await interaction.response.send_message(
        f"🗳️ Votekick started against {user.mention}! Vote now:",
        view=view
    )

    # Save message for later editing
    view.message = await interaction.original_response()

    # Save and start timer
    await view.start_timer(view.message)
# endregion votekick

# region weather
@tree.command(name="wetter", description="show current weather for a location")
@app_commands.describe(ort="Enter the location")
async def wetter(interaction: discord.Interaction, ort: str):
    await interaction.response.defer() # for the api call in case it takes long

    url = f"http://api.openweathermap.org/data/2.5/weather?q={ort}&appid={WEATHER_API_KEY}&units=metric&lang=de"
    response = requests.get(url)

    if response.status_code != 200:
        await interaction.followup.send("❌ Location not found or API error", ephemeral=True)
        return
    data = response.json()
    stadt = data["name"]
    temp = data["main"]["temp"]
    wetter = data["weather"][0]["description"].capitalize()
    wind = data["wind"]["speed"]

    antwort = (
        f"📍 **{stadt}**\n"
        f"🌡️ Temperature: {temp}°C\n"
        f"🌥️ Weather: {wetter}\n"
        f"💨 Wind: {wind} m/s"
    )

    await interaction.followup.send(antwort)
# endregion

# region report
@tree.command(name="report", description="report a person")
@app_commands.describe(grund="Why do you want to report this person")
async def report(interaction: discord.Interaction, grund: str):
        responses = [
            f"mimimi {grund} mimimi ",
            "don't be a pussy",
            "ohhh nooooo!"
        ]

        try:
            await interaction.user.send(random.choice(responses))
            await interaction.response.send_message("Your report has been processed",ephemeral=True, delete_after= 30)
        except discord.Forbidden:
            await interaction.response.send_message("I can't send you a DM", ephemeral=True, delete_after= 30)
#endregion    




@tree.command(name="help", description="list all the commands")
async def help(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    slash_commands = tree.get_commands()

    help_text =  "**📖 Verfügbare Slash-Befehle:**\n\n"
    
    for cmd in slash_commands:
        if isinstance(cmd, app_commands.Command):
            name = f"/{cmd.name}"
            description = cmd.description or "Keine Beschreibung vorhanden"
            help_text += f"**{name}** – {description}\n"

    prefix_help_text = "\n**⌨️ Verfügbare Prefix-Befehle:**\n\n"

    for cmd in bot.commands:
        if not cmd.hidden:
            name = f"!{cmd.name}"
            desc = cmd.description or "Keine Beschreibung vorhanden"
            prefix_help_text += f"**{name}** – {desc}\n" 

    await interaction.followup.send(help_text + prefix_help_text, ephemeral=True)



# Slash command /hallo
@tree.command(name="hallo", description="say hello back!")
async def hallo(interaction: discord.Interaction):
    await interaction.response.send_message(f"hello {interaction.user.name}")

@bot.command(description="sagt hallo")
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.name}!")

@bot.command(description="pong!")
async def ping(ctx):
    await ctx.send("pong!")

@bot.command(description="schreibt dir eine dm mit deiner Nachricht")
async def dm(ctx, *, msg):
    try:
        await ctx.author.send(f"you said {msg}")
    except discord.Forbidden:
        await ctx.send("could not send DM")

@bot.command(description="antwortet dir")
async def antworten(ctx):
    await ctx.reply("this is a reply")

@bot.event
async def on_message(message):
    # prevent bot from responding to itself
    if message.author == bot.user:
        return
    
    # you can simply add trigger words with responses here
    responses = {
        "turtlebot": "bottastic!",
        "samil": "boosted"  
    }

    content = message.content.lower()
    for trigger, response in responses.items():
        if trigger in content:
            await message.channel.send(response)
            break # so only one response per message

    # important so other commands still work
    await bot.process_commands(message)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Bot is ready. Logged in as {bot.user}.")

bot.run(DISCORD_TOKEN)