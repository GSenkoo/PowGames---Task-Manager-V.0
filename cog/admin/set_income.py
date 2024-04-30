import discord
import function.data as data_manager
from discord.ext import commands

class set_income_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description = "Définir l'investissement pour les revenus chaque mois.")
    @discord.guild_only()
    async def set_income(self, ctx, quantitée : discord.Option(discord.SlashCommandOptionType.integer)): # type: ignore
        if ctx.author.id not in data_manager.get_data("config", "admins"):
            await ctx.respond("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral = True)
            return
        
        if not 0 <= quantitée <= 1000000000000:
            await ctx.respond("Le montant d'investissement mensuel sur les revenus doit être entre 0 (inclu) et 1 trilliards (inclu).")
            return
        
        data_manager.set_data("db", "current_income", quantitée)

        await ctx.respond(f"L'investissement total sur les revenus est désormais de **{quantitée}** robux")


def setup(bot):
    bot.add_cog(set_income_Command(bot))