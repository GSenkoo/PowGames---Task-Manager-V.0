import discord
import function.data as data_manager
from discord.ext import commands


class user_unregister_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.slash_command(description = "Retirer l'enregistrement d'un utilisteur")
    @discord.guild_only()
    async def user_unregister(self,
        ctx,
        utilisateur : discord.Option(discord.SlashCommandOptionType.user) # type: ignore                       
    ):
        if ctx.author.id not in data_manager.get_data("config", "admins"):
            await ctx.respond("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral = True)
            return
        
        users_profil = data_manager.get_data("db", "users_profil")
        registered = False

        for user_id in users_profil.keys():
            if user_id == str(utilisateur.id):
                registered = True
                break
        
        if not registered:
            await ctx.respond(f"<@{utilisateur.id}> n'est pas enregistré.", ephemeral = True)
            return
        
        del users_profil[str(utilisateur.id)]
        data_manager.set_data("db", "users_profil", users_profil)

        await ctx.respond(f"<@{utilisateur.id}> a correctement été retiré des enregistrements.")

        try:
            logs_channel = await ctx.guild.fetch_channel(logs_channel)
            await logs_channel.send(embed = discord.Embed(description = f"<@{ctx.author.id}> vient de retirer <@{utilisateur.id}> des enregistrements.", color = 0xFFFFFF))
        except:
            pass

def setup(bot):
    bot.add_cog(user_unregister_Command(bot))