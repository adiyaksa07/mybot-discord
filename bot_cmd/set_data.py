import discord

OWNER_USERID = 676722563681878016
PRIVATE_CHANNEL = 1268491225883873351

from discord.ext import commands
from func.database import cursor, db

class SetCog(commands.Cog): 
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def addrcash(self, ctx, user_id: int, amount: int):
        if ctx.channel.id == PRIVATE_CHANNEL: 
            if ctx.author.id == OWNER_USERID or ctx.author.id == self.bot.owner_id:
                cursor.execute("SELECT rcash FROM users WHERE discord_id=%s", (user_id, ))
                data = cursor.fetchone()

                if data is None: 
                    await ctx.send("user_id tidak ditemukan di database")
                else: 
                    current_rcash = data["rcash"]  
                    if amount == 0:
                        await ctx.send("mau ngisi apa bang?")
                    elif amount < 0:
                        await ctx.send("bodoh negatif")
                    elif len(str(amount)) > 20:
                        await ctx.send("jangan banyak banyak bang entar infasi")
                    else: 
                        new_rcash = current_rcash + amount
                        cursor.execute("""UPDATE users
                        SET rcash = %s
                        WHERE discord_id = %s
                        """, (new_rcash, user_id))

                        db.commit()

                        await ctx.send(f"Berhasil menambahkan rcash di user_id = {user_id} total rcash = {new_rcash}")
            else:
               return None
        else: 
            return None
        
    @commands.command()
    async def addlevel(self, ctx, user_id: int, level: int):
        if ctx.channel.id == PRIVATE_CHANNEL: 
            if ctx.author.id == OWNER_USERID or ctx.author.id == self.bot.owner_id:
                cursor.execute("SELECT level FROM users WHERE discord_id=%s", (user_id, ))
                data = cursor.fetchone()

                if data is None: 
                    await ctx.send("user_id tidak ditemukan di database")
                else: 
                    current_level = data["level"]  
                    if level == 0:
                        await ctx.send("mau ngisi apa bang?")
                    else: 
                        new_level = current_level + level
                        cursor.execute("""UPDATE users
                        SET level = %s
                        WHERE discord_id = %s
                        """, (new_level, user_id))

                        db.commit()

                        await ctx.send(f"Berhasil menambahkan level di user_id = {user_id} total level = {new_level}")
            else:
               return None
        else: 
            return None
        
    @addrcash.error
    @addlevel.error
    async def normal_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return 
        else:
            await ctx.send(f"Terjadi kesalahan: {error}")