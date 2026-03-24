import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8') if sys.platform == "win32" else None

import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
import json
import random
from datetime import datetime, timedelta
from collections import defaultdict

load_dotenv()

intents = nextcord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "economy": {}, "achievements": {}, "streaks": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

ACHIEVEMENTS = {
    "first_message": {"name": "Первое сообщение", "desc": "Написал первое сообщение", "reward": 10},
    "first_daily": {"name": "Первые шаги", "desc": "Получил первую ежедневную награду", "reward": 20},
    "level_5": {"name": "Новичок", "desc": "Достиг 5 уровня", "reward": 50},
    "level_10": {"name": "Опытный", "desc": "Достиг 10 уровня", "reward": 100},
    "level_25": {"name": "Профессионал", "desc": "Достиг 25 уровня", "reward": 250},
    "streak_7": {"name": "Постоянец", "desc": "7 дней подряд получал награду", "reward": 100},
    "streak_30": {"name": "Преданный", "desc": "30 дней подряд получал награду", "reward": 500},
    "rich": {"name": "Богач", "desc": "Накопил 1000 монет", "reward": 100},
    "gambler": {"name": "Игрок", "desc": "Сыграл 10 раз в казино", "reward": 50},
    "big_winner": {"name": "Крупный выигрыш", "desc": "Выиграл 500+ монет за раз", "reward": 150}
}

QUOTES = [
    "Счастье не в том, чтобы делать то, что хочешь, а в том, чтобы хотеть то, что делаешь.",
    "Единственный способ делать великие дела — любить то, что делаешь.",
    "Успех — это не final, failure — не fatal: надо иметь мужество продолжать.",
    "Человек, который не рискует, не может ни построить, ни разрушить.",
    "Все великие дела начинались с решения попробовать.",
    "Лучшее время посадить дерево было 20 лет назад. Второе лучшее — сейчас.",
    "Не жди идеального момента — бери момент и делай его идеальным.",
    "Трудности — это часть пути. Преодолевай их, и ты станешь сильнее.",
    "Мечты без действий — просто мечты. Действия без мечт — скучная рутина.",
    "Тот, кто говорит 'невозможно', не должен мешать тем, кто делает."
]

JOKES = [
    "Почему программист ушёл с работы? Потому что он не получил массив (array).",
    "В чем разница между PHP и Java? PHP — это как русский язык: сложный, но все говорят. Java — как английский: все учат, но не все понимают.",
    "— Где ты работаешь?\n— В Google.\n— Какое отделение?\n— Они ещё не поняли.",
    "— Как называют программиста, который не спит?\n— Caffeine-dependent entity.",
    "Семь раз отмерь, один раз накодируй, семь раз отладь, один раз плачь.",
    "В IT говорят 'у меня всё работает' — это как в медицине 'вскрытие показало'.",
    "— У меня баг!\n— А может это фича?\n— Нет, баг.\n— Тогда точно фича.",
    "Почему Python хороший язык? Потому что он понятный. А почему JavaScript плохой? Потому что он JavaScript.",
    "Программист — это человек, который решает проблему, о существовании которой ты не знал, способом, который ты не понимаешь.",
    "— Сколько программистов нужно, чтобы поменять лампочку?\n— Ни одного, это hardware проблема."
]

@bot.event
async def on_ready():
    print(f'Ready: {bot.user}')
    await bot.change_presence(activity=nextcord.Game(name="/help | !help"))

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    data = load_data()
    user_id = str(message.author.id)
    
    if user_id not in data["users"]:
        data["users"][user_id] = {"xp": 0, "level": 1}
        data["economy"][user_id] = {"money": 0, "last_daily": None}
        data["achievements"][user_id] = []
        data["streaks"][user_id] = {"days": 0, "last_claim": None}
    
    if "first_message" not in data["achievements"].get(user_id, []):
        data["achievements"][user_id].append("first_message")
        data["economy"][user_id]["money"] += ACHIEVEMENTS["first_message"]["reward"]
        await message.author.send(f"🏆 Достижение получено: '{ACHIEVEMENTS['first_message']['name']}'! +{ACHIEVEMENTS['first_message']['reward']} монет")
    
    data["users"][user_id]["xp"] += random.randint(1, 3)
    xp = data["users"][user_id]["xp"]
    level = data["users"][user_id]["level"]
    
    if xp >= level * 100:
        data["users"][user_id]["level"] += 1
        data["users"][user_id]["xp"] = 0
        
        if level == 4 and "level_5" not in data["achievements"].get(user_id, []):
            data["achievements"][user_id].append("level_5")
            data["economy"][user_id]["money"] += ACHIEVEMENTS["level_5"]["reward"]
            await message.author.send(f"🏆 Достижение: '{ACHIEVEMENTS['level_5']['name']}'! +{ACHIEVEMENTS['level_5']['reward']} монет")
        elif level == 9 and "level_10" not in data["achievements"].get(user_id, []):
            data["achievements"][user_id].append("level_10")
            data["economy"][user_id]["money"] += ACHIEVEMENTS["level_10"]["reward"]
            await message.author.send(f"🏆 Достижение: '{ACHIEVEMENTS['level_10']['name']}'! +{ACHIEVEMENTS['level_10']['reward']} монет")
        elif level == 24 and "level_25" not in data["achievements"].get(user_id, []):
            data["achievements"][user_id].append("level_25")
            data["economy"][user_id]["money"] += ACHIEVEMENTS["level_25"]["reward"]
            await message.author.send(f"🏆 Достижение: '{ACHIEVEMENTS['level_25']['name']}'! +{ACHIEVEMENTS['level_25']['reward']} монет")
        else:
            try:
                await message.author.send(f"🎉 Поздравляю! Ты достиг уровня {level + 1}!")
            except:
                pass
    
    save_data(data)
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    data = load_data()
    data["users"][str(member.id)] = {"xp": 0, "level": 1}
    data["economy"][str(member.id)] = {"money": 0, "last_daily": None}
    data["achievements"][str(member.id)] = []
    data["streaks"][str(member.id)] = {"days": 0, "last_claim": None}
    save_data(data)
    
    channel = nextcord.utils.get(member.guild.text_channels, name="general")
    if channel:
        embed = nextcord.Embed(title="👋 Добро пожаловать!", color=0x00ff00)
        embed.description = f"{member.mention} присоединился к серверу!\n\nНапиши !help чтобы увидеть все команды."
        embed.set_thumbnail(member.display_avatar.url)
        await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    channel = nextcord.utils.get(member.guild.text_channels, name="general")
    if channel:
        embed = nextcord.Embed(title="😢 Участник ушел", color=0xff0000)
        embed.description = f"{member.name} покинул сервер"
        await channel.send(embed=embed)

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"🏓 Pong! `{round(bot.latency*1000)}ms`")

@bot.command(name="profile")
async def profile(ctx, member: nextcord.Member = None):
    member = member or ctx.author
    data = load_data()
    user_id = str(member.id)
    
    if user_id not in data["users"]:
        data["users"][user_id] = {"xp": 0, "level": 1}
        data["economy"][user_id] = {"money": 0, "last_daily": None}
        data["achievements"][user_id] = []
        data["streaks"][user_id] = {"days": 0, "last_claim": None}
    
    xp = data["users"][user_id]["xp"]
    level = data["users"][user_id]["level"]
    money = data["economy"][user_id]["money"]
    achievements = len(data["achievements"].get(user_id, []))
    streak = data["streaks"].get(user_id, {}).get("days", 0)
    
    embed = nextcord.Embed(title=f"📊 Профиль: {member.name}", color=member.color)
    embed.set_thumbnail(member.display_avatar.url)
    embed.add_field(name="⭐ Уровень", value=str(level), inline=True)
    embed.add_field(name="💫 XP", value=f"{xp}/{level*100}", inline=True)
    embed.add_field(name="💰 Монеты", value=str(money), inline=True)
    embed.add_field(name="🔥 Streak", value=f"{streak} дней", inline=True)
    embed.add_field(name="🏆 Достижения", value=str(achievements), inline=True)
    embed.add_field(name="📅 Присоединился", value=member.joined_at.strftime("%d.%m.%Y"), inline=True)
    await ctx.send(embed=embed)

@bot.command(name="top")
async def top(ctx):
    data = load_data()
    users = sorted(data["users"].items(), key=lambda x: (x[1]["level"], x[1]["xp"]), reverse=True)[:10]
    
    embed = nextcord.Embed(title="🏆 Топ игроков", color=0xffd700)
    medals = ["🥇", "🥈", "🥉"]
    for i, (uid, stats) in enumerate(users, 1):
        user = bot.get_user(int(uid))
        if user:
            medal = medals[i-1] if i <= 3 else f"{i}."
            embed.add_field(name=f"{medal} {user.name}", value=f"⭐{stats['level']} | 💰{data['economy'].get(uid, {}).get('money', 0)}", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name="daily")
async def daily(ctx):
    data = load_data()
    user_id = str(ctx.author.id)
    
    if user_id not in data["economy"]:
        data["economy"][user_id] = {"money": 0, "last_daily": None}
    if user_id not in data["streaks"]:
        data["streaks"][user_id] = {"days": 0, "last_claim": None}
    
    last_daily = data["economy"][user_id].get("last_daily")
    today = datetime.now().date().isoformat()
    yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
    
    if last_daily == today:
        embed = nextcord.Embed(title="⏰ Подожди", color=0xffaa00)
        embed.description = "Ты уже получил ежедневную награду сегодня!\nВозвращайся завтра."
        await ctx.send(embed=embed)
        return
    
    streak = data["streaks"][user_id]["days"]
    if last_daily == yesterday:
        streak += 1
        data["streaks"][user_id]["days"] = streak
        
        if streak == 6 and "streak_7" not in data["achievements"].get(user_id, []):
            data["achievements"][user_id].append("streak_7")
            data["economy"][user_id]["money"] += ACHIEVEMENTS["streak_7"]["reward"]
            await ctx.send(f"🏆 Достижение: '{ACHIEVEMENTS['streak_7']['name']}'! +{ACHIEVEMENTS['streak_7']['reward']} монет")
        elif streak == 29 and "streak_30" not in data["achievements"].get(user_id, []):
            data["achievements"][user_id].append("streak_30")
            data["economy"][user_id]["money"] += ACHIEVEMENTS["streak_30"]["reward"]
            await ctx.send(f"🏆 Достижение: '{ACHIEVEMENTS['streak_30']['name']}'! +{ACHIEVEMENTS['streak_30']['reward']} монет")
    else:
        streak = 1
        data["streaks"][user_id]["days"] = streak
    
    base_reward = random.randint(50, 200)
    streak_bonus = min(streak * 10, 100)
    total_reward = base_reward + streak_bonus
    
    if "first_daily" not in data["achievements"].get(user_id, []):
        data["achievements"][user_id].append("first_daily")
        data["economy"][user_id]["money"] += ACHIEVEMENTS["first_daily"]["reward"]
        await ctx.send(f"🏆 Первое достижение: '{ACHIEVEMENTS['first_daily']['name']}'! +{ACHIEVEMENTS['first_daily']['reward']} монет")
    
    data["economy"][user_id]["money"] += total_reward
    data["economy"][user_id]["last_daily"] = today
    save_data(data)
    
    embed = nextcord.Embed(title="✅ Ежедневная награда получена!", color=0x00ff00)
    embed.add_field(name="Базовое вознаграждение", value=f"+{base_reward} 💰", inline=True)
    embed.add_field(name="Бонус за streak", value=f"+{streak_bonus} 💰", inline=True)
    embed.add_field(name="Всего", value=f"+{total_reward} 💰", inline=True)
    embed.add_field(name="Streak", value=f"🔥 {streak} дней", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="balance")
async def balance(ctx, member: nextcord.Member = None):
    member = member or ctx.author
    data = load_data()
    money = data["economy"].get(str(member.id), {}).get("money", 0)
    embed = nextcord.Embed(title=f"💰 Баланс: {member.name}", color=0xffd700)
    embed.add_field(name="Монет", value=str(money), inline=False)
    await ctx.send(embed=embed)

@bot.command(name="achievements")
async def achievements(ctx, member: nextcord.Member = None):
    member = member or ctx.author
    data = load_data()
    user_id = str(member.id)
    user_achievements = data["achievements"].get(user_id, [])
    
    embed = nextcord.Embed(title=f"🏆 Достижения: {member.name}", color=0x00ff00)
    
    unlocked = []
    locked = []
    for ach_id, ach_data in ACHIEVEMENTS.items():
        if ach_id in user_achievements:
            unlocked.append(f"✅ **{ach_data['name']}** - {ach_data['desc']} (+{ach_data['reward']}💰)")
        else:
            locked.append(f"❌ **{ach_data['name']}**")
    
    if unlocked:
        embed.add_field(name="Полученные", value="\n".join(unlocked[:10]), inline=False)
    if locked:
        embed.add_field(name="Не полученные", value="\n".join(locked[:10]), inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name="casino")
async def casino(ctx, bet: int = None):
    if bet is None:
        await ctx.send("Usage: `!casino <ставка>`")
        return
    
    data = load_data()
    user_id = str(ctx.author.id)
    money = data["economy"].get(user_id, {}).get("money", 0)
    
    if bet > money:
        await ctx.send(f"Недостаточно монет! У тебя: {money}💰")
        return
    if bet < 10:
        await ctx.send("Минимальная ставка: 10 монет")
        return
    
    data["economy"][user_id]["money"] -= bet
    
    result = random.randint(1, 100)
    wins = 0
    for _ in range(3):
        if random.randint(1, 100) <= result:
            wins += 1
    
    if wins >= 2:
        multiplier = wins
        win_amount = bet * multiplier
        data["economy"][user_id]["money"] += win_amount
        
        if win_amount >= 500 and "big_winner" not in data["achievements"].get(user_id, []):
            data["achievements"][user_id].append("big_winner")
            data["economy"][user_id]["money"] += ACHIEVEMENTS["big_winner"]["reward"]
            await ctx.send(f"🏆 Достижение: '{ACHIEVEMENTS['big_winner']['name']}'! +{ACHIEVEMENTS['big_winner']['reward']} монет")
        
        embed = nextcord.Embed(title="🎰 Казино - ПОБЕДА!", color=0x00ff00)
        embed.add_field(name="Выпавшие", value="🍒 " * wins + "💨 " * (3 - wins), inline=False)
        embed.add_field(name="Множитель", value=f"x{multiplier}", inline=True)
        embed.add_field(name="Выигрыш", value=f"+{win_amount}💰", inline=True)
    else:
        embed = nextcord.Embed(title="🎰 Казино - ПРОИГРЫШ", color=0xff0000)
        embed.add_field(name="Выпавшие", value="🍒 " * wins + "💨 " * (3 - wins), inline=False)
        embed.add_field(name="Проигрыш", value=f"-{bet}💰", inline=False)
    
    if "gambler" not in data["achievements"].get(user_id, []):
        plays = data["economy"][user_id].get("casino_plays", 0) + 1
        data["economy"][user_id]["casino_plays"] = plays
        if plays >= 10:
            data["achievements"][user_id].append("gambler")
            data["economy"][user_id]["money"] += ACHIEVEMENTS["gambler"]["reward"]
            await ctx.send(f"🏆 Достижение: '{ACHIEVEMENTS['gambler']['name']}'! +{ACHIEVEMENTS['gambler']['reward']} монет")
    
    if data["economy"].get(user_id, {}).get("money", 0) >= 1000 and "rich" not in data["achievements"].get(user_id, []):
        data["achievements"][user_id].append("rich")
        data["economy"][user_id]["money"] += ACHIEVEMENTS["rich"]["reward"]
        await ctx.send(f"🏆 Достижение: '{ACHIEVEMENTS['rich']['name']}'! +{ACHIEVEMENTS['rich']['reward']} монет")
    
    save_data(data)
    await ctx.send(embed=embed)

@bot.command(name="quote")
async def quote(ctx):
    await ctx.send(f"💬 **{random.choice(QUOTES)}**")

@bot.command(name="joke")
async def joke(ctx):
    await ctx.send(f"😂 {random.choice(JOKES)}")

@bot.command(name="rps")
async def rps(ctx, choice: str = None):
    if choice not in ["r", "rock", "p", "paper", "s", "scissors"]:
        await ctx.send("Usage: `!rps <rock/paper/scissors>` или `!rps <r/p/s>`")
        return
    
    choices = {"r": "Камень", "p": "Бумага", "s": "Ножницы"}
    bot_choice = random.choice(["r", "p", "s"])
    
    user_idx = ["r", "p", "s"].index(choice[0])
    bot_idx = ["r", "p", "s"].index(bot_choice)
    
    result = (user_idx - bot_idx) % 3
    if result == 0:
        msg = "Ничья! 🤝"
    elif result == 1:
        msg = "Ты победил! 🎉"
    else:
        msg = "Бот победил! 🤖"
    
    await ctx.send(f"Ты: {choices[choice[0]]} vs Бот: {choices[bot_choice]}\n{msg}")

@bot.command(name="hack")
async def hack(ctx, member: nextcord.Member = None):
    if not member:
        await ctx.send("Usage: `!hack <@user>`")
        return
    
    hack_msgs = [
        "Взлом Instagram...",
        "Получение доступа к банковскому счету...",
        "Удаление вирусов...",
        "Перевод биткоинов...",
        "Хакерский дроппер..."
    ]
    
    msg = await ctx.send(f"🔨 Начинаю взлом {member.name}...")
    for h in hack_msgs:
        await msg.edit(content=f"🔨 {h}")
        await asyncio.sleep(0.5)
    
    hack_result = random.choice([
        f"Успешно! Взломано 0 монет и {random.randint(1, 100)} XP",
        f"Неудача! Атака отбита антивирусом",
        f"Успешно! Получены данные: `{random.randint(1000, 9999)}`",
        f"Ошибка! Слишком много Firewall",
    ])
    await msg.edit(content=f"🔨 {hack_result}")

@bot.command(name="meme")
async def meme(ctx):
    memes = [
        "https://i.imgflip.com/1bij.jpg",
        "https://i.imgflip.com/1ur9b0.jpg", 
        "https://i.imgflip.com/261o3j.jpg",
        "https://i.imgflip.com/30b1gx.jpg",
        "https://i.imgflip.com/1g8my4.jpg",
        "https://i.imgflip.com/1otk96.jpg",
        "https://i.imgflip.com/43a45p.jpg"
    ]
    embed = nextcord.Embed()
    embed.set_image(url=random.choice(memes))
    await ctx.send(embed=embed)

@bot.command(name="cat")
async def cat(ctx):
    await ctx.send("🐱 https://cataas.com/cat")

@bot.command(name="dog")
async def dog(ctx):
    await ctx.send("🐕 https://dog.ceo/api/breeds/image/random")

@bot.command(name="8ball")
async def eightball(ctx, *, question=None):
    if not question:
        await ctx.send("Задай вопрос: `!8ball <вопрос>`")
        return
    
    answers = [
        "Да!", "Нет", "Возможно", "Скорее всего да", "Скорее всего нет",
        "Определённо", "Не знаю", "Звезды говорят - да", "Звезды говорят - нет",
        "Спроси позже", "Безусловно", "Мой ответ — нет", "Перспективы хорошие"
    ]
    await ctx.send(f"🎱 {random.choice(answers)}")

@bot.command(name="roll")
async def roll(ctx, sides: int = 6):
    if sides > 100:
        sides = 100
    result = random.randint(1, sides)
    await ctx.send(f"🎲 Выпало: **{result}** (из {sides})")

@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: nextcord.Member, *, reason=None):
    await member.kick(reason=reason)
    embed = nextcord.Embed(title="👢 Кик", color=0xff0000)
    embed.description = f"{member.name} кикнут"
    if reason:
        embed.add_field(name="Причина", value=reason)
    await ctx.send(embed=embed)

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: nextcord.Member, *, reason=None):
    await member.ban(reason=reason)
    embed = nextcord.Embed(title="🔨 Бан", color=0xff0000)
    embed.description = f"{member.name} забанен"
    if reason:
        embed.add_field(name="Причина", value=reason)
    await ctx.send(embed=embed)

@bot.command(name="mute")
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: nextcord.Member, duration: int = 60):
    role = nextcord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
        role = await ctx.guild.create_role(name="Muted", color=nextcord.Color.dark_grey())
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(role, send_messages=False, connect=False)
    
    await member.add_roles(role)
    embed = nextcord.Embed(title="🔇 Мьют", color=0xffaa00)
    embed.description = f"{member.name} замьючен на {duration} минут"
    await ctx.send(embed=embed)

@bot.command(name="unmute")
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: nextcord.Member):
    role = nextcord.utils.get(ctx.guild.roles, name="Muted")
    if role:
        await member.remove_roles(role)
        await ctx.send(f"🔊 {member.name} размьючен")

@bot.command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    if amount > 100:
        amount = 100
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"✅ Удалено {amount} сообщений", delete_after=3)

@bot.command(name="say")
@commands.has_permissions(manage_messages=True)
async def say(ctx, *, text):
    await ctx.send(text)
    await ctx.message.delete()

@bot.command(name="help")
async def help_cmd(ctx):
    embed = nextcord.Embed(title="📚 Команды бота", color=0x00ff00)
    embed.add_field(name="🎮 Основные", value="`!ping` - пинг\n`!quote` - случайная цитата\n`!joke` - анекдот\n`!8ball <вопрос>` - предсказание\n`!roll [число]` - кубик", inline=False)
    embed.add_field(name="📊 Уровни & Экономика", value="`!profile [user]` - профиль\n`!top` - топ игроков\n`!balance [user]` - баланс\n`!daily` - ежедневные монеты\n`!casino <ставка>` - казино", inline=False)
    embed.add_field(name="🏆 Достижения", value="`!achievements [user]` - твои достижения", inline=False)
    embed.add_field(name="🛠️ Модерация", value="`!kick` - кик\n`!ban` - бан\n`!mute` - мьют\n`!unmute` - размьют\n`!clear` - очистка", inline=False)
    embed.add_field(name="🎲 Развлечения", value="`!meme` - мем\n`!cat` - кот\n`!dog` - собака\n`!rps <r/p/s>` - камень-ножницы-бумага\n`!hack <@user>` - мини-игра", inline=False)
    embed.set_footer(text="Bot for Ебаного Таркова | 31+")
    await ctx.send(embed=embed)

import asyncio

if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_TOKEN'))

