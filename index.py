import telebot
import sqlite3
from telebot import types

bot = telebot.TeleBot('8047059904:AAE_A_6Hir3WWzkJ95CVXRUyC4rHgxAktP0')

data = {
    "18.01.2025": {
        "СУББОТА": {
            "1": {
                "История": {
                    "teacher": "Зубарев А.А.",
                    "room": None
                }
            },
            "2": {
                "МДК 04.02 Обеспечение качества функционирования КС": {
                    "teacher": "Ольнев А.А.",
                    "room": None
                }
            },
            "3": {
                "ИТ": {
                    "teacher": "Сухорукова О.А.",
                    "room": None
                }
            }
        }
    }
}

group_name = "12919"

conn = sqlite3.connect('schedule.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT UNIQUE
)
''')

cursor.execute('''
INSERT OR IGNORE INTO groups (group_name) VALUES (?)
''', (group_name,))

cursor.execute('SELECT id FROM groups WHERE group_name = ?', (group_name,))
group_id_result = cursor.fetchone()

if group_id_result:
    group_id = group_id_result[0]
else:
    print("Ошибка: Группа не найдена.")
    group_id = None

cursor.execute('''
CREATE TABLE IF NOT EXISTS schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    day_of_week TEXT,
    time INTEGER,
    subject TEXT,
    teacher TEXT,
    room TEXT,
    group_id INTEGER,
    FOREIGN KEY (group_id) REFERENCES groups (id),
    UNIQUE(date, day_of_week, time, subject, group_id)
)
''')

if group_id is not None:
    for date, days in data.items():
        for day, lessons in days.items():
            for time, lesson in lessons.items():
                subject = list(lesson.keys())[0]
                teacher = lesson[subject]['teacher']
                room = lesson[subject]['room']
                
                cursor.execute('''
                INSERT OR IGNORE INTO schedule (date, day_of_week, time, subject, teacher, room, group_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (date, day, time, subject, teacher, room, group_id))

conn.commit()
conn.close()

print("Данные успешно добавлены в базу данных.")



@bot.message_handler(commands=['start'])
def start_command(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('📆 Расписание', callback_data='schedule')
    btn2 = types.InlineKeyboardButton('⚙️ Настройки', callback_data='settings')
    btn3 = types.InlineKeyboardButton('🔔 Уведомление', callback_data='notifications')
    btn4 = types.InlineKeyboardButton('❓ Помощь', callback_data='help')
    btn5 = types.InlineKeyboardButton('📢 Объявления', callback_data='announcements')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    
    bot.send_message(
        message.chat.id,
        f'👋 Привет, {message.from_user.first_name}! Я — твой помощник по расписанию! 📚\n\n'
        f'✨ Что я умею:\n'
        f'• Показывать расписание на сегодня, завтра или любую дату.\n'
        f'• Напоминать о парах за 15/30/60 минут (настроишь в разделе "Уведомления").\n'
        f'• Держать в курсе актуальных изменений и экзаменов.\n'
        f'• Подсказывать контакты преподавателей и аудитории.\n\n'
        f'👉 Просто выбери нужную кнопку ниже, чтобы начать!\n'
        f'_Если что-то пойдет не так — жми «Помощь» или пиши /help._\n\n'
        f'🚀 Давай начнем! Выбери действие:',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'settings':
        set_command(callback.message)
    elif callback.data == 'schedule':
        number_group(callback.message)

def set_command(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('Группа', callback_data='group')
    btn2 = types.InlineKeyboardButton('Уведомления', callback_data='notifications')
    btn3 = types.InlineKeyboardButton('Формат времени', callback_data='time_format')
    btn4 = types.InlineKeyboardButton('Язык', callback_data='language')
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(message.chat.id, f'⚙️ Настройки', reply_markup=markup)



def number_group(message):
    markup = types.InlineKeyboardMarkup(row_width=1)

    connection = sqlite3.connect('schedule.db')
    cursor = connection.cursor()

    cursor.execute('SELECT id, group_name FROM groups')  
    groups = cursor.fetchall()  

    if groups:
        for group in groups:
            group_id, group_name = group
            btn = types.InlineKeyboardButton(f'Группа {group_name}', callback_data=f'group_{group_id}')
            markup.add(btn)
    else:
        btn = types.InlineKeyboardButton('Нет доступных групп', callback_data='no_group')
        markup.add(btn)

    cursor.close()  
    connection.close()  

    bot.send_message(message.chat.id, 'Выберите номер группы', reply_markup=markup) 

@bot.callback_query_handler(func=lambda call: call.data.startswith('group_'))
def handle_group_selection(call):
    group_id = call.data.split('_')[1]  # Получаем ID группы из callback_data

    connection = sqlite3.connect('schedule.db')
    cursor = connection.cursor()

    # Отладочное сообщение
    print(f"Запрос расписания для группы с ID: {group_id}")

    # Проверка наличия расписания для группы
    cursor.execute('SELECT * FROM schedule WHERE group_id = ?', (group_id,))
    schedule = cursor.fetchall()

    if schedule:
        response = "Расписание для группы:\n"
        for entry in schedule:
            response += f"Дата: {entry[1]}, День: {entry[2]}, Время: {entry[3]}, Предмет: {entry[4]}, Преподаватель: {entry[5]}, Аудитория: {entry[6]}\n"
    else:
        response = "Нет расписания для выбранной группы."

    cursor.close()
    connection.close()

    print(response)
    print(f"Расписание для группы {group_id}: {schedule}")
    bot.send_message(call.message.chat.id, response)


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f'Произошла ошибка при запуске бота: {e}')