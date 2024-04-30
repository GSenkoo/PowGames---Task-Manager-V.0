import discord
import function.data as data_manager
from discord.ext import commands
from discord.ext.pages import Page, Paginator, PaginatorButton

class CustomPaginator(Paginator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.usercheck:
            if self.user != interaction.user:
                await interaction.response.send_message("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral = True)
                return False
        return True
    

class help_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description = "Obtenir des informations sur les commandes du bot")
    @discord.guild_only()
    async def help(self, ctx):
        pages = [
            Page(
                embeds = [
                    discord.Embed(
                        title = "Commandes public",
                        description = "*Les options `<...>` sont obligatoires et les options `[...]` sont facultatives.*\n\n"
                        + "**`/complete_task`**"
                        + "\nDemander aux administrateurs la complétion d'une tâche.\n\n"
                        
                        + "**`/help`**"
                        + "\nObtenir de l'aide sur les commandes du bot.\n\n"

                        + "**`/leaderboard`**"
                        + "\nVoir le classement par points des utilisateurs enregistrés.\n\n"

                        + "**`/profil [utilisateur]`**"
                        + "\nVoir le profil d'un utilisateur enregistré.\n\n"

                        + "**`/tasks`**"
                        + "\nVoir les tâches disponibles et en choisir.",
                        color = 0xFFFFFF
                    )
                ]
            ),
            Page(
                embeds = [
                    discord.Embed(
                        title = "Commandes réservées aux admins",
                        description = "*Les options `<...>` sont obligatoires et les options `[...]` sont facultatives.*\n\n"
                        + "**`/set_income <quantitée>`**"
                        + "\nDéfinir l'investissement mensuel (en robux) dans le projet.\n\n"

                        + "**`/set_status <statut>`**"
                        + "\nDéfinir le texte affiché dans le statut du bot.\n\n"

                        + "**`/settings`**"
                        + "\nVoir les paramètres principaux définis.\n\n"

                        + "**`/task_confirm_channel <salon>`**"
                        + "\nDéfinir un salon de confirmation des tâches.\n\n"

                        + "**`/task_log_channel <salon>`**"
                        + "\nDéfinir un salon de logs pour les tâches.\n\n"

                        + "**`/task_create`**"
                        + "\nCréer une tâche.\n\n"

                        + "**`/task_delete`**"
                        + "\nSupprimer une tâche.\n\n"

                        + "**`/user_register <utilisateur>`**"
                        + "\nEnregistrer un utilisateur.\n\n"

                        + "**`/user_manage <utilisateur>`**"
                        + "\nGérer un utilisateur.\n\n"

                        + "**`/user_unregister <utilisateur>`**"
                        + "\nRetirer un utilisateur des enregistrements.\n\n",
                        color = 0xFFFFFF
                    )
                ]
            )
        ]

        buttons = [
            PaginatorButton("prev", label = "◀", style = discord.ButtonStyle.primary, row = 0),
            PaginatorButton("next", label = "▶", style = discord.ButtonStyle.primary, row = 0)
        ]

        paginator = CustomPaginator(
            pages = pages,
            use_default_buttons = False,
            show_indicator = False,
            custom_buttons = buttons,
            timeout = 600
        )

        await paginator.respond(ctx.interaction)

def setup(bot):
    bot.add_cog(help_Command(bot))