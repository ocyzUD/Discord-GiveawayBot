import discord
from discord.ext import commands, tasks
from discord import app_commands
import random
import asyncio
import datetime

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="1", intents=intents)

giveaway_data = {}

def is_eligible_for_giveaway(user, giveaway):
    return user not in giveaway["participants"]

@bot.tree.command(name="start_giveaway", description="start a giveaway!")
async def start_giveaway(interaction: discord.Integration, prize: str, duration: int):
    """starts a giveaway with a prize and duration (in seconds)."""

    embed = discord.Embed(title= "🎉 Giveaway Started!", description=f"Prize: {prize}\nDuration {duration} seconds", color=discord.Color.green())
    giveaway_message = await interaction.channel.send(embed=embed)

    giveaway_data[giveaway_message.id] = {
        "prize": prize,
        "end_time": datetime.datetime.utcnow() + datetime.timedelta(seconds=duration),
        "participants": [],
        "message_id": giveaway_message.id
    }

    await giveaway_message.add_reaction("🎉")

    await asyncio.sleep(duration)

    giveaway = giveaway_data.pop(giveaway_message.id, None)
    if giveaway:
        winner = random.choice(giveaway["participants"]) if giveaway["participants"] else None

        if winner: 
            await interaction.channel.send(f"🎉 Congratulations {winner.mention}! You won the **{giveaway['prize']}**!")
        else:
            await interaction.channel.send("The giveaway ended, but no participants entered!")

        await giveaway_message.delete()

@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.user):

    if user.bot:
        return
    if reaction.emoji == "🎉" and reaction.message.id in giveaway_data:
        giveaway = giveaway_data[reaction.message.id]

        if is_eligible_for_giveaway(user, giveaway):
            giveaway["participants"].append(user)
            await reaction.message.channel.send(f"{user.mention}, you entered the giveaway for **{giveaway['prize']}**!", ephermal=True)
        else:
            await reaction.message.channel.send(f"{user.mention}, you already entered the giveaway for **{giveaway['prize']}**!", ephermal=True)
            
@bot.tree.command(name="giveaway_status", description="Check the status of an ongoing giveaway.")
async def giveaway_status(interaction: discord.Interaction, message_id: int):
    """Check the status of an ongoing giveaway."""
    
    if message_id not in giveaway_data:
        await interaction.response.send_message("No ongoing giveaway with that message ID.", ephemeral=True)
        return
    
    giveaway = giveaway_data[message_id]
    time_left = giveaway["end_time"] - datetime.datetime.utcnow()
    time_left_str = str(time_left).split('.')[0]  

    embed = discord.Embed(title="🎉 Giveaway Status", description=f"Prize: {giveaway['prize']}\nTime Left: {time_left_str}\nParticipants: {len(giveaway['participants'])}", color=discord.Color.blue())
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

    await bot.tree.sync()

bot.run("YOUR_TOKEN_HERE")
