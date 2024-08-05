import discord
from func.database import cursor 
from discord.ext import commands

class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    @commands.command()     
    async def status(self, ctx):
        discord_id = ctx.author.id

        query = "SELECT username, rcash, level, created_at FROM users WHERE discord_id = %s"
        cursor.execute(query, (discord_id,))
        result = cursor.fetchone()

        user_data = result

        if user_data:
            embed = discord.Embed(
                title="👤 User Status",
                description=f"Status detail untuk **{user_data['username']}**",
                color=0xC8102E # Warna abu-abu gelap yang modern
            )

            embed.add_field(
                name="💼 **Username**", 
                value=f"`{user_data['username']}`", 
                inline=True
            )
            embed.add_field(
                name="🪙 **R-Cash**", 
                value=f"`{user_data['rcash']} RC`", 
                inline=True
            )
            embed.add_field(
                name="🎯 **Win Gambling**", 
                value=f"`{user_data['level']}`", 
                inline=True
            )
            embed.add_field(
                name="📅 **Account Created**", 
                value=f"`{user_data['created_at'].strftime('%Y-%m-%d %H:%M:%S')}`", 
                inline=False
            )

            embed.set_thumbnail(url=ctx.author.avatar.url)

            embed.set_footer(
                text="Stay active and level up!",
                icon_url="https://i.ibb.co/g4dqgcP/money-mouth-face-svgrepo-com.png"  # URL ke icon custom, sesuaikan jika perlu
            )

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❗ Data pengguna untuk **{ctx.author.name}** tidak ditemukan.")
