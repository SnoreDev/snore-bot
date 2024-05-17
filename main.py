import os
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import datetime

load_dotenv()

TOKEN = os.getenv('TOKEN')

if TOKEN is None:
    raise ValueError("No DISCORD_TOKEN found in environment variable.")

PREFIX = "$"
client = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())

WELCOME_CHANNEL_NAME = 'welcome'

@client.event
async def on_ready():
    print(f"Logged in as {client.user.name} ({client.user.id})")
    update_status.start()

@tasks.loop(seconds=50)
async def update_status():
    guild_count = len(client.guilds)
    activity = discord.Activity(type=discord.ActivityType.watching, name=f"{guild_count} guilds 👀")
    await client.change_presence(activity=activity)

@update_status.before_loop
async def before_update_status():
    await client.wait_until_ready()

async def get_or_create_welcome_channel(guild):
    # Check if the welcome channel exists
    for channel in guild.text_channels:
        if channel.name == WELCOME_CHANNEL_NAME:
            return channel

    # Create the welcome channel if it doesn't exist
    return await guild.create_text_channel(WELCOME_CHANNEL_NAME)

@client.event
async def on_member_join(member):
    channel = await get_or_create_welcome_channel(member.guild)
    
    embed = discord.Embed(
        title=f"Welcome! {member.name} 👋",
        description=f"You've joined `{member.guild.name}`",
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now()
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

    await channel.send(embed=embed)

@client.event
async def on_member_remove(member):
    channel = await get_or_create_welcome_channel(member.guild)
    
    embed = discord.Embed(
        title="Goodbye! 😢",
        description=f"{member.mention} has left `{member.guild.name}`",
        color=discord.Color.red(),
        timestamp=datetime.datetime.now()
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

    await channel.send(embed=embed)

client.run(TOKEN)
