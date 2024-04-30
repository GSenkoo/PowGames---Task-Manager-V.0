import discord
import function.data as data_manager
from discord.ext import commands


class set_status_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description = "Définir le texte du statut du bot.")
    @discord.guild_only()
    async def set_status(self, ctx, statut : str):
        if not ctx.author.id in data_manager.get_data("config", "admins"):
            await ctx.respond("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral = True)
            return
        
        if not 0 < len(statut) < 26:
            await ctx.respond("Le statut doit être entre 1 (inclu) et 25 (inclu) caractères.", ephemeral = True)
            return
        
        data_manager.set_data("db", "bot_status", statut)
        await ctx.respond(f"Le statut du bot a bien été définis à **{statut}**.")
    
def setup(bot):
    bot.add_cog(set_status_Command(bot))