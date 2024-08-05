import os
import discord
import sys
import random

from discord import app_commands
from dotenv import load_dotenv
from discord.ext import commands
from colorama import Fore, Style, init

from func.save_data import save_user_data
from func.maintance import MaintenanceView
from func.database import db, cursor

from bot_cmd.status import StatusCog
from bot_cmd.set_data import SetCog

init()
load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
GUILD = discord.Object(0)
OWNER_USERID = 676722563681878016
PRIVATE_CHANNEL = 1268491225883873351

bot = commands.Bot(command_prefix='/', intents=intents)

async def setup(bot):
    print("Setting up cogs...")
    await bot.add_cog(StatusCog(bot))
    await bot.add_cog(SetCog(bot))
    print("Selesai setting cogs...")

@bot.event
async def on_ready():
    print(f"{Fore.GREEN}Berhasil menjalankan bot!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Bot telah login sebagai {bot.user.name}#{bot.user.discriminator}{Style.RESET_ALL}")
    await setup(bot)

@bot.event
async def on_message(message):
    if message.author == bot.user: 
        return
    user_id = message.author.id
    username = str(message.author)
    cursor.execute('SELECT * FROM users WHERE discord_id=%s', (user_id,))
    user = cursor.fetchone()
    if user is None: 
        await save_user_data(user_id, username)
    await bot.process_commands(message) 

@bot.command()
async def maintance(ctx, rcon: int):
    await ctx.message.delete()
    if rcon == 234234: 
        if ctx.author.id == OWNER_USERID or ctx.author.id == bot.owner_id:
            view = MaintenanceView(bot)
            await ctx.send("Pilih aksi pemeliharaan yang diinginkan:", view=view)
        else:
            await ctx.send("Anda tidak memiliki izin untuk melakukan pemeliharaan.", ephemeral=True)

@maintance.error
async def normal_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        return 
    else:
        await ctx.send(f"Terjadi kesalahan: {error}")

def main():
    bot_token = os.getenv("BOT_TOKEN")
    
    if not bot_token:
        print(f"{Fore.RED}Error: BOT_TOKEN tidak ditemukan dalam variabel lingkungan.{Style.RESET_ALL}")
        sys.exit(1)

    print(f"{Fore.GREEN}Mencoba menjalankan bot...{Style.RESET_ALL}")
    try:
        bot.run(bot_token)
    except Exception as e:
        print(f"{Fore.RED}Terjadi kesalahan saat menjalankan bot: {e}{Style.RESET_ALL}")
        sys.exit(1)

""" 
    Casino Games
"""
color = 0xC8102E 
suits = ['♠', '♥', '♦', '♣']
values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
card_values = {value: min(index + 2, 10) for index, value in enumerate(values[:-1])}  # Value 2-10
card_values.update({'J': 10, 'Q': 10, 'K': 10, 'A': 11})

def create_deck():
    """Create a new deck of cards."""
    deck = [f"{value}{suit}" for suit in suits for value in values]
    return deck

def hand_value(hand):
    """Calculate the value of a hand."""
    value = sum(card_values[card[:-1]] for card in hand)
    num_aces = sum(card.endswith('A') for card in hand)
    while value > 21 and num_aces:
        value -= 10
        num_aces -= 1
    return value

def draw_card(deck):
    """Draw a card from the deck."""
    return deck.pop(random.randint(0, len(deck) - 1))

def build_embed(player_hand, dealer_hand, player_value, dealer_value, is_reveal=False):
    embed = discord.Embed(title="Blackjack 🎲", description="**Bermain Blackjack di sini!**", color=color)
    
    player_cards = ' '.join(player_hand)
    dealer_cards = ' '.join(dealer_hand)
    
    embed.add_field(
        name="🃏 Kartu Pemain",
        value=f"{player_cards}\n**Nilai:** {player_value}",
        inline=False
    )
    
    if is_reveal:
        embed.add_field(
            name="🤵 Kartu Dealer",
            value=f"{dealer_cards}\n**Nilai:** {dealer_value}",
            inline=False
        )
    else:
        dealer_first_card = dealer_hand[0]
        embed.add_field(
            name="🤵 Kartu Dealer",
            value=f"{dealer_first_card} ❓\n**Nilai:** {card_values[dealer_first_card[:-1]]}",
            inline=False
        )
    
    return embed

@bot.command(aliases=["bj"])
async def blackjack(ctx, bet: int):
    if bet == 0:
        await ctx.send("Masukan taruhan rcash anda! /bj <taruhan>")
    elif bet > 999: 
        await ctx.send("Maksimal bet 999 rcash, tidak boleh lebih!")
    elif bet < 0: 
        await ctx.send("Kamu mau taruhan mines? masukan /bj <taruhan>.")
    else:
        user_id = ctx.author.id

        cursor.execute("""
            SELECT rcash, level FROM users WHERE discord_id=%s
        """, (user_id, ))
        result = cursor.fetchone()
        rcash = result["rcash"]
        win_level = result["level"] + 1

        if rcash < bet: 
            await ctx.send(f"hei rcash anda tidak mencukupi, saldo rcash anda {rcash}")
        else: 
            new_rcash = rcash - bet
            cursor.execute("UPDATE users SET rcash = %s WHERE discord_id=%s", (new_rcash, user_id))
            db.commit()

            deck = create_deck()
            random.shuffle(deck)
            player_hand = [draw_card(deck), draw_card(deck)]
            dealer_hand = [draw_card(deck), draw_card(deck)]

            def get_hand_value(hand):
                return hand_value(hand)

            player_value = get_hand_value(player_hand)
            dealer_value = get_hand_value(dealer_hand)

            embed = build_embed(player_hand, dealer_hand, player_value, dealer_value)
            message = await ctx.send(embed=embed)
            await message.add_reaction('🃏')  # Hit
            await message.add_reaction('🛑')  # Stand

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ['🃏', '🛑']

            while player_value < 21:
                try:
                    reaction, _ = await bot.wait_for('reaction_add', timeout=60.0, check=check)
                except TimeoutError:
                    await ctx.send("⏳ Waktu habis rcash anda tidak dikembalikan!")
                    return

                if str(reaction.emoji) == '🃏':
                    player_hand.append(draw_card(deck))
                    player_value = get_hand_value(player_hand)
                    embed = build_embed(player_hand, dealer_hand, player_value, dealer_value)
                    await message.edit(embed=embed)
                    if player_value > 21:
                        await ctx.send(f"😔 Kamu kalah! Nilai tanganmu melebihi 21, uang anda berkurang -{bet}.")
                        return
                elif str(reaction.emoji) == '🛑':
                    break

            while dealer_value < 18:
                dealer_hand.append(draw_card(deck))
                dealer_value = get_hand_value(dealer_hand)

            embed = build_embed(player_hand, dealer_hand, player_value, dealer_value, is_reveal=True)
            await message.edit(embed=embed)

            if player_value > 21:
                await ctx.send(f"😔 Kamu kalah! Nilai tanganmu melebihi 21, rcash anda berkurang -{bet}.")
            elif dealer_value > 21 or player_value > dealer_value:
                win_rcash = bet * 2
                result_win = rcash + win_rcash
                cursor.execute("UPDATE users SET rcash = %s, level = %s WHERE discord_id=%s", (result_win, win_level, user_id))
                db.commit()
                await ctx.send(f"🏆 Selamat! Kamu menang! rcash anda bertambah {win_rcash}")
            elif player_value < dealer_value:
                await ctx.send(f"😔 Sayang sekali, kamu kalah, rcash anda berkurang -{bet}.")
            else:
                cursor.execute("UPDATE users SET rcash = %s WHERE discord_id=%s", (rcash, user_id))
                db.commit()
                await ctx.send("🎉 Seri!")

@blackjack.error
async def on_command_error(ctx, error):
   if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send(f"Masukan taruhan rcash anda, /bj <taruhan>")
   else:
        raise error

""" Dice """
def roll_dice():
    """Roll a dice and return the result."""
    return random.randint(1, 6)

def create_dice_embed(player_roll, result_message, color=color):
    """Create a modern embed for the dice game."""
    embed = discord.Embed(title="Dice 🍀", description="**Ayo main game dadu!**", color=color)
    
    embed.add_field(
        name="🎲 Hasil Guliran",
        value=f"**Kamu mendapatkan:** {player_roll}",
        inline=False
    )
    
    embed.add_field(
        name="🔮 Hasil",
        value=result_message,
        inline=False
    )
    
    return embed

@bot.command()
async def dice(ctx, bet: int):
    user_id = ctx.author.id

    if bet == 0:
        await ctx.send("Masukan taruhan rcash anda! /dice <taruhan>")
    elif bet > 999: 
        await ctx.send("Maksimal bet 999 rcash, tidak boleh lebih!")
    elif bet < 0: 
        await ctx.send("Kamu mau taruhan mines? masukan /dice <taruhan>.")
    else:       
        cursor.execute("SELECT rcash, level FROM users WHERE discord_id=%s", (user_id, ))
        result = cursor.fetchone()
        rcash = result["rcash"]
        level = result["level"]

        new_rcash = rcash - bet
        cursor.execute("UPDATE users SET rcash = %s WHERE discord_id=%s", (new_rcash, user_id))
        db.commit()

        if rcash < bet: 
            await ctx.send("Rcash anda tidak mencukupi")
        else: 
            """Command to roll the dice."""
            player_roll = roll_dice()
            result_message = ""
            
            if player_roll == 6:
                win_level = level + 1
                wbet = bet * 2
                win_rcash =  new_rcash + wbet + 50
                cursor.execute("UPDATE users SET rcash = %s, level = %s WHERE discord_id=%s", (win_rcash, win_level, user_id))
                db.commit()
                result_message = f"✨ Kamu mendapatkan hasil terbaik! Selamat! 🎉 +{wbet}"
            elif player_roll >= 4:
                win_level = level + 1
                wbet = bet * 2
                win_rcash =  new_rcash + wbet 
                cursor.execute("UPDATE users SET rcash = %s, level = %s WHERE discord_id=%s", (win_rcash, win_level, user_id))
                db.commit()
                result_message = f"👍 Bagus! Hasil yang solid +{wbet}."
            else:
                result_message = f"😅 Kurang beruntung. Coba lagi! -{bet}"
            
            embed = create_dice_embed(player_roll, result_message)
            await ctx.send(embed=embed)

@dice.error
async def dice_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("/dice <taruhan anda>")
    else: 
        print(error)


# """ Slot """
# symbols = ['🍒', '🍋', '🍉', '🍇', '🔔', '⭐']  # Tambahkan lebih banyak simbol sesuai kebutuhan

# # Probabilitas untuk setiap simbol
# symbol_weights = {
#     '🍒': 5,  # Simbol umum
#     '🍋': 5,
#     '🍉': 3,  # Simbol yang jarang muncul
#     '🍇': 3,
#     '🔔': 2,  # Simbol dengan hadiah tinggi
#     '⭐': 1    # Simbol dengan hadiah terbesar
# }

# def spin_slot():
#     """Simulasikan putaran slot machine."""
#     return [random.choices(list(symbol_weights.keys()), weights=symbol_weights.values())[0] for _ in range(3)]

# def calculate_winnings(result):
#     """Hitung kemenangan berdasarkan hasil putaran."""
#     winnings = 0
#     if len(set(result)) == 1:  # Semua simbol sama
#         if result[0] == '⭐':
#             winnings = 1000  # Hadiah terbesar
#         elif result[0] == '🔔':
#             winnings = 500
#         else:
#             winnings = 100
#     return winnings

# @bot.command()
# async def slot(ctx):
#     result = spin_slot()
#     winnings = calculate_winnings(result)
#     embed = discord.Embed(title="Slot Machine 🎰", description="**Selamat datang di Slot Machine!**", color=color)
#     embed.add_field(
#         name="🎰 Hasil Putaran",
#         value=' | '.join(result),
#         inline=False
#     )
#     if winnings > 0:
#         embed.add_field(
#             name="🏆 Kemenangan",
#             value=f"Kamu menang {winnings} poin!",
#             inline=False
#         )
#     else:
#         embed.add_field(
#             name="😔 Kalah",
#             value="Sayang sekali, kamu belum menang.",
#             inline=False
#         )
#     await ctx.send(embed=embed)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        bot.close()
        sys.exit(0)
