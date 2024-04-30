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

roles_menu = [
    discord.SelectOption(
        label = "Scripter",
        emoji = "📜",
        description = "Construit la logique des jeux",
        value = "scripter"
    ),
    discord.SelectOption(
        label = "Modélisateur",
        emoji = "🎨",
        description = "Crée les objets 3D",
        value = "modeler"
    ),
    discord.SelectOption(
        label = "Animateur",
        emoji = "🎬",
        description = "Anime les personnages",
        value = "animator"
    ),
    discord.SelectOption(
        label = "Builder",
        emoji = "🔨",
        description = "Construit les mondes",
        value = "builder"
    ),
    discord.SelectOption(
        label = "VFX Maker",
        emoji = "💥",
        description = "Crée les effets spéciaux.",
        value = "vfx"
    ),
    discord.SelectOption(
        label = "SFX Maker",
        emoji = "🔊",
        description = "Crée les effets sonnores.",
        value = "sfx"
    ),
    discord.SelectOption(
        label = "Graphiste",
        emoji = "📐",
        description = "Crée des images pour le jeu.",
        value = "graphic_designer"
    ),
    discord.SelectOption(
        label = "Staff Discord",
        emoji = "🛡️",
        description = "Gère le serveur discord.",
        value = "discord_staff"
    ),
    discord.SelectOption(
        label = "Autres rôles",
        emoji = "💫",
        description = "Gère d'autres tâches.",
        value = "others"
    )
]


class user_manage_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description = "Gérer un utilisateur")
    @discord.guild_only()
    async def user_manage(self,
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
            await ctx.respond(f"<@{utilisateur.id}> n'est pas enregistré.")
            return
        
        the_interaction = ctx.interaction
        await ctx.respond(f"Chargement des données de {utilisateur.name} en cours...")
        
        user_data = users_profil[str(utilisateur.id)]
        embed = discord.Embed(
            title = f"Gérer {utilisateur.display_name}",
            color = 0xFFFFFF,
            description = 
            f"\nNombre de tâches : **{len(user_data['current_tasks'])}**" +
            f"\nNombre de points : **{user_data['current_points']}**" +
            f"\nRôles : " + (", ".join([role_id_to_name[role] for role in user_data["current_roles"]]) if len(user_data["current_roles"]) != 0 else "*Aucun rôles*") +
            f"\nNombre de tâches autorisés : **{user_data['max_tasks']}**"
        )

        class ManageSelect(discord.ui.View):
            @discord.ui.select(
                placeholder = "Choisir une action",
                row = 0,
                options = [
                    discord.SelectOption(
                        label = "Ajouter une tâche",
                        emoji = "💼",
                        value = "add_task"
                    ),
                    discord.SelectOption(
                        label = "Retirer une tâche",
                        emoji = "❌",
                        value = "remove_task"
                    ),
                    discord.SelectOption(
                        label = "Ajouter des points",
                        emoji = "➕",
                        value = "add_points"
                    ),
                    discord.SelectOption(
                        label = "Retirer des points",
                        emoji = "➖",
                        value = "remove_points"
                    ),
                    discord.SelectOption(
                        label = "Modifier les rôles",
                        emoji = "🎭",
                        value = "edit_roles"
                    ),
                    discord.SelectOption(
                        label = "Définir le nombre de tâche autorisé",
                        emoji = "📝",
                        value = "edit_allowed_tasks"
                    )
                ]
            )
            async def select_callback1(self, select, interaction):
                if ctx.author.id != interaction.user.id:
                    await interaction.response.send_message("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral = True)
                    return

                # checks...
                users_profil = data_manager.get_data("db", "users_profil")

                registered = False
                for user_id in users_profil.keys():
                    if user_id == str(utilisateur.id):
                        registered = True
                        break

                if not registered:
                    await interaction.message.edit(
                        embed = discord.Embed(
                            title = f"<@{utilisateur.id}> n'est plus enregistré.",
                            color = 0xFFFFFF
                        ),
                        view = None
                    )
                    return
                

                # ------------ add task --------------
                if select.values[0] == "add_task":

                    users_profil = data_manager.get_data("db", "users_profil")
                    tasks = data_manager.get_data("db", "tasks")
                    tasks = list(tasks.keys())

                    if users_profil[str(utilisateur.id)]['max_tasks'] <= len(users_profil[str(utilisateur.id)]['current_tasks']):
                        await interaction.response.send_message(f"<@{utilisateur.id}> a atteint sa limite de tâche.", ephemeral = True)
                        return

                    if len(tasks) == 0:
                        await interaction.response.send_message(f"Il n'y a aucune tâches de créé pour le moment.", ephemeral = True)
                        return

                    pages = []

                    for index in range(0, len(tasks), 20):
                        class Tasks(discord.ui.View):
                            @discord.ui.select(
                                    placeholder = f"Choisir une tâche à ajouter",
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
                                users_profil = data_manager.get_data("db", "users_profil")
                                tasks_names = list(tasks.keys())

                                if select.values[0] not in tasks_names:
                                    await interaction.response.send_message(f"La tâche **{select.values[0]}** a l'air de ne plus être présente, quelqu'un a du la supprimer entre temps.", ephemeral = True)
                                    return
                                
                                user_in_the_task = []
                                
                                for user_id, user_data in data_manager.get_data("db", "users_profil").items():
                                    if select.values[0] in user_data["current_tasks"]:
                                        user_in_the_task.append(user_id)
                                
                                if tasks[select.values[0]]["max_users_count"] <= len(user_in_the_task):
                                    await ctx.respond(f"La limite d'utilisateur sur la tâche \"{select.values[0]}\" est de {tasks[select.values[0]]['max_users_count']} utilisateurs, et celle-ci a été atteinte.", epehemeral = True)
                                    return
                                
                                current_user_data = users_profil[str(utilisateur.id)]
                                if current_user_data["max_tasks"] <= len(current_user_data["current_tasks"]):
                                    await ctx.respond(f"<@{utilisateur.id}> a atteint sa limite de tâche pendant que vous étiez entrain de choisir.")
                                    return
                                current_user_data['current_tasks'].append(select.values[0])
                                users_profil[str(utilisateur.id)] = current_user_data

                                data_manager.set_data("db", "users_profil", users_profil)
                                
                                await interaction.message.edit(f"La tâche **{select.values[0]}** a été assignée à <@{utilisateur.id}>.", embed = None, view = None, delete_after = 3)
                                
                                user_data = current_user_data
                                try:
                                    await the_interaction.edit_original_response(
                                        embed = discord.Embed(
                                            title = f"Gérer {utilisateur.display_name}",
                                            color = 0xFFFFFF,
                                            description = 
                                            f"\nNombre de tâches : **{len(user_data['current_tasks'])}**" +
                                            f"\nNombre de points : **{user_data['current_points']}**" +
                                            f"\nRôles : " + (", ".join([role_id_to_name[role] for role in user_data["current_roles"]]) if len(user_data["current_roles"]) != 0 else "*Aucun rôles*") +
                                            f"\nNombre de tâches autorisés : **{user_data['max_tasks']}**"
                                        )
                                    )

                                except:
                                    pass

                                logs_channel = data_manager.get_data("db", "tasks_logs_channel")
                                try:
                                    logs_channel = await interaction.guild.fetch_channel(logs_channel)
                                    await logs_channel.send(embed = discord.Embed(description = f"<@{interaction.user.id}> vient d'assigner la tâche **{select.values[0]}** à <@{utilisateur.id}>.", color = 0xFFFFFF))
                                except:
                                    pass
                            
                        pages.append(
                            Page(
                                embeds = [
                                    discord.Embed(
                                        title = f"Choisissez une tâche à ajouter à {utilisateur.display_name}.",
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
                        custom_buttons = buttons,
                        timeout = 600
                    )

                    await paginator.respond(interaction)

                # ------------- remove task ------------------
                elif select.values[0] == "remove_task":
                    user_data = users_profil[str(utilisateur.id)]
                    
                    if len(user_data['current_tasks']) == 0:
                        await interaction.response.send_message(f"<@{utilisateur.id}> n'a pas de tâche.", ephemeral = True)
                        return
                    
                    user_tasks = user_data['current_tasks']

                    class ChooseTaskToRemove(discord.ui.View):
                        @discord.ui.select(
                            placeholder = "Choisissez une tâche",
                            options = [
                                discord.SelectOption(
                                    label = task,
                                    emoji = "💼"
                                ) for task in user_tasks
                            ]
                        )
                        async def select_callback_(self, select, interaction):
                            if interaction.user.id != ctx.author.id:
                                await interaction.response.send_message("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral = True)
                                return
                            
                            users_profil = data_manager.get_data("db", "users_profil")

                            registered = False
                            for user_id in users_profil.keys():
                                if user_id == str(utilisateur.id):
                                    registered = True
                                    break

                            if not registered:
                                await interaction.message.response(f"<@{utilisateur.id}> n'est plus enregistré.", ephemeral = True)
                                return
                            
                            user_data = users_profil[str(utilisateur.id)]
                            if not select.values[0] in user_data["current_tasks"]:
                                await interaction.message.response(f"<@{utilisateur.id}> n'a plus la tâche **{select.values[0]}**")
                                return
                            
                            user_data["current_tasks"].remove(select.values[0])
                            users_profil[str(utilisateur.id)] = user_data

                            data_manager.set_data("db", "users_profil", users_profil)

                            await interaction.message.edit(f"La tâche **{select.values[0]}** a été retirée des tâches de <@{utilisateur.id}>", embed = None, view = None, delete_after = 3)

                            try:
                                await the_interaction.edit_original_response(
                                    embed = discord.Embed(
                                        title = f"Gérer {utilisateur.display_name}",
                                        color = 0xFFFFFF,
                                        description = 
                                        f"\nNombre de tâches : **{len(user_data['current_tasks'])}**" +
                                        f"\nNombre de points : **{user_data['current_points']}**" +
                                        f"\nRôles : " + (", ".join([role_id_to_name[role] for role in user_data["current_roles"]]) if len(user_data["current_roles"]) != 0 else "*Aucun rôles*") +
                                        f"\nNombre de tâches autorisés : **{user_data['max_tasks']}**"
                                    )
                                )

                            except:
                                pass

                            logs_channel = data_manager.get_data("db", "tasks_logs_channel")
                            try:
                                logs_channel = await interaction.guild.fetch_channel(logs_channel)
                                await logs_channel.send(embed = discord.Embed(description = f"<@{interaction.user.id}> vient de retirer la tâche **{select.values[0]}** à <@{utilisateur.id}>.", color = 0xFFFFFF))
                            except:
                                pass


                    await interaction.response.send_message(
                        embed = discord.Embed(
                            title = "Choisissez une tâche à retirer",
                            color = 0xFFFFFF,
                            description = "- " + "\n- ".join(user_tasks)
                        ),
                        view = ChooseTaskToRemove(timeout = 600)
                    )
                    
                # ------------ add points & remove points --------------
                elif select.values[0] == "add_points" or select.values[0] == "remove_points":
                    add = True if select.values[0] == "add_points" else False

                    class AddPointsModal(discord.ui.Modal):
                        def __init__(self, *args, **kwargs) -> None:
                            super().__init__(*args, **kwargs)

                            self.add_item(discord.ui.InputText(label = "Nombre de points", min_length = 1, max_length = 10, placeholder = f"Nombres de points à {'ajouter' if add else 'retirer'}"))

                        async def callback(self, interaction: discord.Interaction):
                            if interaction.user.id != ctx.author.id:
                                await interaction.response.send_message("Vous n'êtes pas autorisés à intéragir avec ceci.")
                                return
                            
                            if not self.children[0].value.isdigit():
                                await interaction.response.send_message("Nombre de points invalide, merci de donner un nombre.", ephemeral = True)
                                return
                            
                            users_profil = data_manager.get_data("db", "users_profil")
                            registered = False
                            for user_id, user_data in users_profil.items():
                                if user_id == str(utilisateur.id):
                                    registered = True
                                    user_profil = user_data
                                    break

                            if not registered:
                                await interaction.response.send_message(f"<@{utilisateur.id}> n'est plus enregistré.", ephemeral = True)
                                return
                            
                            if add:
                                user_profil["current_points"] = user_profil["current_points"] + int(self.children[0].value)
                            else:
                                if user_profil["current_points"] - int(self.children[0].value) < 0:
                                    await interaction.response.send_message(f"Vous ne pouvez pas définir un nombre de points négatif.", ephemeral = True)
                                    return
                                
                                user_profil["current_points"] = user_profil["current_points"] - int(self.children[0].value)

                            users_profil[str(utilisateur.id)] = user_profil

                            data_manager.set_data("db", "users_profil", users_profil)

                            await interaction.response.send_message(f"**{self.children[0].value}** points ont été {'ajoutés' if add else 'retiré'} aux points de <@{utilisateur.id}>.", delete_after = 3)

                            user_data = user_profil
                            try:
                                await the_interaction.edit_original_response(
                                    embed = discord.Embed(
                                        title = f"Gérer {utilisateur.display_name}",
                                        color = 0xFFFFFF,
                                        description = 
                                        f"\nNombre de tâches : **{len(user_data['current_tasks'])}**" +
                                        f"\nNombre de points : **{user_data['current_points']}**" +
                                        f"\nRôles : " + (", ".join([role_id_to_name[role] for role in user_data["current_roles"]]) if len(user_data["current_roles"]) != 0 else "*Aucun rôles*") +
                                        f"\nNombre de tâches autorisés : **{user_data['max_tasks']}**"
                                    )
                                )

                            except:
                                pass

                            logs_channel = data_manager.get_data("db", "tasks_logs_channel")
                            try:
                                logs_channel = await interaction.guild.fetch_channel(logs_channel)
                                await logs_channel.send(embed = discord.Embed(
                                    description = f"<@{interaction.user.id}> vient d'ajouter **{self.children[0].value}** points à <@{utilisateur.id}>." \
                                    if add else f"<@{interaction.user.id}> vient de retirer **{self.children[0].value}** points à <@{utilisateur.id}>.",
                                    color = 0xFFFFFF))
                            except:
                                pass
                            
                    await interaction.response.send_modal(AddPointsModal(title = f"Ajouter des points" if add else "Retirer des points"))

                # ----------- edit roles ---------------
                elif select.values[0] == "edit_roles":
                    class SelectRoles(discord.ui.View):
                        @discord.ui.select(
                            max_values = 9,
                            placeholder = "Définir les rôles",
                            options = roles_menu
                        )
                        async def _sellect_callback(self, select, interaction):
                            if interaction.user.id != ctx.author.id:
                                await interaction.response.send_message("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral = True)
                                return
                            
                            users_profil = data_manager.get_data("db", "users_profil")

                            registered = False
                            for user_id, user_data in users_profil.items():
                                if user_id == str(utilisateur.id):
                                    registered = True
                                    break

                            if not registered:
                                await interaction.response.send_message(f"<@{utilisateur.id}> n'est plus enregistré.", ephemeral = True)
                                return
                            
                            users_profil[str(utilisateur.id)]['current_roles'] = select.values
                            data_manager.set_data("db", "users_profil", users_profil)

                            await interaction.message.edit(f"Les rôles de <@{utilisateur.id}> ont correctements étés mis à jour.", embed = None, view = None, delete_after = 3)

                            try:
                                await the_interaction.edit_original_response(
                                    embed = discord.Embed(
                                        title = f"Gérer {utilisateur.display_name}",
                                        color = 0xFFFFFF,
                                        description = 
                                        f"\nNombre de tâches : **{len(user_data['current_tasks'])}**" +
                                        f"\nNombre de points : **{user_data['current_points']}**" +
                                        f"\nRôles : " + (", ".join([role_id_to_name[role] for role in user_data["current_roles"]]) if len(user_data["current_roles"]) != 0 else "*Aucun rôles*") +
                                        f"\nNombre de tâches autorisés : **{user_data['max_tasks']}**"
                                    )
                                )

                            except:
                                pass

                            logs_channel = data_manager.get_data("db", "tasks_logs_channel")
                            try:
                                logs_channel = await interaction.guild.fetch_channel(logs_channel)
                                await logs_channel.send(embed = discord.Embed(description = f"<@{interaction.user.id}> a mis à jour les rôles de <@{utilisateur.id}>.", color = 0xFFFFFF))
                            except:
                                pass

                    await interaction.response.send_message(
                        embed = discord.Embed(
                            title = f"Définissez les rôles de {utilisateur.display_name}",
                            color = 0xFFFFFF,
                            description = f"Rôles atuels de <@{utilisateur.id}> :\n\n" +
                            ("- " + "\n- ".join([role_id_to_name[role] for role in users_profil[str(utilisateur.id)]["current_roles"]])) 
                            if len(users_profil[str(utilisateur.id)]["current_roles"]) > 0 else
                            ("*Aucun rôles*")
                        ),
                        view = SelectRoles(timeout = 600)
                    )

                # ---------- edit allowed tasks ---------------
                elif select.values[0] == "edit_allowed_tasks":
                    class SetTaskCountModal(discord.ui.Modal):
                        def __init__(self, *args, **kwargs) -> None:
                            super().__init__(*args, **kwargs)

                            self.add_item(discord.ui.InputText(label = "Nombre de tâche max.", min_length = 1, max_length = 2, placeholder = f"Entre 1 (inclu) et 25 (inclu)"))

                        async def callback(self, interaction: discord.Interaction):
                            if not self.children[0].value.isdigit():
                                await interaction.response.send_message("Nombre de tâche invalide, merci de donner un nombre valide.", ephemeral = True)
                                return
                            
                            if not 0 < int(self.children[0].value) < 26:
                                await interaction.response.send_message("Nombre de tâche invalide, vous devez indiquer un nombre entre 1 (inclu) et 25 (inclu).", ephemeral = True)
                                return
                            
                            users_profil = data_manager.get_data("db", "users_profil")
                            
                            registered = False
                            for user_id, user_data in users_profil.items():
                                if user_id == str(utilisateur.id):
                                    registered = True
                                    break

                            if not registered:
                                await interaction.response.send_message(f"<@{utilisateur.id}> n'est plus enregistré.", ephemeral = True)

                            if int(self.children[0].value) == users_profil[str(utilisateur.id)]["max_tasks"]:
                                await interaction.response.send_message(f"Le nombre de tâche maximum de <@{utilisateur.id}> est déjà définis à {self.children[0].value}", ephemeral = True)
                                return
                            
                            users_profil[str(utilisateur.id)]["max_tasks"] = int(self.children[0].value)
                            data_manager.set_data("db", "users_profil", users_profil)

                            await interaction.response.send_message(f"Le nombre de tâche maximum de <@{utilisateur.id}> a été définis à {self.children[0].value}.", delete_after = 3)

                            user_data = users_profil[str(utilisateur.id)]
                            try:
                                await the_interaction.edit_original_response(
                                    embed = discord.Embed(
                                        title = f"Gérer {utilisateur.display_name}",
                                        color = 0xFFFFFF,
                                        description = 
                                        f"\nNombre de tâches : **{len(user_data['current_tasks'])}**" +
                                        f"\nNombre de points : **{user_data['current_points']}**" +
                                        f"\nRôles : " + (", ".join([role_id_to_name[role] for role in user_data["current_roles"]]) if len(user_data["current_roles"]) != 0 else "*Aucun rôles*") +
                                        f"\nNombre de tâches autorisés : **{user_data['max_tasks']}**"
                                    )
                                )

                            except:
                                pass

                            logs_channel = data_manager.get_data("db", "tasks_logs_channel")
                            try:
                                logs_channel = await interaction.guild.fetch_channel(logs_channel)
                                await logs_channel.send(embed = discord.Embed(description = f"<@{interaction.user.id}> a définis le nombre de tâche maximum de <@{utilisateur.id}> à **{self.children[0].value}**.", color = 0xFFFFFF))
                            except:
                                pass
                    
                    await interaction.response.send_modal(SetTaskCountModal(title = "Nombres de tâches autorisés"))
                    

        await the_interaction.edit_original_response(
            content = "",
            embed = embed,
            view = ManageSelect(timeout = 600)
        )

def setup(bot):
    bot.add_cog(user_manage_Command(bot))