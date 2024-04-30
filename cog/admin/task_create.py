import discord
import function.data as data_manager
from discord.ext import commands


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


class TaskModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="Titre de la tâche", min_length = 3, max_length = 25))
        self.add_item(discord.ui.InputText(label="Description de la tâche", style = discord.InputTextStyle.long, min_length = 3, max_length = 1250))
        self.add_item(discord.ui.InputText(label = "Points", min_length = 1, max_length = 4, placeholder = "Entre 0 et 1000"))
        self.add_item(discord.ui.InputText(label = "Nombre d'utilisateur maximum", min_length = 1, max_length = 100, placeholder = "Entre 1 et 100"))

    async def callback(self, interaction: discord.Interaction):
        tasks = data_manager.get_data("db", "tasks")
            
        if "/" in self.children[0].value:
            await interaction.response.send_message("Vous ne pouvez pas mettre de \"/\" dans le nom de la tâche, contrainte imposé par la base de donnée.", ephemeral = True)
            return
        
        for task_name in tasks.keys():
            if task_name == self.children[0].value:
                await interaction.response.send_message("Ce nom de tâche éxiste déjà.", ephemeral = True)
                return

        if not self.children[2].value.isdigit():
            await interaction.response.send_message("Nombre de points invalide, le nombre donné est invalide.", ephemeral = True)
            return
        
        if not 0 <= int(self.children[2].value) <= 1000:
            await interaction.response.send_message("Nombre de points invalide, le nombre doit être entre 0 (inclu) et 100 (inclu).", ephemeral = True)
            return
        
        if not self.children[3].value.isdigit():
            await interaction.response.send_message("Nombre d'utilisateur maximum pour la tâche invalide, vous devez mettre un nombre.", ephemeral = True)
            return
        
        if not 1 <= int(self.children[3].value) <= 100:
            await interaction.response.send_message("Nombre d'utilisateur maximum pour la tâche invalide, vous devez mettre un nombre entre 1 (inclu) et 100 (inclu).", ephemeral = True)
            return


        data = {
            "name": self.children[0].value,
            "description": self.children[1].value,
            "points": int(self.children[2].value),
            "roles_allowed": [],
            "max_users_count": int(self.children[3].value),
            "made_by": interaction.user.id
        }
        
        modal_interaction = interaction
        class ChooseAllowedRoles(discord.ui.View):
            @discord.ui.select(
                placeholder = "Choisir un/des rôle(s)",
                min_values = 1,
                max_values = len(roles_menu),
                options = roles_menu
            )
            async def select_callback(self, select, interaction):
                if interaction.user.id != modal_interaction.user.id:
                    await interaction.respond("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral = True)
                    return
                
                tasks = data_manager.get_data("db", "tasks")

                for task_name in tasks.keys():
                    if task_name == data["name"]:
                        await interaction.message.edit("Entre temps, on dirait bien qu'une tâche avec le même nom a été créée.", view = None, embed = None)
                        return
                
                data["roles_allowed"] = select.values
                data_manager.set_data("db", f"tasks/{data['name']}", data)

                await interaction.message.edit(f"La tâche **{data['name']}** a été créée avec succès.", view = None, embed = None)

                try:
                    logs_channel = await interaction.guild.fetch_channel(logs_channel)
                    await logs_channel.send(embed = discord.Embed(description = f"<@{interaction.user.id}> vient de créer la tâche **{data['name']}**.", color = 0xFFFFFF))
                except:
                    pass

            
        await interaction.response.send_message(
            embed = discord.Embed(
                title = "Choisissez les rôles concernés.",
                color = 0xFFFFFF
            ),
            view = ChooseAllowedRoles()
        )

class task_create_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description = "Créer une tâche")
    @discord.guild_only()
    async def task_create(self, ctx):
        if ctx.author.id not in data_manager.get_data("config", "admins"):
            await ctx.respond("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral = True)
            return
        
        await ctx.send_modal(TaskModal(title = "Task Manager"))


def setup(bot):
    bot.add_cog(task_create_Command(bot))