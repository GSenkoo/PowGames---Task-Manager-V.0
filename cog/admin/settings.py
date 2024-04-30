import discord
import function.data as data_manager
from discord.ext import commands

class settings_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description = "Voir les paramètres définis actuellement")
    @discord.guild_only()
    async def settings(self, ctx):
        if not ctx.author.id in data_manager.get_data("config", "admins"):
            await ctx.respond("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral = True)
            return

        tasks = data_manager.get_data("db", "tasks")
        users = data_manager.get_data("db", "users_profil")
        try:
            confirm_channel = await ctx.guild.fetch_channel(data_manager.get_data("db", "tasks_confirm_channel"))
        except:
            confirm_channel = None

        try:
            logs_channel = await ctx.guild.fetch_channel(data_manager.get_data("db", "tasks_logs_channel"))
        except:
            logs_channel = None

        project_income = data_manager.get_data("db", "current_income")

        await ctx.respond(
            embed = discord.Embed(
                title = "Paramètres",
                description =
                f"> Nombre de tâches disponibles : **{len(tasks)}**\n" +
                f"> Nombre d'utilsateur enregistré : **{len(users)}**\n" +
                f"> Salon de confirmation : " + (f"<#{confirm_channel.id}>" if confirm_channel else "*Aucun salon définis*") + "\n" +
                f"> Salon de logs : " + (f"<#{logs_channel.id}>" if logs_channel else "*Aucun salon définis*") + "\n" +
                f"> Investissement mensuel dans le projet : **{project_income} robux**",
                color = 0xFFFFFF
            )
        )


def setup(bot):
    bot.add_cog(settings_Command(bot))