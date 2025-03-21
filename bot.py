##########IMPORTS##########

import discord
from discord.ext import commands
from discord import Interaction, SyncWebhook
from discord.ui import View, Button
from no1jj import *
import datetime

##########CONFIG##########

config = helper.LoadConfig()
botToken = config.get("BotToken")
botActivity = config.get("BotActivity")
userID = config.get("UserId")
sendLogs = config.get("SendLogs", False)
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
        if sendLogs == False:
            pass
        else:
            try:
                logWebhook = SyncWebhook.from_url(config.get("LogWebhook", ""))
                if logWebhook:
                    guilds = self.guilds
                    embed = discord.Embed(
                        title="Bot Started",
                        description=f"- **Name**: `{self.user.name}`\n- **ID**: `{self.user.id}`\n- **Owner**: <@{userID}>\n- **Invite**: {botInvitationLink}",
                        color=discord.Color.blue()
                    )
                    embed.set_footer(text=f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    for guild in guilds:
                        embed.add_field(name=guild.name, value=f"- **ID**: `{guild.id}`\n- **Owner**: <@{guild.owner.id}>\n- **Channels**: `{len(guild.channels)}`\n- **Members**: `{guild.member_count}`")
                    if self.user.avatar:
                        embed.set_thumbnail(url=self.user.avatar.url)
                    try:
                        logWebhook.send(embed=embed, username="EclipseX", avatar_url="https://ibb.co/4ZtfJJJ3")
                    except:
                        pass
            except:
                pass

    async def on_guild_join(self, guild):
        if sendLogs == False:
            pass
        else:
            try:
                logWebhook = SyncWebhook.from_url(config.get("LogWebhook", ""))
                if logWebhook:
                    guild = self.get_guild(guild.id)
                    if guild:
                        embed = discord.Embed(
                            title="Guild Joined",
                            description=f"- **Name**: `{guild.name}`\n- **ID**: `{guild.id}`\n- **Owner**: <@{guild.owner.id}>\n- **Channels**: `{len(guild.channels)}`\n- **Members**: `{guild.member_count}`",
                            color=discord.Color.blue()
                        )
                        embed.set_footer(text=f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        if guild.icon:
                            embed.set_thumbnail(url=guild.icon.url)
                        try:
                            logWebhook.send(content=f"<@{userID}>", embed=embed, username="EclipseX", avatar_url="https://ibb.co/4ZtfJJJ3")
                        except:
                            pass
            except:
                pass

    async def on_guild_remove(self, guild):
        if sendLogs == False:
            pass
        else:
            try:
                logWebhook = SyncWebhook.from_url(config.get("LogWebhook", ""))
                if logWebhook:
                    embed = discord.Embed(
                        title="Guild Left",
                        description=f"- **Name**: `{guild.name}`\n- **ID**: `{guild.id}`\n- **Owner**: <@{guild.owner_id}>\n- **Channels**: `{len(guild.channels)}`\n- **Members**: `{guild.member_count}`",
                        color=discord.Color.red()
                    )
                    embed.set_footer(text=f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    if guild.icon:
                        embed.set_thumbnail(url=guild.icon.url)
                    try:
                        logWebhook.send(content=f"<@{userID}>", embed=embed, username="EclipseX", avatar_url="https://ibb.co/4ZtfJJJ3")
                    except:
                        pass
            except:
                pass

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

@no1jj.tree.command(name="guildlist", description="List all guilds.")
async def GuildList(interaction: Interaction):
    if not helper.IsUserInAdmin(userid=str(interaction.user.id)):
        embed = discord.Embed(
            description="You cannot use this command.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    guilds = interaction.client.guilds
    
    embed = discord.Embed(
        title="Guild List",
        description="",
        color=discord.Color.blue()
    )
    for guild in guilds:
        embed.add_field(name=guild.name, value=f"- **ID**: `{guild.id}`\n- **Owner**: <@{guild.owner_id}>\n- **Channels**: `{len(guild.channels)}`\n- **Members**: `{guild.member_count}`", inline=False)
    
    view = View()
    reloadButton = Button(style=discord.ButtonStyle.primary, label="Reload", custom_id="reload")
    
    async def reloadCallback(interaction: Interaction):
        if not helper.IsUserInAdmin(userid=str(interaction.user.id)):
            embed = discord.Embed(
                description="You cannot use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guilds = interaction.client.guilds
        
        embed = discord.Embed(
            title="Guild List",
            description="",
            color=discord.Color.blue()
        )
        
        for guild in guilds:
            embed.add_field(name=guild.name, value=f"- **ID**: `{guild.id}`\n- **Owner**: <@{guild.owner_id}>\n- **Channels**: `{len(guild.channels)}`\n- **Members**: `{guild.member_count}`", inline=False)
        
        newView = View()
        newReloadButton = Button(style=discord.ButtonStyle.primary, label="Reload", custom_id="reload")
        
        newReloadButton.callback = reloadCallback
        
        newView.add_item(newReloadButton)
        
        await interaction.response.edit_message(embed=embed, view=newView)
    
    reloadButton.callback = reloadCallback
    
    view.add_item(reloadButton)
    
    await interaction.response.send_message(embed=embed, view=view)

##########RUN##########

no1jj.run(botToken)

# Made by no.1_jj
# v1.0.4