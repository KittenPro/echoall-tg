from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ContentTypes
from aiogram import Bot, Dispatcher, executor, types
import asyncio
import config
import db
bot = Bot(token=config.BOT_TOKEN, parse_mode="html")
dp = Dispatcher(bot)
db.create()
async def started(dp):
    for a in config.ADMIN_ID:
        await bot.send_message(chat_id=a, text='✅Бот запущен!')
@dp.message_handler(commands='start')
async def start(message):
    name = db.get('name', message.from_user.id)
    if name == None:
        db.insert(message.from_user.first_name, message.from_user.id)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    stats = KeyboardButton(text="📊Статистика")
    profile = KeyboardButton(text="👤Профиль")
    keyboard.add(profile, stats)
    await message.reply(f'👋Привет, я - бот который разошлет твоё сообщение всем!', reply_markup=keyboard)
@dp.message_handler(lambda msg: msg.text == '👤Профиль')
async def profile(message):
   await message.reply(f"👤Имя: {message.from_user.first_name}\n🐕Юзернейм: @{message.from_user.username}\n🆔Айди: <code>{message.from_user.id}</code>\n🔝Сообщений: {db.get('msgs', message.from_user.id)}")
@dp.message_handler(lambda msg: msg.text == '📊Статистика')
async def stats(message):
   db.cursor.execute("SELECT id FROM users")
   await message.reply(f'👥Пользователей в боте: {str(len(db.cursor.fetchall()))}')
@dp.message_handler(commands=['ban', 'бан'], commands_prefix='!?./', is_chat_admin=True)
async def ban(message):
    if message.from_user.id not in config.ADMIN_ID:
        await message.reply("❌Недостаточно прав!")
        return
    try:
        ban_user = message.text.split()[1]
    except:
         await message.reply("❌Неправильно указаны аргументы!")
         return
    ban = db.get('ban', ban_user)
    if ban == None:
        await message.reply("❌Пользователя нет в базе данных!")
        return
    elif ban == 1:
        await message.reply("❌Пользователь уже забанен!")
        return
    else:
        db.set('ban', 1, ban_user)
        await message.reply(f"✅Пользователь {ban_user} забанен!")
        try:
            await bot.send_message(ban_user, text='<b>❌Тебя забанили в боте!</b>')
        except:
            pass
@dp.message_handler(commands=['unban', 'разбан'], commands_prefix='!?./', is_chat_admin=True)
async def unban(message):
    if message.from_user.id not in config.ADMIN_ID:
        await message.reply("❌Недостаточно прав!")
        return
    try:
        unban_user = message.text.split()[1]
    except:
        await message.reply("❌Неправильно указаны аргументы!")
        return
    ban = db.get('ban', unban_user)
    if ban == None:
        await message.reply("❌Пользователя нет в базе данных!")
        return
    elif ban == 0:
        await message.reply("❌Пользователь не забанен!")
        return
    else:
        db.set('ban', 0, unban_user)
        await message.reply(f"✅Пользователь {unban_user} разбанен!")
        try:
            await bot.send_message(unban_user, text='<b>✅Тебя разбанили в боте!</b>')
        except:
            pass
cooldown = []
@dp.message_handler(content_types=ContentTypes.all())
async def echo(message):
    if message.chat.type != "private":
        await bot.leave_chat(message.chat.id)
        return
    if message.from_user.id in cooldown:
        await message.reply("❌Не так часто! Отправлять сообщение можно раз в минуту!")
        return
    ban = db.get('ban', message.from_user.id)
    if ban == 1:
        await message.reply("❌Вы забанены в боте!")
        return
    msgs = db.get('msgs', message.from_user.id)
    db.set('msgs', msgs + 1, message.from_user.id)
    user_all = db.all()
    user_ids = [user[0] for user in user_all]
    await message.reply(f'📲Отправляю твоё сообщение {str(len(user_all))} юзерам..')
    for user in user_ids:
        admin_kb = InlineKeyboardMarkup()
        admin_button = InlineKeyboardButton(text="💙АДМИН💙", url=f"t.me/{message.from_user.username}")
        admin_kb.add(admin_button)
        if message.from_user.id in config.ADMIN_ID:
            try:
                if message.reply_to_message:
                    await bot.send_message(user, text=f'>> {message.reply_to_message.text}\n\n{message.text}', reply_markup=admin_kb)
                else:
                    await message.copy_to(user, reply_markup=admin_kb)
            except:
                pass
        else:
            try:
                if message.reply_to_message:
                    await bot.send_message(user, text=f'>> {message.reply_to_message.text}\n\n{message.text}')
                else:
                    await message.copy_to(user)
            except:
                pass
            cooldown.append(message.from_user.id)
            await asyncio.sleep(config.cooldown)
            cooldown.remove(message.from_user.id)
executor.start_polling(dp, on_startup=started, skip_updates=True)