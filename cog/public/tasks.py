import discord
import function.data as data_manager
from discord.ext import commands
from discord.ext.pages import Page, Paginator, PaginatorButton
from datetime import datetime

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

class CustomPaginator(Paginator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.usercheck:
            if self.user != interaction.user:
                await interaction.response.send_message("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral = True)
                return False
        return True

class tasks_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        def get_user_in_task(task_name):
            users_profil = data_manager.get_data("db", "users_profil")
            
            user_in_task = []
            for user_id, user_data in users_profil.items():
                if task_name in user_data["current_tasks"]:
                    user_in_task.append(user_id)
            return user_in_task
        
        self.get_user_in_task = get_user_in_task

    @discord.slash_command(description = "Voir les tâches actuellements disponibles")
    @discord.guild_only()
    async def tasks(self, ctx):
        tasks = data_manager.get_data("db", "tasks")
        pages = []
        
        get_user_in_task = self.get_user_in_task

        for task_name, task_data in tasks.items():
            class MyButton(discord.ui.View):
                async def on_timeout(self):
                    self.clear_items()

                @discord.ui.button(
                    label = "Envoyer une demande",
                    emoji = "📝",
                    custom_id = task_name,
                    style = discord.ButtonStyle.success,
                    row = 1
                )
                async def button_callback(self, button, interaction):
                    the_task_name = button.custom_id
                    tasks = data_manager.get_data("db", "tasks")

                    if interaction.user.id != ctx.author.id:
                        await interaction.response.send_message("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral  = True)
                        return
                    
                    users_profil = data_manager.get_data("db", "users_profil")
                    registred = False

                    for user_id, user_data in users_profil.items():
                        if user_id == str(interaction.user.id):
                            registred = True
                            user_profil = user_data
                            break

                    if not registred:
                        await interaction.response.send_message("Vous devez êtres enregistrés pour faire ceci.", ephemeral = True)
                        return
                    
                    if the_task_name in user_profil["current_tasks"]:
                        await interaction.response.send_message("Vous êtes déjà affecter à cette tâche.", ephemeral = True)
                        return
                    
                    task_exists = False
                    for task_name, task_d in tasks.items():
                        if task_name == the_task_name:
                            task_exists = True
                            task_data = task_d
                            break

                    if not task_exists:
                        await interaction.response.send_message(f"La tâche **{the_task_name}** n'éxiste plus.", ephemeral = True)
                        return   
                

                    allowed = False
                    for user_role in user_profil["current_roles"]:
                        if user_role in task_data['roles_allowed']:
                            allowed = True
                    
                    if not allowed:
                        await interaction.response.send_message(f"La tâche **{the_task_name}** nécessite des rôles que vous n'avez pas", ephemeral = True)
                        return

                    
                    if len(user_profil["current_tasks"]) >= user_profil["max_tasks"]:
                        await interaction.response.send_message("Vous avez déjà atteint votre limite de tâche.", ephemeral = True)
                        return
                    
                    async def send_request(current_interaction, text_added = None, interaction_if_first_interaction_is_a_modal = None):

                        users_profil = data_manager.get_data("db", "users_profil")
                        tasks = data_manager.get_data("db", "tasks")

                        registred = False
                        for user_id, user_data in users_profil.items():
                            if user_id == str(current_interaction.user.id):
                                registred = True
                                user_profil = user_data
                                break

                        task_exist = False
                        for task_name, task_d in tasks.items():
                            if task_name == the_task_name:
                                task_exist = True
                                task_data = task_d
                                break

                        if the_task_name in user_profil["current_tasks"]:
                            await interaction.response.send_message("Vous êtes déjà affecter à cette tâche.", ephemeral = True)
                            return
                        
                        if len(user_profil["current_tasks"]) >= user_profil["max_tasks"]:
                            await interaction.response.send_message("Vous avez déjà atteint votre limite de tâche.", ephemeral = True)
                            return

                        if not registred:
                            await current_interaction.response.send_message("Vous n'êtes plus enregistrés.", ephemeral = True)
                            return
                        
                        if not task_exist:
                            await interaction.response.send_message(f"La tâche **{the_task_name}** n'éxiste plus.")
                            return

                        time = round(datetime.now().timestamp())
                        embed = discord.Embed(
                            author = discord.EmbedAuthor(
                                name = current_interaction.user.display_name,
                                icon_url = current_interaction.user.avatar.url
                            ),
                            title = "Demande d'affectation à une tâche",
                            description = f"- Nom de la tâche : **{the_task_name}**\n"
                            + f"- Nombre d'utilisateurs sur celle-ci : **{len(get_user_in_task(the_task_name))}/{task_data['max_users_count']}**\n\n"

                            + f"**__Ajout de l'auteur__**\n"
                            + (f"{text_added}" if text_added else "*Aucun commentaire*")
                            
                            + f"\n\n*Expiration de la demande :* ***<t:{time + (60 * 60 * 3)}:R>***",
                            color = 0xFFFFFF
                        )

                        confirm_channel = data_manager.get_data("db", "tasks_confirm_channel")

                        class ConfirmTask(discord.ui.View):
                            async def on_timeout(self):
                                self.clear_items()

                            @discord.ui.button(
                                label = "Accepter",
                                emoji = "✅",
                                style = discord.ButtonStyle.secondary
                            )
                            async def confirm_callback(self, button, interaction):
                                if interaction.user.id not in data_manager.get_data("config", "admins"):
                                    await interaction.response.send_message("Seul les administrateurs du bot sont autorisés à faire ceci")
                                    return
                                
                                users_profil = data_manager.get_data("db", "users_profil")
                                tasks = data_manager.get_data("db", "tasks")

                                registered = False
                                for user_id, user_data in users_profil.items():
                                    if user_id == str(ctx.author.id):
                                        registered = True
                                        user_profil = user_data
                                        break
                                
                                if not registered:
                                    await interaction.response.send_message(f"<@{ctx.author.id}> n'est plus enregistré.", ephemeral = True)
                                    return
                                
                                if len(user_profil['current_tasks']) >= user_profil['max_tasks']:
                                    await interaction.response.send_message(f"<@{ctx.author.id}> a déjà atteint sa limite de tâche.", ephemeral = True)
                                    return
                                
                                if the_task_name in user_profil['current_tasks']:
                                    await interaction.response.send_message(f"<@{ctx.author.id}> a déjà été affecté de la tâche **{the_task_name}**.", ephemeral = True)
                                    return
                                
                                task_exists = False
                                for task_name, task_d in tasks.items():
                                    if task_name == the_task_name:
                                        task_exists = True
                                        task_data = task_d
                                        break
                                
                                if not task_exists:
                                    await interaction.response.send_message(f"La tâche **{the_task_name}** n'éxiste plus.", ephemeral = True)
                                    return
                                
                                if len(get_user_in_task(the_task_name)) >= task_data["max_users_count"]:
                                    await interaction.response.send_message(f"Le nombre d'utilisateur dans la tâche **{the_task_name}** est déjà à son maximum", ephemeral = True)
                                    return
                                
                                user_profil["current_tasks"].append(the_task_name)
                                data_manager.set_data("db", f"users_profil/{ctx.author.id}", user_profil)

                                class AcceptedButton(discord.ui.View):
                                    @discord.ui.button(
                                        style = discord.ButtonStyle.success,
                                        label = f"Accepté par {interaction.user.display_name}",
                                        disabled = True
                                    )
                                    async def callback(self, button, interaction):
                                        pass

                                await interaction.message.edit(
                                    view = AcceptedButton(timeout = None)
                                )

                                await interaction.response.send_message(f"La tâche **{the_task_name}** a bien été assignée à <@{ctx.author.id}>", ephemeral = True)
                                try:
                                    await ctx.author.send(f"Votre demande pour la tâche **{the_task_name}** a été **acceptée** par <@{interaction.user.id}>.")
                                except:
                                    pass

                                try:
                                    logs_channel = data_manager.get_data("db", "tasks_logs_channel")
                                    logs_channel = await interaction.guild.fetch_channel(logs_channel)
                                    await logs_channel.send(embed = discord.Embed(description = f"<@{interaction.user.id}> vient d'accepter une affectation de <@{ctx.author.id}>.", color = 0xFFFFFF))
                                except:
                                    pass
                                

                            @discord.ui.button(
                                label = "Refuser",
                                style = discord.ButtonStyle.secondary,
                                emoji = "❌"
                            )
                            async def cancel_callback(self, button, interaction):
                                if interaction.user.id not in data_manager.get_data("config", "admins"):
                                    await interaction.response.send_message("Seul les administrateurs du bot sont autorisés à faire ceci")
                                    return
                                
                                class CanceledButton(discord.ui.View):
                                    @discord.ui.button(
                                        style = discord.ButtonStyle.danger,
                                        label = f"Refusé par {interaction.user.display_name}",
                                        disabled = True
                                    )
                                    async def callback(self, button, interaction):
                                        pass
                                
                                await interaction.message.edit(
                                    view = CanceledButton(timeout = None)
                                )

                                try:
                                    await ctx.author.send(f"Votre demande pour la tâche **{the_task_name}** a été **refusé** par <@{interaction.user.id}>.")
                                except:
                                    pass

                                try:
                                    logs_channel = data_manager.get_data("db", "tasks_logs_channel")
                                    logs_channel = await interaction.guild.fetch_channel(logs_channel)
                                    await logs_channel.send(embed = discord.Embed(description = f"<@{interaction.user.id}> vient de refuser une affectation de <@{ctx.author.id}>.", color = 0xFFFFFF))
                                except:
                                    pass

                        try:
                            confirm_channel = await current_interaction.guild.fetch_channel(confirm_channel)
                            await confirm_channel.send(
                                embed = embed,
                                view = ConfirmTask(timeout = 60 * 60 * 3)
                            )
                        except:
                            await current_interaction.response.send_message("Impossible d'envoyer votre demandes, vérifiez que celui-ci a été définis par les admins du bot & que j'ai les permissions nécessaires.", ephemeral = True)
                            return
                        

                        await current_interaction.message.edit("Votre demande a été correctement envoyé.", embed = None, view = None)
                        if interaction_if_first_interaction_is_a_modal:
                            await interaction_if_first_interaction_is_a_modal.message.edit(
                                content = "Demande envoyé",
                                embed = None,
                                view = None
                            )

                        try:
                            logs_channel = data_manager.get_data("db", "tasks_logs_channel")
                            logs_channel = await interaction.guild.fetch_channel(logs_channel)
                            await logs_channel.send(embed = discord.Embed(description = f"<@{ctx.author.id}> a demandé une affectation pour la tâche **{the_task_name}**.", color = 0xFFFFFF))
                        except:
                            pass
                    
                    previous_interaction = interaction
                    class RequestText(discord.ui.View):
                        async def on_timeout(self):
                            self.clear_items()

                        @discord.ui.button(
                            label = "Ajouter",
                            emoji = "📝",
                            style = discord.ButtonStyle.success
                        )
                        async def add_callback(self, button, interaction):
                            if previous_interaction.user.id != interaction.user.id:
                                await interaction.response.send_message("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral = True)
                                return
                            
                            previous_interaction_ = interaction
                            
                            class AddText(discord.ui.Modal):
                                def __init__(self, *args, **kwargs) -> None:
                                    super().__init__(*args, **kwargs)

                                    self.add_item(discord.ui.InputText(label="Commentaire", style=discord.InputTextStyle.long, max_length = 1000, min_length = 5))

                                async def callback(self, interaction: discord.Interaction):
                                    await interaction.response.send_message("Votre commentaire a été pris en compte.", ephemeral = True)
                                    await send_request(interaction, self.children[0].value, previous_interaction_)
                            
                            await interaction.response.send_modal(AddText(title = "Ajouter un commentaire"))

                        @discord.ui.button(
                            label = "Envoyer",
                            emoji = "📮",
                            style = discord.ButtonStyle.danger
                        )
                        async def just_send_callback(self, button, interaction):
                            if previous_interaction.user.id != interaction.user.id:
                                await interaction.response.send_message("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral = True)
                                return

                            await send_request(interaction)

                    await interaction.message.edit(
                        embed = discord.Embed(
                            title = "Souhaitez vous ajouter un commentaire ou tout simplement envoyer votre demande sans en ajouter?",
                            color = 0xFFFFFF
                        ),
                        view = RequestText(timeout = 300)
                    )

            pages.append(
                Page(
                    embeds = [
                        discord.Embed(
                            title = task_name,
                            color = 0xFFFFFF,
                            description = task_data["description"]
                            + "\n\n**__Informations__**\n"
                            + f"- Ajouté par <@{task_data['made_by']}>\n"
                            + f"- Nombre de points : **{task_data['points']}**\n"
                            + f"- Utilisateurs : **{len(get_user_in_task(task_name))}/{task_data['max_users_count']}**\n"
                            + f"- Rôles autorisés :\n" + (" - "+ "\n - ".join([role_id_to_name[role] for role in task_data["roles_allowed"]]) if len(task_data['roles_allowed']) > 0 else " - *Aucun rôles*")
                        )
                    ],
                    custom_view = MyButton(timeout = None)
                )
            )

        buttons = [
            PaginatorButton("prev", label = "◀", style = discord.ButtonStyle.primary, row = 0),
            PaginatorButton("page_indicator", style = discord.ButtonStyle.gray, disabled = True, row = 0),
            PaginatorButton("next", label = "▶", style = discord.ButtonStyle.primary, row = 0)
        ]

        paginator = CustomPaginator(
            pages = pages,
            use_default_buttons = False,
            custom_buttons = buttons,
            timeout = 600
        )

        await paginator.respond(ctx.interaction)


def setup(bot):
    bot.add_cog(tasks_Command(bot))