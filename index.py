import telebot
from telebot import types

bot = telebot.TeleBot('8047059904:AAE_A_6Hir3WWzkJ95CVXRUyC4rHgxAktP0')

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

def set_command(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('Группа', callback_data='group')
    btn2 = types.InlineKeyboardButton('Уведомления', callback_data='notifications')
    btn3 = types.InlineKeyboardButton('Формат времени', callback_data='time_format')
    btn4 = types.InlineKeyboardButton('Язык', callback_data='language')
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(message.chat.id, f'⚙️ Настройки', reply_markup=markup)

if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f'Произошла ошибка при запуске бота: {e}')