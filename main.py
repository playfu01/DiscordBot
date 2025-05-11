import discord
from dotenv import load_dotenv
import os
from discord.ext import commands
from discord import app_commands
import asyncio


load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

intents = discord.Intents.default()
intents.message_content = True  # Required to read message content
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
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
        self.executed = False # check so it doesnt run twice

    @discord.ui.button(label="KICKEN", style=discord.ButtonStyle.green)
    async def kick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in self.voted:
             self.yes_votes += 1
             self.voted.append(interaction.user.id)
             await interaction.response.send_message("✅ Deine Stimme wurde für das Kicken gezählt!", ephemeral=True)
        else:
            await interaction.response.send_message("Du hast schon gevoted!", ephemeral=True)

       
    
    @discord.ui.button(label="NICHT KICKEN", style=discord.ButtonStyle.red)
    async def dont_kick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in self.voted:
             self.no_votes += 1
             self.voted.append(interaction.user.id)
             await interaction.response.send_message("❌ Deine Stimme wurde für gegen das Kicken gezählt!", ephemeral=True)
        else:
            await interaction.response.send_message("Du hast schon gevoted!", ephemeral=True)
        
        


    # update den timer jede sekunde und zählt die stimmen und zeig alles an
    async def update_timer(self):
        while self.timer > 0 and not self.executed:
            await asyncio.sleep(1)
            self.timer -= 1
            try:
                await self.message.edit(
                    content=f"🗳️ Votekick gegen {self.target_user.mention}! Zeit: {self.timer}s verbleibend. Stimme jetzt ab:\n\n✅ {self.yes_votes} Stimmen\n❌ {self.no_votes} Stimmen",
                    view=self)
            except discord.NotFound:
                break

        await self.on_timeout()
    


    async def on_timeout(self):
        if self.executed:  # wenn schon einmal ausgeführt nicht noch einmal
            return
        self.executed = True
        # Wenn die zeit abgeluafen ist, wertet der bot aus
        result = f"🗳️ Abstimmung beendet: ✅ {self.yes_votes} | ❌ {self.no_votes}\n"
        # hier werden die votes gezählt
        if self.yes_votes > self.no_votes:
            if self.target_user.voice is not None: # schaut ob der user überhaupt in einem voicechannel ist
                try:
                    result += f"🚨 Mehrheit will {self.target_user.mention} kicken!"
                    await self.target_user.move_to(None) # wird verscuht in aus dem voichannel zu kicken
                except discord.Forbidden:
                    result += f"❌ Konnte {self.target_user.mention} nicht aus dem Voicechannel entfernen (fehlende Rechte)." # passiert falls der bot keine rechte hat fürs kicken
            else:
                result += f"ℹ️ {self.target_user.mention} ist nicht in einem Voicechannel" # wenn er in keine voicechannel ist
        else:
            result += f" {self.target_user.mention} darf bleiben." # die vote waren dafür, dass er im Voicechannel bleiben darf

        for item in self.children:
            item.disabled = True # buttons deaktivieren

        # Nachricht aktualisieren
        await self.message.edit(content=result, view=self)

    async def start_timer(self, message):
        self.message = message
        #starte den Timer prozess in einer seperaten task
        asyncio.create_task(self.update_timer())

    
@tree.command(name="votekick", description="Starte eine Abstimmung um jemanden zu kicken.")
@app_commands.describe(user="Wähle den User, den du kicken willst")
async def votekick(interaction: discord.Interaction, user: discord.Member):

    og_turtle = interaction.guild.get_role(895597801289961522)
    crazy_turtle = interaction.guild.get_role(1361142495580524584)
    member = interaction.guild.get_member(interaction.user.id)
    if og_turtle not in member.roles and crazy_turtle not in member.roles: 
        await interaction.response.send_message("Du darfst diesen befehl nicht benutzen", ephemeral=True)
        return

    view = VoteKickView(target_user=user, guild=interaction.guild)
    await interaction.response.send_message(
        f"🗳️ Votekick gestartet gegen {user.mention} ! Stimme jetzt ab:",
        view=view
    )

    # Speichere Nachricht für spätere Bearbeitung
    view.message = await interaction.original_response()

    # Speichern und Timer starten
    await view.start_timer(view.message)
# endregion votekick



    






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
    
    # man kann hier einfach trigger wörter mit antworten hinzufügen
    responses = {
        "turtlebot": "bottastisch!",
        "samil": "boosted"  

    }

    content = message.content.lower()
    for trigger, response in responses.items():
        if trigger in content:
            await message.channel.send(response)
            break # damit ur eine antwort pro nachricht 

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

