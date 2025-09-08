import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler, \
    CallbackQueryHandler
from telegram.constants import ParseMode

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
(
    MAIN_MENU,
    CAR_INFO,
    ADDRESS_SELECT,
    ALARM_TYPE,
    TINTING_TYPE,
    CAMERA_NEED,
    MILEAGE,
    LAST_SERVICE,
    RECORD_CONFIRMATION
) = range(9)


# Класс для хранения данных пользователя
class UserData:
    def __init__(self):
        self.car_model = None
        self.service_type = None
        self.address = None
        self.alarm_type = None
        self.tinting_type = None
        self.camera_need = None
        self.mileage = None
        self.last_service = None


user_sessions = {}


# Главное меню
def main_menu_keyboard():
    keyboard = [
        ['📍 Наши адреса'],
        ['🚨 Установка сигнализации'],
        ['🪟 Тонировка авто'],
        ['📱 Установка андроид магнитолы'],
        ['🔧 Плановое ТО и Ремонт']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# Клавиатура "Назад"
def back_keyboard():
    keyboard = [['⬅️ Назад']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# Клавиатура для выбора адреса
def address_keyboard():
    keyboard = [
        ['📍 ул. Фадеева, 51А', '📍 Московское ш., 16 км, 1А'],
        ['⬅️ Назад']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# Начало работы бота
async def start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    user_sessions[user_id] = UserData()

    await update.message.reply_text(
        "Добро пожаловать! Выберите услугу:",
        reply_markup=main_menu_keyboard()
    )
    return MAIN_MENU


# Обработка главного меню
async def handle_main_menu(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    user_id = update.message.from_user.id

    if text == '📍 Наши адреса':
        await show_addresses(update)
        return MAIN_MENU

    elif text == '🚨 Установка сигнализации':
        user_sessions[user_id].service_type = 'signalization'
        await update.message.reply_text(
            "Введите марку, модель и год вашего автомобиля:",
            reply_markup=back_keyboard()
        )
        return CAR_INFO

    elif text == '🪟 Тонировка авто':
        user_sessions[user_id].service_type = 'tinting'
        await update.message.reply_text(
            "Введите марку, модель и год вашего автомобиля:",
            reply_markup=back_keyboard()
        )
        return CAR_INFO

    elif text == '📱 Установка андроид магнитолы':
        user_sessions[user_id].service_type = 'android_radio'
        await update.message.reply_text(
            "Введите марку, модель и год вашего автомобиля:",
            reply_markup=back_keyboard()
        )
        return CAR_INFO

    elif text == '🔧 Плановое ТО и Ремонт':
        user_sessions[user_id].service_type = 'service'
        await update.message.reply_text(
            "Введите марку, модель и год вашего автомобиля:",
            reply_markup=back_keyboard()
        )
        return CAR_INFO

    return MAIN_MENU


# Показать адреса
async def show_addresses(update: Update):
    addresses_text = (
        "Работаем без выходных с 9 до 19\n\n"
        "📍<a href='https://maps.google.com/?q=ул. Фадеева, 51А'>ул. Фадеева, 51А</a>\n"
        "<a href='tel:+79272679070'>+7 (927) 267-90-70</a>\n\n"
        "📍<a href='https://maps.google.com/?q=Московское ш., 16 км, 1А'>Московское ш., 16 км, 1А</a>\n"
        "<a href='tel:+79371809633'>+7 (937) 180-96-33</a>"
    )

    keyboard = [
        [InlineKeyboardButton("Записаться на установку", callback_data="record_installation")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        addresses_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )


# Обработка кнопки "Записаться на установку"
async def handle_record_button(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user_sessions[user_id] = UserData()
    user_sessions[user_id].service_type = 'installation'

    await query.edit_message_text(
        "Введите марку, модель и год вашего автомобиля:",
        reply_markup=back_keyboard()
    )
    return CAR_INFO


# Получение информации об автомобиле
async def get_car_info(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    user_sessions[user_id].car_model = update.message.text

    service_type = user_sessions[user_id].service_type

    if service_type == 'signalization':
        keyboard = [
            ['🚗 Сигнализация с автозапуском', '🚙 Сигнализация без автозапуском'],
            ['⬅️ Назад']
        ]
        await update.message.reply_text(
            "Выберите тип сигнализации:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return ALARM_TYPE

    elif service_type == 'tinting':
        keyboard = [
            ['🔲 Задний отсек', '🔳 Передние боковые', '🌐 Лобовое стекло'],
            ['⬅️ Назад']
        ]
        await update.message.reply_text(
            "Выберите тип тонировки:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return TINTING_TYPE

    elif service_type == 'android_radio':
        keyboard = [
            ['✅ Да', '❌ Нет'],
            ['⬅️ Назад']
        ]
        await update.message.reply_text(
            "Требуется ли установка камеры заднего вида?",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return CAMERA_NEED

    elif service_type == 'service':
        keyboard = [
            ['До 15 000 км', '15 000 - 30 000 км', '30 000 - 60 000 км'],
            ['60 000 - 100 000 км', 'Свыше 100 000 км'],
            ['⬅️ Назад']
        ]
        await update.message.reply_text(
            "Какой у вас пробег автомобиля?",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return MILEAGE

    elif service_type == 'installation':
        await update.message.reply_text(
            "Выберите адрес:",
            reply_markup=address_keyboard()
        )
        return ADDRESS_SELECT


# Обработка выбора типа сигнализации
async def handle_alarm_type(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    user_sessions[user_id].alarm_type = update.message.text

    await update.message.reply_text(
        "Выберите адрес:",
        reply_markup=address_keyboard()
    )
    return ADDRESS_SELECT


# Обработка выбора типа тонировки
async def handle_tinting_type(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    user_sessions[user_id].tinting_type = update.message.text

    await update.message.reply_text(
        "Выберите адрес:",
        reply_markup=address_keyboard()
    )
    return ADDRESS_SELECT


# Обработка необходимости камеры
async def handle_camera_need(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    user_sessions[user_id].camera_need = update.message.text

    await update.message.reply_text(
        "Выберите адрес:",
        reply_markup=address_keyboard()
    )
    return ADDRESS_SELECT


# Обработка пробега
async def handle_mileage(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    user_sessions[user_id].mileage = update.message.text

    keyboard = [
        ['Менее 6 месяцев назад', '6-12 месяцев назад'],
        ['Более года назад', 'Не помню'],
        ['⬅️ Назад']
    ]
    await update.message.reply_text(
        "Когда было последнее ТО?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return LAST_SERVICE


# Обработка последнего ТО
async def handle_last_service(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    user_sessions[user_id].last_service = update.message.text

    await update.message.reply_text(
        "Выберите адрес:",
        reply_markup=address_keyboard()
    )
    return ADDRESS_SELECT


# Обработка выбора адреса
async def handle_address_select(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    user_sessions[user_id].address = update.message.text

    # Формирование сообщения с данными
    user_data = user_sessions[user_id]
    message = f"✅ Заявка оформлена!\n\n"
    message += f"🚗 Автомобиль: {user_data.car_model}\n"
    message += f"📍 Адрес: {user_data.address}\n"

    if user_data.service_type == 'signalization':
        message += f"🚨 Услуга: Установка сигнализации\n"
        message += f"📋 Тип: {user_data.alarm_type}\n"
    elif user_data.service_type == 'tinting':
        message += f"🪟 Услуга: Тонировка авто\n"
        message += f"📋 Тип: {user_data.tinting_type}\n"
    elif user_data.service_type == 'android_radio':
        message += f"📱 Услуга: Установка андроид магнитолы\n"
        message += f"📷 Камера заднего вида: {user_data.camera_need}\n"
    elif user_data.service_type == 'service':
        message += f"🔧 Услуга: Плановое ТО и Ремонт\n"
        message += f"📏 Пробег: {user_data.mileage}\n"
        message += f"⏰ Последнее ТО: {user_data.last_service}\n"
    elif user_data.service_type == 'installation':
        message += f"🔧 Услуга: Запись на установку\n"

    message += f"\nС вами свяжутся в ближайшее время!"

    await update.message.reply_text(
        message,
        reply_markup=main_menu_keyboard()
    )

    # Очистка данных пользователя
    del user_sessions[user_id]

    return MAIN_MENU


# Обработка кнопки "Назад"
async def handle_back(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "Главное меню:",
        reply_markup=main_menu_keyboard()
    )
    return MAIN_MENU


# Обработка отмены
async def cancel(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    if user_id in user_sessions:
        del user_sessions[user_id]

    await update.message.reply_text(
        "Действие отменено. Возврат в главное меню.",
        reply_markup=main_menu_keyboard()
    )
    return MAIN_MENU


def main() -> None:
    # Создание приложения
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

    # Создание ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [
                MessageHandler(filters.Text(['📍 Наши адреса', '🚨 Установка сигнализации', '🪟 Тонировка авто',
                                             '📱 Установка андроид магнитолы', '🔧 Плановое ТО и Ремонт']),
                               handle_main_menu),
                CallbackQueryHandler(handle_record_button, pattern="^record_installation$")
            ],
            CAR_INFO: [
                MessageHandler(filters.TEXT & ~filters.Text(['⬅️ Назад']), get_car_info),
                MessageHandler(filters.Text(['⬅️ Назад']), handle_back)
            ],
            ALARM_TYPE: [
                MessageHandler(filters.Text(['🚗 Сигнализация с автозапуском', '🚙 Сигнализация без автозапуском']),
                               handle_alarm_type),
                MessageHandler(filters.Text(['⬅️ Назад']), handle_back)
            ],
            TINTING_TYPE: [
                MessageHandler(filters.Text(['🔲 Задний отсек', '🔳 Передние боковые', '🌐 Лобовое стекло']),
                               handle_tinting_type),
                MessageHandler(filters.Text(['⬅️ Назад']), handle_back)
            ],
            CAMERA_NEED: [
                MessageHandler(filters.Text(['✅ Да', '❌ Нет']), handle_camera_need),
                MessageHandler(filters.Text(['⬅️ Назад']), handle_back)
            ],
            MILEAGE: [
                MessageHandler(filters.Text(['До 15 000 км', '15 000 - 30 000 км', '30 000 - 60 000 км',
                                             '60 000 - 100 000 км', 'Свыше 100 000 км']), handle_mileage),
                MessageHandler(filters.Text(['⬅️ Назад']), handle_back)
            ],
            LAST_SERVICE: [
                MessageHandler(filters.Text(['Менее 6 месяцев назад', '6-12 месяцев назад',
                                             'Более года назад', 'Не помню']), handle_last_service),
                MessageHandler(filters.Text(['⬅️ Назад']), handle_back)
            ],
            ADDRESS_SELECT: [
                MessageHandler(filters.Text(['📍 ул. Фадеева, 51А', '📍 Московское ш., 16 км, 1А']),
                               handle_address_select),
                MessageHandler(filters.Text(['⬅️ Назад']), handle_back)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Добавление обработчиков
    application.add_handler(conv_handler)

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    main()