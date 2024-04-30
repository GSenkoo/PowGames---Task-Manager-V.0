import discord
import math
import function.data as data_manager
from discord.ext import commands
from datetime import datetime


class complete_task_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description = "Envoyer une demande pour considérer une tâche comme faite.")
    @discord.guild_only()
    async def complete_task(self, ctx):
        users_profil = data_manager.get_data("db", "users_profil")
        user_profil = users_profil[str(ctx.author.id)]

        if not user_profil:
            await ctx.respond("Vous n'êtes pas enregistrés.", ephemeral = True)
            return
        
        if not len(user_profil['current_tasks']) > 0:
            await ctx.respond("Vous n'avez pas de tâche.", ephemeral = True)
            return
        
        class ChooseTask(discord.ui.View):
            @discord.ui.select(
                placeholder = "Choisir une tâche",
                options = [
                    discord.SelectOption(
                        label = task,
                        emoji = "💼"
                    ) for task in user_profil["current_tasks"]
                ]
            )
            async def select_callback(self, select, interaction):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral = True)
                    return
                
                users_profil = data_manager.get_data("db", "users_profil")
                tasks = data_manager.get_data("db", "tasks")

                task = select.values[0]

                user_profil = users_profil[str(ctx.author.id)]
                if not user_profil:
                    await interaction.response.send_message("Vous n'êtes plus enregistrés.", ephemeral = True)
                    return
                
                task_data = tasks[task]
                if not task_data:
                    await interaction.response.send_message(f"La tâche **{task}** n'éxiste plus.", ephemeral = True)
                    return
                
                if not task in user_profil['current_tasks']:
                    await interaction.response.send_message(f"La tâche **{task}** ne vous est plus affecté.", ephemeral = True)
                    return
                
                def get_user_in_task(task_name):
                    users_profil = data_manager.get_data("db", "users_profil")
                    users = []
                    for user_id, user_data in users_profil.items():
                        if task_name in user_data['current_tasks']:
                            users.append(user_id)
                    return users
                
                class AskToComplete(discord.ui.View):
                    @discord.ui.button(
                        label = "Accepter",
                        emoji = "✅",
                        style = discord.ButtonStyle.secondary
                    )
                    async def button_callback(self, button, interaction):
                        users_profil = data_manager.get_data("db", "users_profil")
                        user_profil = users_profil[str(ctx.author.id)]

                        if not user_profil:
                            await interaction.response.send_message(f"<@{ctx.author.id}> n'est plus enregistré.", ephemeral = True)
                            return
                        
                        if task not in user_profil['current_tasks']:
                            await interaction.response.send_message(f"<@{ctx.author.id}> n'est plus affecté à la tâche **{task}**", ephemeral = True)
                            return
                        
                        tasks = data_manager.get_data("db", "tasks")
                        task_data = tasks[task]
                        
                        if not task_data:
                            await interaction.response.send_message(f"La tâche **{task}** n'éxiste plus.")
                            return
                        
                        class AcceptedButton(discord.ui.View):
                            @discord.ui.button(
                                label = f"Accepté par {interaction.user.display_name}",
                                style = discord.ButtonStyle.success,
                                disabled = True
                            )
                            async def _callback(self, button, interaction):
                                pass
    
                        
                        await interaction.response.send_message(f"La demande de complétion a été accepté avec succès.", ephemeral = True)
                        await interaction.message.edit(
                            view = AcceptedButton(timeout = None)
                        )
                        
                        users_in_task = get_user_in_task(task)
                        points_per_ppl = math.floor(task_data['points'] / len(users_in_task))

                        user_profil['current_points'] = user_profil['current_points'] + points_per_ppl
                        user_profil['current_tasks'].remove(task)
                        data_manager.set_data("db", f"users_profil/{ctx.author.id}", user_profil)

                        try:
                            logs_channel = data_manager.get_data("db", "tasks_logs_channel")
                            logs_channel = await interaction.guild.fetch_channel(logs_channel)
                            await logs_channel.send(embed = discord.Embed(color = 0xFFFFFF, description = f"**{points_per_ppl}** points ont été ajoutés à <@{ctx.author.id}> pour avoir complété la tâche **{task}**."))
                        except:
                            pass

                        try:
                            await ctx.author.send(f"Votre demande de complétion pour la tâche **{task}** a été **acceptée** par <@{interaction.user.id}>, vous avez reçu **{points_per_ppl}** points.")
                        except:
                            pass

                        users_in_task.remove(str(ctx.author.id))

                        for user_id in users_in_task:
                            data_manager.set_data("db", f"users_profil/{user_id}/current_points", data_manager.get_data("db", f"users_profil/{user_id}/current_points") + points_per_ppl)
                            data_manager.set_data("db", f"users_profil/{user_id}/current_tasks", data_manager.get_data("db", f"users_profil/{user_id}/current_tasks").remove(task))

                            try:
                                logs_channel = data_manager.get_data("db", "tasks_logs_channel")
                                logs_channel = await interaction.guild.fetch_channel(logs_channel)
                                await logs_channel.send(embed = discord.Embed(color = 0xFFFFFF, description = f"**{points_per_ppl}** points ont été ajoutés à <@{user_id}> pour avoir complété la tâche **{task}**."))
                            except:
                                pass

                            try:
                                user = await ctx.guild.fetch_member(int(user_id))
                                await user.send(f"Vous avez complété avec certaines personnes la tâche **{task}**, **{points_per_ppl}** points vous ont étés ajoutés.")
                            except:
                                pass
                        
                        try:
                            logs_channel = data_manager.get_data("db", "tasks_logs_channel")
                            logs_channel = await interaction.guild.fetch_channel(logs_channel)
                            await logs_channel.send(embed = discord.Embed(color = 0xFFFFFF, description = f"<@{interaction.user.id}> a accepté la complétion de la tâche **{task}**."))
                        except:
                            pass

                        tasks = data_manager.get_data("db", "tasks")
                        del tasks[task]
                        data_manager.set_data("db", "tasks", tasks)

                    @discord.ui.button(
                        label = "Refuser",
                        emoji = "❌",
                        style = discord.ButtonStyle.secondary
                    )
                    async def _button_callback(self, button, interaction):
                        if interaction.user.id not in data_manager.get_data("config", "admins"):
                            await interaction.response.send_message("Vous n'êtes pas autorisés à intéragir avec ceci.", ephemeral = True)
                            return
                        
                        class CanceledButton(discord.ui.View):
                            @discord.ui.button(
                                label = f"Refusé par {interaction.user.display_name}",
                                style = discord.ButtonStyle.danger,
                                disabled = True
                            )
                            async def _callback():
                                pass

                        await interaction.message.edit(view = CanceledButton(timeout = None))
                        await interaction.response.defer()

                        try:
                            await ctx.author.send(f"Votre demande de complétion pour la tâche **{task}** a été **refusée** par <@{interaction.user.id}>")
                        except:
                            pass

                        try:
                            logs_channel = data_manager.get_data("db", "tasks_logs_channel")
                            logs_channel = await interaction.guild.fetch_channel(logs_channel)
                            await logs_channel.send(embed = discord.Embed(color = 0xFFFFFF, description = f"<@{interaction.user.id}> a refusé une demande de complétion de <@{ctx.author.id}>."))
                        except:
                            pass
                

                embed = discord.Embed(
                    title = "Demande de complétion d'une tâche",
                    author = discord.EmbedAuthor(
                        icon_url = ctx.author.avatar.url,
                        name = ctx.author.display_name
                    ),
                    color = 0xFFFFFF,
                    description = f"Nom de la tâche : **{task}**\n"
                    + f"Nombre d'utilisateur sur celle-ci : **{len(get_user_in_task(task))}/{task_data['max_users_count']}**\n\n"
                    + f"*Expiration de la demande :* ***<t:{round(datetime.now().timestamp() + 60 * 60 * 3)}:R>***"
                )

                try:
                    confirm_channel = data_manager.get_data("db", "tasks_confirm_channel")
                    confirm_channel = await interaction.guild.fetch_channel(confirm_channel)
                    
                    await confirm_channel.send(embed = embed, view = AskToComplete(timeout = 60 * 60 * 3))
                except:
                    await interaction.message.response(f"Impossible d'envoyer la demande, vérifiez que le salon de confirmation a bien été définis & que j'ai les permissions nécessaires.", ephemeral = True)
                    return

                await interaction.message.edit(f"Demande de complétion pour la tâche **{task}** envoyée.", embed = None, view = None)
                await interaction.response.defer()

                try:
                    logs_channel = data_manager.get_data("db", "tasks_logs_channel")
                    logs_channel = await interaction.guild.fetch_channel(logs_channel)
                    await logs_channel.send(embed = discord.Embed(color = 0xFFFFFF, description = f"<@{ctx.author.id}> a envoyé une demande de complétion pour la tâche **{task}**."))
                except:
                    pass
        
        await ctx.respond(
            embed = discord.Embed(
                title = "Choisissez une tâche.",
                color = 0xFFFFFF
            ),
            view = ChooseTask(timeout = 600)
        )
        
    

def setup(bot):
    bot.add_cog(complete_task_Command(bot))