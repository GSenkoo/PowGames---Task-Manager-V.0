import discord
import math
import function.data as data_manager
from discord.ext import commands
from discord.ext.pages import Page, Paginator, PaginatorButton


class CustomPaginator(Paginator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.usercheck:
            if self.user != interaction.user:
                await interaction.response.send("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral = True)
                return False
        return True

class task_delete_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description = "Supprimer une tâche")
    @discord.guild_only()
    async def task_delete(self, ctx):
        if ctx.author.id not in data_manager.get_data("config", "admins"):
            await ctx.respond("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral = True)
            return
        
        tasks = data_manager.get_data("db", "tasks")
        tasks = list(tasks.keys())

        if len(tasks) == 0:
            await ctx.respond("Il n'y a aucune tâches à supprimer.")
            return

        pages = []

        for index in range(0, len(tasks), 20):
            class Tasks(discord.ui.View):
                @discord.ui.select(
                        placeholder = "Choisir une tâche à supprimer",
                        min_values = 1,
                        max_values = 1,
                        row = 0,
                        options = [
                            discord.SelectOption(
                                label = tasks[i],
                                emoji = "💼",
                                value = tasks[i]
                            ) for i in range(index, ( index + 20 if index + 20 < len(tasks)-1 else len(tasks) ))
                        ]
                )
                async def select_callback(self, select, interaction):
                    if interaction.user.id != ctx.author.id:
                        await interaction.response.send_message("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral = True)
                        return

                    tasks = data_manager.get_data("db", "tasks")
                    tasks_names = list(tasks.keys())

                    if select.values[0] not in tasks_names:
                        await interaction.respond(f"La tâche **{select.values[0]}** a l'air de ne plus être présente, quelqu'un a du la supprimer entre temps.", ephemeral = True)
                        return
                    
                    del tasks[select.values[0]]

                    users_profil = data_manager.get_data("db", "users_profil")
                    for user_id, user_data in users_profil.items():
                        if select.values[0] in user_data['current_tasks']:
                            users_profil[str(user_id)]['current_tasks'].remove(select.values[0])

                    data_manager.set_data("db", "users_profil", users_profil)
                    data_manager.set_data("db", "tasks", tasks)
                    await interaction.message.edit(f"La tâche **{select.values[0]}** a été supprimé avec succès.", embed = None, view = None)

                    logs_channel = data_manager.get_data("db", "task_logs_channel")

                    try:
                        logs_channel = await interaction.guild.fetch_channel(logs_channel)
                        await logs_channel.send(embed = discord.Embed(description = f"<@{interaction.user.id}> vient de supprimer la tâche **{select.values[0]}**.", color = 0xFFFFFF))
                    except:
                        pass
                
            pages.append(
                Page(
                    embeds = [
                        discord.Embed(
                            title = "Choisissez une tâche à supprimer.",
                            color = 0xFFFFFF,
                            description = "- " + f"\n- ".join([tasks[i] for i in range(
                                    index, 
                                    ( index + 20 if index + 20 < len(tasks)-1 else len(tasks) )
                                )])
                        ).set_footer(text = f"Page {len(pages)+1}/{math.ceil(len(tasks) / 20)}")
                    ],
                    custom_view = Tasks()
                )
            )
        
        buttons = [
            PaginatorButton("prev", label = "◀", style = discord.ButtonStyle.primary, row = 1),
            PaginatorButton("next", label = "▶", style = discord.ButtonStyle.primary, row = 1)
        ]

        paginator = CustomPaginator(
            pages = pages,
            show_indicator = False,
            use_default_buttons = False,
            custom_buttons = buttons
        )

        await paginator.respond(ctx.interaction)
    

def setup(bot):
    bot.add_cog(task_delete_Command(bot))