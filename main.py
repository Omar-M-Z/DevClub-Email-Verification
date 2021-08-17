import discord
from discord.ext import commands
import os
from os import listdir

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = "-", intents = intents)

@client.event
async def on_ready():
    print("The bot is ready.")

cogs = ["Verification"]

for i in range(len(cogs)):
    from os.path import realpath, split, join, splitext
    for item in listdir(join(split(realpath(__file__))[0], cogs[i])):
        if item.endswith(".py"):
            client.load_extension(f"{cogs[i]}." + splitext(item)[0])

client.run(os.environ.get("BOT_TOKEN"))