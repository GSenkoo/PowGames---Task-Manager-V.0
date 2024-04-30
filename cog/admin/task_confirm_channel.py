import discord
import function.data as data_manager
from discord.ext import commands

class task_confirm_channel_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description = "Définir le salon de confirmation des tâches.")
    @discord.guild_only()
    async def task_confirm_channel(self,
        ctx,
        salon : discord.Option(discord.SlashCommandOptionType.channel) # type: ignore
    ):
        if ctx.author.id not in data_manager.get_data("config", "admins"):
            await ctx.respond("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral = True)
            return

        current_channel = data_manager.get_data("db", "tasks_confirm_channel")
        
        if salon.id == current_channel:
            await ctx.respond(f"Le salon <#{salon.id}> est déjà le salon de confirmation des tâches.")
            return
        
        data_manager.set_data("db", "tasks_confirm_channel", salon.id)

        await ctx.respond(f"Le salon <#{salon.id}> est désormais le salon de confirmation des tâches.")

        try:
            logs_channel = await ctx.guild.fetch_channel(logs_channel)
            await logs_channel.send(embed = discord.Embed(description = f"<@{ctx.author.id}> vient de définir un nouveau salon de confirmation des tâches : {salon.id}.", color = 0xFFFFFF))
        except:
            pass


def setup(bot):
    bot.add_cog(task_confirm_channel_Command(bot))