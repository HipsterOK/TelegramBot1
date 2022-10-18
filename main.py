import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot('5611209525:AAGM7lOYw4jIKUV6p1Zll6n_sz9hvkQuv8U')
conn = sqlite3.connect('db/database', check_same_thread=False)
cursor = conn.cursor()


def to_fixed(num_obj, digits=0):
    return f"{num_obj:.{digits}f}"


def menu_buttons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    item1 = types.KeyboardButton("/rashod")
    item2 = types.KeyboardButton("/dohod")
    item3 = types.KeyboardButton("/balance")
    markup.add(item3)
    markup.row(item1, item2)
    return markup


def db_table_val(user_id: int, user_name: str, user_surname: str, username: str, balance: float):
    try:
        cursor.execute('INSERT INTO users (user_id, user_name, user_surname, username, balance) VALUES (?, ?, ?, ?, ?)',
                       (user_id, user_name, user_surname, username, balance))
        conn.commit()
    except conn.OperationalError:
        bot.send_message(user_id, "Ошибка базы данных!", reply_markup=menu_buttons())
    except conn.IntegrityError:
        bot.send_message(user_id, "Ваши данные обновлены!", reply_markup=menu_buttons())
        cursor.execute('UPDATE users SET user_name = ?, user_surname = ?, username = ? where user_id = ?',
                       (user_name, user_surname, username, user_id,))
        conn.commit()


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Добро пожаловать!', reply_markup=menu_buttons())
    us_id = message.from_user.id
    us_name = message.from_user.first_name
    us_sname = message.from_user.last_name
    username = message.from_user.username
    db_table_val(user_id=us_id, user_name=us_name, user_surname=us_sname, username=username, balance=0)


@bot.message_handler(commands=['balance'])
def my_balance(message):
    summa = cursor.execute('SELECT balance from users WHERE user_id = ?', (message.chat.id,)).fetchone()[0]
    bot.send_message(message.chat.id, 'Текущий баланс:' + '\n' + to_fixed(summa, 2), reply_markup=menu_buttons())


@bot.message_handler(commands=['dohod'])
def new_dohod(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    item1 = types.KeyboardButton("Отмена")
    markup.add(item1)
    send = bot.send_message(message.chat.id, 'Введите сумму дохода:', reply_markup=markup)
    bot.register_next_step_handler(send, get_summa_dohoda)


def get_summa_dohoda(message):
    if message.text.lower() == 'отмена':
        bot.send_message(message.from_user.id, 'Главное меню', reply_markup=menu_buttons())
        return
    try:
        v = to_fixed(float(message.text), 2)
        if float(v) < 0:
            raise ValueError()
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели некорректные данные!", reply_markup=menu_buttons())
    else:
        summaOst = float(v)
        summa = cursor.execute('SELECT balance from users WHERE user_id = ?', (message.chat.id,)).fetchone()[0]
        summaOst += summa
        bot.send_message(message.chat.id, 'Текущий баланс:' + '\n' + str(summaOst), reply_markup=menu_buttons())
        conn.execute('UPDATE users SET balance = ? where user_id = ?', (summaOst, message.chat.id,))
        conn.commit()


@bot.message_handler(commands=['rashod'])
def new_rashod(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    item1 = types.KeyboardButton("Непредвиденные расходы")
    item2 = types.KeyboardButton("Развлечения")
    item3 = types.KeyboardButton("Лекарства")
    item4 = types.KeyboardButton("Оплата связи")
    item5 = types.KeyboardButton("Трансопртные расходы")
    item6 = types.KeyboardButton("Коммунальные услуги")
    item7 = types.KeyboardButton("Хозяйственные расходы")
    item8 = types.KeyboardButton("Питание")
    item9 = types.KeyboardButton("Одежда")
    item10 = types.KeyboardButton("Другое")
    item11 = types.KeyboardButton("Отмена")
    markup.add(item11)
    markup.add(item1)
    markup.add(item2)
    markup.add(item3)
    markup.add(item4)
    markup.add(item5)
    markup.add(item6)
    markup.add(item7)
    markup.add(item8)
    markup.add(item9)
    markup.add(item10)
    send = bot.send_message(message.chat.id, 'Выберите категорию', reply_markup=markup)
    bot.register_next_step_handler(send, get_summa_rashoda)


def get_summa_rashoda(message):
    if message.text in (
            "Непредвиденные расходы", "Развлечения", "Лекарства", "Оплата связи", "Трансопртные расходы",
            "Коммунальные услуги",
            "Хозяйственные расходы", "Питание", "Одежда", "Другое", "Отмена"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        item1 = types.KeyboardButton("Отмена")
        markup.add(item1)
        global typeRashod
        typeRashod = message.text
        if message.text.lower() == 'отмена':
            bot.send_message(message.from_user.id, 'Главное меню', reply_markup=menu_buttons())
            return
        send = bot.send_message(message.chat.id, 'Введите сумму:', reply_markup=markup)
        bot.register_next_step_handler(send, save_rashod)
    else:
        bot.send_message(message.chat.id, "Вы ввели некорректные данные!", reply_markup=menu_buttons())


def save_rashod(message):
    if message.text.lower() == 'отмена':
        bot.send_message(message.from_user.id, 'Главное меню')
        return
    try:
        v = to_fixed(float(message.text), 2)
        if float(v) < 0:
            raise ValueError()
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели некорректные данные!", reply_markup=menu_buttons())
    else:
        summaRashod = float(v)
        summaOst = cursor.execute('SELECT balance from users WHERE user_id = ?', (message.chat.id,)).fetchone()[0]
        bot.send_message(message.chat.id, 'Новый расход:' + "\n" + typeRashod + "\n" + str(summaRashod))
        cursor.execute('INSERT INTO user_rashod (user_id, summa, type) VALUES (?, ?, ?)',
                       (message.chat.id, summaRashod, typeRashod))
        conn.commit()
        summaOst -= summaRashod
        bot.send_message(message.chat.id, 'Новый баланс:' + '\n' + str(summaOst), reply_markup=menu_buttons())
        conn.execute('UPDATE users SET balance = ? where user_id = ?', (summaOst, message.chat.id,))
        conn.commit()


bot.infinity_polling(none_stop=True)
