##########IMPORTS##########

import discord
from discord.ext import commands
from discord import Interaction
from no1jj import *

##########CONFIG##########

config = helper.LoadConfig()
botToken = config.get("BotToken")
botActivity = config.get("BotActivity")
userID = config.get("UserID")

##########BOT##########

class Bot(commands.AutoShardedBot):
    async def on_ready(self):
        await self.wait_until_ready()
        await self.tree.sync()
        activity = discord.Game(name=botActivity)
        await self.change_presence(activity=activity)
        botID = self.user.id
        botInvitationLink = f"https://discord.com/oauth2/authorize?client_id={botID}&permissions=8&integration_type=0&scope=bot"
        print(f"Bot Invitation Link: {botInvitationLink}")

intents = discord.Intents.all()
no1jj = Bot(intents=intents, command_prefix="J!", help_command=None)

##########COMMANDS##########

@no1jj.tree.command(name="start", description="Start.")
async def Start(interaction: Interaction):
    if not helper.IsUserInAdmin(userid=str(interaction.user.id)):
        embed = discord.Embed(
            description="You cannot use this command.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return  
    
    guild = interaction.client.guilds
    view = discordUI.SelectGuildView(guild)
    
    await interaction.response.send_message(view=view)

##########RUN##########

no1jj.run(botToken)

# Made by no.1_jj
# v1.0.2