import os
import sys

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
import json
import random
from datetime import datetime

load_dotenv()

intents = nextcord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "economy": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@bot.event
async def on_ready():
    print(f'Ready: {bot.user}')
    await bot.change_presence(activity=nextcord.Game(name="/help"))

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    data = load_data()
    user_id = str(message.author.id)
    
    if user_id not in data["users"]:
        data["users"][user_id] = {"xp": 0, "level": 1}
        data["economy"][user_id] = {"money": 0, "last_daily": None}
    
    data["users"][user_id]["xp"] += random.randint(1, 3)
    xp = data["users"][user_id]["xp"]
    level = data["users"][user_id]["level"]
    
    if xp >= level * 100:
        data["users"][user_id]["level"] += 1
        data["users"][user_id]["xp"] = 0
        try:
            await message.author.send(f"Поздравляю! Ты достиг уровня {level + 1}!")
        except:
            pass
    
    save_data(data)
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    data = load_data()
    data["users"][str(member.id)] = {"xp": 0, "level": 1}
    data["economy"][str(member.id)] = {"money": 0, "last_daily": None}
    save_data(data)
    
    channel = nextcord.utils.get(member.guild.text_channels, name="general")
    if channel:
        embed = nextcord.Embed(title="Добро пожаловать!", color=0x00ff00)
        embed.description = f"{member.mention} присоединился к серверу!"
        await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    channel = nextcord.utils.get(member.guild.text_channels, name="general")
    if channel:
        embed = nextcord.Embed(title="Участник ушел", color=0xff0000)
        embed.description = f"{member.name} покинул сервер"
        await channel.send(embed=embed)

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency*1000)}ms")

@bot.command(name="test")
async def test(ctx):
    await ctx.send("Test OK!")

@bot.command(name="profile")
async def profile(ctx, member: nextcord.Member = None):
    member = member or ctx.author
    data = load_data()
    user_id = str(member.id)
    
    if user_id not in data["users"]:
        data["users"][user_id] = {"xp": 0, "level": 1}
        data["economy"][user_id] = {"money": 0, "last_daily": None}
    
    xp = data["users"][user_id]["xp"]
    level = data["users"][user_id]["level"]
    money = data["economy"][user_id]["money"]
    
    embed = nextcord.Embed(title=f"Профиль: {member.name}", color=member.color)
    embed.set_thumbnail(member.display_avatar.url)
    embed.add_field(name="Уровень", value=str(level), inline=True)
    embed.add_field(name="XP", value=f"{xp}/{level*100}", inline=True)
    embed.add_field(name="Монеты", value=str(money), inline=True)
    await ctx.send(embed=embed)

@bot.command(name="top")
async def top(ctx):
    data = load_data()
    users = sorted(data["users"].items(), key=lambda x: x[1]["level"], reverse=True)[:10]
    
    embed = nextcord.Embed(title="Топ игроков", color=0xffd700)
    for i, (uid, stats) in enumerate(users, 1):
        user = bot.get_user(int(uid))
        if user:
            embed.add_field(name=f"{i}. {user.name}", value=f"Уровень: {stats['level']} | XP: {stats['xp']}", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name="daily")
async def daily(ctx):
    data = load_data()
    user_id = str(ctx.author.id)
    
    if user_id not in data["economy"]:
        data["economy"][user_id] = {"money": 0, "last_daily": None}
    
    last_daily = data["economy"][user_id].get("last_daily")
    today = datetime.now().date().isoformat()
    
    if last_daily == today:
        await ctx.send("Ты уже получил ежедневную награду сегодня! Возвращайся завтра.")
        return
    
    reward = random.randint(50, 200)
    data["economy"][user_id]["money"] += reward
    data["economy"][user_id]["last_daily"] = today
    save_data(data)
    
    await ctx.send(f"Ты получил {reward} монет!")

@bot.command(name="balance")
async def balance(ctx, member: nextcord.Member = None):
    member = member or ctx.author
    data = load_data()
    money = data["economy"].get(str(member.id), {}).get("money", 0)
    await ctx.send(f"Баланс {member.name}: {money} монет")

@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: nextcord.Member, *, reason=None):
    await member.kick(reason=reason)
    embed = nextcord.Embed(title="Кик", color=0xff0000)
    embed.description = f"{member.name} кикнут"
    if reason:
        embed.add_field(name="Причина", value=reason)
    await ctx.send(embed=embed)

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: nextcord.Member, *, reason=None):
    await member.ban(reason=reason)
    embed = nextcord.Embed(title="Бан", color=0xff0000)
    embed.description = f"{member.name} забанен"
    if reason:
        embed.add_field(name="Причина", value=reason)
    await ctx.send(embed=embed)

@bot.command(name="mute")
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: nextcord.Member, duration: int = 60):
    role = nextcord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
        role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(role, send_messages=False)
    
    await member.add_roles(role)
    await ctx.send(f"{member.name} замьючен на {duration} минут")

@bot.command(name="unmute")
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: nextcord.Member):
    role = nextcord.utils.get(ctx.guild.roles, name="Muted")
    if role:
        await member.remove_roles(role)
        await ctx.send(f"{member.name} размьючен")

@bot.command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"Удалено {amount} сообщений", delete_after=3)

@bot.command(name="meme")
async def meme(ctx):
    memes = [
        "https://i.imgflip.com/1bij.jpg",
        "https://i.imgflip.com/1ur9b0.jpg", 
        "https://i.imgflip.com/261o3j.jpg",
        "https://i.imgflip.com/30b1gx.jpg",
        "https://i.imgflip.com/1g8my4.jpg"
    ]
    embed = nextcord.Embed()
    embed.set_image(url=random.choice(memes))
    await ctx.send(embed=embed)

@bot.command(name="cat")
async def cat(ctx):
    cats = [
        "https://cataas.com/cat",
        "http://placekitten.com/200/200",
        "https://cataas.com/cat?width=300"
    ]
    await ctx.send(random.choice(cats))

@bot.command(name="dog")
async def dog(ctx):
    await ctx.send("https://dog.ceo/api/breeds/image/random")

@bot.command(name="8ball")
async def eightball(ctx, *, question=None):
    if not question:
        await ctx.send("Задай вопрос!")
        return
    
    answers = [
        "Да!", "Нет", "Возможно", "Скорее всего да", "Скорее всего нет",
        "Определённо", "Не знаю", "Звезды говорят - да", "Звезды говорят - нет"
    ]
    await ctx.send(f"🎱 {random.choice(answers)}")

@bot.command(name="roll")
async def roll(ctx, sides: int = 6):
    result = random.randint(1, sides)
    await ctx.send(f"🎲 Выпало: {result} (из {sides})")

@bot.command(name="say")
@commands.has_permissions(manage_messages=True)
async def say(ctx, *, text):
    await ctx.send(text)
    await ctx.message.delete()

@bot.command(name="help")
async def help_cmd(ctx):
    embed = nextcord.Embed(title="Команды бота", color=0x00ff00)
    embed.add_field(name="🎮 Основные", value="`!ping` - пинг\n`!test` - тест\n`!8ball <вопрос>` - предсказание", inline=False)
    embed.add_field(name="📊 Уровни", value="`!profile [user]` - профиль\n`!top` - топ игроков\n`!balance [user]` - баланс\n`!daily` - ежедневные монеты", inline=False)
    embed.add_field(name="🛠️ Модерация", value="`!kick <user>` - кик\n`!ban <user>` - бан\n`!mute <user>` - мьют\n`!unmute <user>` - размьют\n`!clear <кол-во>` - очистка", inline=False)
    embed.add_field(name="🎲 Развлечения", value="`!meme` - случайный мем\n`!cat` - кот\n`!dog` - пес\n`!roll <кол-во>` - кубик", inline=False)
    await ctx.send(embed=embed)

if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_TOKEN'))
