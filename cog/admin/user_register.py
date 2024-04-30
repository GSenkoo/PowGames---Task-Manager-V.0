import discord
import function.data as data_manager
from discord.ext import commands

class user_register_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description = "Enregistrer un utilisateur")
    @discord.guild_only()
    async def user_register(self, 
        ctx,
        utilisateur : discord.Option(discord.SlashCommandOptionType.user) # type: ignore
    ):
        if ctx.author.id not in data_manager.get_data("config", "admins"):
            await ctx.respond("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral = True)
            return
        
        users_profil = data_manager.get_data("db", "users_profil")

        for user_id in users_profil.keys():
            if user_id == str(utilisateur.id):
                await ctx.respond(f"<@{utilisateur.id}> est déjà enregistré.")
                return
        
        user_data = {
            "current_tasks": [],
            "current_points": 0,
            "current_roles": [],
            "max_tasks": 1
        }

        users_profil[str(utilisateur.id)] = user_data
        data_manager.set_data("db", "users_profil", users_profil)

        await ctx.respond(f"<@{utilisateur.id}> a été enregistré avec succès, pour gérer cet utilisateur, utilisez `/user_manage <utilisateur>`.")

        try:
            logs_channel = await ctx.guild.fetch_channel(logs_channel)
            await logs_channel.send(embed = discord.Embed(description = f"<@{ctx.author.id}> vient d'enregister <@{utilisateur.id}>.", color = 0xFFFFFF))
        except:
            pass

def setup(bot):
    bot.add_cog(user_register_Command(bot))