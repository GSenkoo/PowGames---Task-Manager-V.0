import discord
import function.data as data_manager
from discord.ext import commands

role_id_to_name = {
    "scripter": "Scripter",
    "modeler": "Modélisateur",
    "animator": "Animateur",
    "builder": "Builder",
    "vfx": "VFX Maker",
    "sfx": "SFX Maker",
    "graphic_designer": "Graphiste",
    "discord_staff": "Staff Discord",
    "others": "Autres rôles"
}

class profil_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description = "Voir le profil d'un utilisteur dans le projet")
    @discord.guild_only()
    async def profil(self, ctx, utilisateur : discord.Option(discord.SlashCommandOptionType.user) = None): # type: ignore
        users_profil = data_manager.get_data("db", "users_profil")
        if not utilisateur:
            utilisateur = ctx.author

        all_points = 0
        registered = False
        for user_id, user_d in users_profil.items():
            all_points += user_d["current_points"]
            if user_id == str(utilisateur.id):
                registered = True

        if not registered:
            await ctx.respond(f"<@{utilisateur.id}> n'est pas enregistré.")
            return
        
        class ProfileSelect(discord.ui.View):
            @discord.ui.select(
                placeholder = "Choisir une page",
                options = [
                    discord.SelectOption(
                        label = "Informations principaux",
                        emoji = "ℹ️",
                        value = "principal_values"
                    ),
                    discord.SelectOption(
                        label = "Tâches",
                        emoji = "📜",
                        value = "tasks"
                    ),
                    discord.SelectOption(
                        label = "Rôles",
                        emoji = "🎓",
                        value = "roles"
                    ),
                    discord.SelectOption(
                        label = "Revenus",
                        emoji = "💶",
                        value = "income"
                    )
                ]
            )
            async def select_callback(self, select, interaction):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral = True)
                    return
                
                users_data = data_manager.get_data("db", "users_profil")
                user_data = users_data[str(utilisateur.id)]
                
                if not user_data:
                    await interaction.response.send_message(f"<@{utilisateur.id}> n'est plus enregistré.", ephemeral = True)
                    return

                all_points = 0
                for user_id, user_d in users_data.items():
                    all_points += user_d["current_points"]
    

                if select.values[0] == "principal_values":
                    embed = discord.Embed(
                        author = discord.EmbedAuthor(
                            name = utilisateur.display_name,
                            icon_url = utilisateur.avatar.url
                        ),
                        title = "Informations principaux",
                        color = 0xFFFFFF
                    ).add_field(
                        name = "Nombre de tâches",
                        value = str(len(user_data['current_tasks']))
                    ).add_field(
                        name = "Nombre de rôles",
                        value = str(len(user_data['current_roles']))
                    ).add_field(
                        name = "Nombre de points",
                        value = str(user_data['current_points'])
                    )

                elif select.values[0] == "tasks":
                    embed = discord.Embed(
                        author = discord.EmbedAuthor(
                            name = utilisateur.display_name,
                            icon_url = utilisateur.avatar.url
                        ),
                        title = "Tâches",
                        description = ("- " + "\n- ".join(user_data['current_tasks'])) if len(user_data['current_tasks']) else "*Aucune tâches*",
                        color = 0xFFFFFF
                    )
                
                elif select.values[0] == "roles":
                    embed = discord.Embed(
                        author = discord.EmbedAuthor(
                            name = utilisateur.display_name,
                            icon_url = utilisateur.avatar.url
                        ),
                        title = "Rôles",
                        description = ("- " + "\n- ".join([role_id_to_name[role_id] for role_id in user_data['current_roles']])) if len(user_data['current_roles']) else "*Aucun rôles*",
                        color = 0xFFFFFF
                    )
                
                elif select.values[0] == "income":
                    income = user_data['current_points'] / all_points if all_points != 0 else 0
                    project_income = data_manager.get_data("db", "current_income")

                    embed = discord.Embed(
                        author = discord.EmbedAuthor(
                            name = utilisateur.display_name,
                            icon_url = utilisateur.avatar.url
                        ),
                        title = "Revenus",
                        color = 0xFFFFFF
                    ).add_field(
                        name = "Part de travail",
                        value = str(round(income * 100, 1)) + "%"
                    ).add_field(
                        name = "Revenu BRUT estimé",
                        value = str(round(income * project_income, 1)) + " robux"
                    ).add_field(
                        name = "Revenu NET estimé",
                        value = str(round(income * project_income * 0.7, 1)) + " robux"
                    )
                else:
                    return
                
                await interaction.message.edit(embed = embed)
                await interaction.response.defer()
        
        await ctx.respond(
            embed = discord.Embed(
                author = discord.EmbedAuthor(
                    name = utilisateur.display_name,
                    icon_url = utilisateur.avatar.url
                ),
                color = 0xFFFFFF,
                description = "Choisissez une catégorie."
            ),
            view = ProfileSelect(timeout = 600)
        )



def setup(bot):
    bot.add_cog(profil_Command(bot))