import discord
from discord.ext import commands
import os
import sys
import asyncio

class ConfirmShutdownView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=60) 
        self.bot = bot
        self.confirmed = False

    @discord.ui.button(label="✅ Confirm Shutdown", style=discord.ButtonStyle.danger)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.bot.owner_id or interaction.user.id == 676722563681878016:
            self.confirmed = True
            await interaction.response.edit_message(content="Bot sedang dimatikan. Mohon tunggu sebentar...", view=None)
            await self.bot.close()
            # Shutdown event loop gracefully
            await asyncio.sleep(1)  # Tambahkan sedikit delay agar bot bisa menutup semua koneksi dengan benar
            await self.bot.loop.shutdown_asyncgens()
            sys.exit()  # Ini terakhir untuk menutup program
        else:
            await interaction.response.send_message("Anda tidak memiliki izin untuk melakukan aksi ini.", ephemeral=True)

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.bot.owner_id or interaction.user.id == 676722563681878016:
            await interaction.response.edit_message(content="Force shutdown dibatalkan.", view=None)
        else:
            await interaction.response.send_message("Anda tidak memiliki izin untuk melakukan aksi ini.", ephemeral=True)

class MaintenanceView(discord.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @discord.ui.button(label="🔄 Restart", style=discord.ButtonStyle.danger)
    async def restart_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.bot.owner_id or interaction.user.id == 676722563681878016:
            await interaction.response.send_message("Bot sedang di-restart. Mohon tunggu sebentar...")
            await self.bot.close()
            os.execv(sys.executable, ['python'] + sys.argv)
        else:
            await interaction.response.send_message("Anda tidak memiliki izin untuk melakukan aksi ini.", ephemeral=True)
 
    @discord.ui.button(label="🛑 Force Shutdown", style=discord.ButtonStyle.danger)
    async def shutdown_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.bot.owner_id or interaction.user.id == 676722563681878016:
            # Kirim pesan konfirmasi dengan tombol
            await interaction.response.send_message(
                "Anda yakin ingin mematikan bot? Tekan tombol di bawah untuk mengonfirmasi atau membatalkan.",
                view=ConfirmShutdownView(self.bot)
            )
        else:
            await interaction.response.send_message("Anda tidak memiliki izin untuk melakukan aksi ini.", ephemeral=True)
