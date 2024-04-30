import discord
import function.data as data_manager
from discord.ext import commands


class leaderboard_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description = "Voir le classement des utilisateurs dans le projet.")
    @discord.guild_only()
    async def leaderboard(self, ctx):
        users_profil = data_manager.get_data("db", "users_profil")
        project_income = data_manager.get_data("db", "current_income")
        all_points = sum([user_data['current_points'] for user_id, user_data in users_profil.items()])
        
        sorted_users_profil = sorted(users_profil.items(), key = lambda x: x[1]["current_points"], reverse = True)

        txt = None
        if len(sorted_users_profil) > 20:
            sorted_users_profil = sorted_users_profil[:20]
            txt = f"\n(et {len(sorted_users_profil) - 20} autres)"

        leaderboard = []
        n = 0
        for user_id, user_data in sorted_users_profil:
            n += 1
            leaderboard.append(
                f"{n}. <@{user_id}> - **{user_data['current_points']}** points ({round(user_data['current_points'] / all_points * 100, 1)}% / {round(user_data['current_points'] / all_points * project_income, 1)} robux brut)"
            )
        
        await ctx.respond(
            embed = discord.Embed(
                title = "Leaderboard",
                color = 0xFFFFFF,
                description = ("\n".join(leaderboard) if len(leaderboard) else "*Aucun utilisateur enregistré.*") + (txt if txt else "")
                + "\n\n*Pour monter dans le classement, vous pouvez faire des tâches que vous pouvez voir et choisir via la commande `/tasks`.*"
                + "\n*Plus vous faites des tâches, plus vous gagnez de points, donc plus vous gagner des robux.*"
            )
        )


def setup(bot):
    bot.add_cog(leaderboard_Command(bot))