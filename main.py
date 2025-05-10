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
    def __init__(self, target_user: discord.Member, guild: discord.Guild):
        super().__init__(timeout=60)
        self.target_user = target_user
        self.guild = guild
        self.yes_votes = 0
        self.no_votes = 0
        self.message = None

    @discord.ui.button(label="✅ KICKEN", style=discord.ButtonStyle.danger)
    async def kick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.yes_votes += 1
        await interaction.response.send_message("✅ Stimme fürs KICKEN wurde gezählt!", ephemeral=True)
    
    @discord.ui.button(label="❌ NICHT KICKEN", style=discord.ButtonStyle.success)
    async def dont_kick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.no_votes += 1
        await interaction.response.send_message("❌ Stimme fürs NICHT KICKEN wurde gezählt!", ephemeral=True)

    async def on_timeout(self):
        # Wenn die zeit abgeluafen ist, wertet der bot aus
        result = f"🗳️ Abstimmung beendet: ✅ {self.yes_votes} | ❌ {self.no_votes}\n"
        # hier werden die votes gezählt
        if self.yes_votes > self.no_votes:
            if self.target_user.voice is not None: # schaut ob der user überhaupt in einem voicechannel ist
                try:
                    await self.target_user.move_to(None) # wird verscuht in aus dem voichannel zu kicken
                    result += f"🚨 Mehrheit will {self.target_user.mention} kicken!"
                except discord.Forbidden:
                    result += f"❌ Konnte {self.target_user.mention} nicht aus dem Voicechannel entfernen (fehlende Rechte)." # passiert falls der bot keine rechte hat fürs kicken
            else:
                result += f"ℹ️ {self.target_user.mention} ist nicht in einem Voicechannel" # wenn er in keine voicechannel ist
        else:
            result += f" {self.target_user.mention} darf bleiben." # die vote waren dafür, dass er im Voicechannel bleiben darf

        for item in self.children:
            item.disabled = True # buttons deaktivieren

        # Nachricht aktualiesieren
        await self.message.edit(content=result, view=self)
    
@tree.command(name="gutentag", description="Starte eine Abstimmung um jemanden zu kicken.")
@app_commands.describe(user="Wähle den User, den du kicken willst")
async def votekick(interaction: discord.Interaction, user: discord.Member):
    view = VoteKickView(target_user=user, guild=interaction.guild)
    msg = await interaction.response.send_message(
        f"🗳️ Votekick gestartet gegen {user.mention}! Stimme jetzt ab:",
        view=view
    )

    # Speichere Nachricht fpüür spätere Bearbeitung
    view.message = await interaction.original_response()

    






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

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Bot is ready. Logged in as {bot.user}.")







        

bot.run(DISCORD_TOKEN)

