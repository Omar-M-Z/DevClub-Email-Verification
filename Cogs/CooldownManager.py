import discord
from discord.ext import commands, tasks
from Cogs.EmailVerification import usersOnCooldown
import datetime

cooldown = datetime.timedelta(hours = 10)

class CooldownManager(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.UpdateCooldowns.start()

    @tasks.loop(minutes = 5)
    async def UpdateCooldowns(self):
        currentTime = datetime.datetime.now()
        for count, i in usersOnCooldown:
            if (currentTime - usersOnCooldown[i]) <= cooldown:
                usersOnCooldown.pop(usersOnCooldown.keys()[count])

    @UpdateCooldowns.before_loop
    async def BeforeUpdateCooldowns(self):
        print("loading...")

def setup(client):
    client.add_cog(CooldownManager(client))