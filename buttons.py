from telebot import types


def gender():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
    male = types.KeyboardButton('мужской')
    female = types.KeyboardButton('женский')
    markup.add(male, female)
    return markup


def category():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
    category1 = types.KeyboardButton('Серьёзные отношения💞')
    category2 = types.KeyboardButton('Свободные отношения❤️‍🔥')
    category3 = types.KeyboardButton('Дружба🫡')
    category4 = types.KeyboardButton('Не определился🫠')
    markup.add(category1, category2, category3, category4)
    return markup


def send_locaton():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    locaton = types.KeyboardButton('Моя локация', request_location=True)
    markup.add(locaton)
    return markup


def skip():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    skip = types.KeyboardButton('Пропустить')
    markup.add(skip)
    return markup


def watch_photo():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    skip = types.KeyboardButton('Смотреть мои фотографии')
    markup.add(skip)
    return markup


def find_age():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    age1 = types.KeyboardButton('18-25')
    age2 = types.KeyboardButton('25-35')
    age3 = types.KeyboardButton('45-55')
    age4 = types.KeyboardButton('55-65')
    markup.add(age1, age2, age3, age4)
    return markup


def find_gender():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
    male = types.KeyboardButton('мужской')
    female = types.KeyboardButton('женский')
    all = types.KeyboardButton('любой')
    markup.add(male, female, all)
    return markup


def check(id):
    markup = types.InlineKeyboardMarkup()
    acept = types.InlineKeyboardButton('Одобрить', callback_data=f'acept|{id}')
    cansel = types.InlineKeyboardButton('Отказать', callback_data=f'cansel|{id}')
    markup.add(acept, cansel)
    return markup


def menu(user):
    markup = types.InlineKeyboardMarkup(row_width=1)
    watch = types.InlineKeyboardButton('Смотреть анкеты 👀', callback_data='profiles')
    create = types.InlineKeyboardButton(f'Мэтчи ({user.like_users.all().count()}) ♥️',
                                        callback_data='profiles|watch_like')
    edit_filter = types.InlineKeyboardButton('Настроить поиск 🔍', callback_data='filter')
    verefi = types.InlineKeyboardButton('Подтверждение анкеты ✅', callback_data='edit_profile|verefi')
    my_active = types.InlineKeyboardButton('Моя активность ⚡️', callback_data='my_active')
    edit_profile = types.InlineKeyboardButton('Настроить анкету ⚙️', callback_data='edit_profile')
    markup.add(watch, create, edit_filter, verefi, my_active ,edit_profile)
    return markup


def filter_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    watch = types.InlineKeyboardButton('К анкетам 👀', callback_data='profiles')
    edit_age = types.InlineKeyboardButton('Изменить возраст', callback_data='filter|age')
    edit_gender = types.InlineKeyboardButton('Выбрать пол', callback_data='filter|gender')
    edit_category = types.InlineKeyboardButton('Определить цель', callback_data='filter|category')
    menu = types.InlineKeyboardButton('В меню ', callback_data='menu')
    markup.add(edit_age, edit_gender, edit_category, menu, watch)
    return markup


def profile_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    edit_avatar = types.InlineKeyboardButton('Изменить фотографию', callback_data='edit_profile|photo')
    edit_name = types.InlineKeyboardButton('Изменить имя', callback_data='edit_profile|name')
    edit_gender = types.InlineKeyboardButton('Изменить пол', callback_data='edit_profile|gender')
    edit_category = types.InlineKeyboardButton('Изменить категорию поиска', callback_data='edit_profile|category')
    edit_city = types.InlineKeyboardButton('Изменить город', callback_data='edit_profile|city')
    edit_description = types.InlineKeyboardButton('Изменить описание', callback_data='edit_profile|description')
    edit_age = types.InlineKeyboardButton('Изменить возраст', callback_data='edit_profile|age')
    go_sleep = types.InlineKeyboardButton('Выйти из поиска', callback_data='edit_profile|go_sleep')
    delite = types.InlineKeyboardButton('Удалить анкету', callback_data='edit_profile|delite')
    menu = types.InlineKeyboardButton('Вернуться назад ️️️⬅️', callback_data='menu')
    markup.add(edit_age, edit_name, edit_gender, edit_avatar, edit_city, edit_description, go_sleep, delite, menu)
    return markup


def questionnaire_menu(user_id):
    markup = types.InlineKeyboardMarkup(row_width=4)
    like = types.InlineKeyboardButton('💗', callback_data=f'profiles|like|{user_id}')
    dislike = types.InlineKeyboardButton('🚫', callback_data=f'profiles|dislike|{user_id}')
    sleep = types.InlineKeyboardButton('😴', callback_data='menu')
    send_message_or_video = types.InlineKeyboardButton('🎥/💬', callback_data=f'profiles|send_message_or_video|{user_id}')
    report = types.InlineKeyboardButton('Пожаловаться', callback_data=f'profiles|report|{user_id}')
    markup.add(like, dislike, sleep, send_message_or_video, report)
    return markup


def watch_questionnaire():
    markup = types.InlineKeyboardMarkup(row_width=1)
    watch = types.InlineKeyboardButton('Продолжить смотреть анкты', callback_data='profiles')
    menu = types.InlineKeyboardButton('В меню', callback_data='menu')
    markup.add(watch, menu)
    return markup


def watch_questionnaire_after_ad():
    markup = types.InlineKeyboardMarkup(row_width=1)
    watch = types.InlineKeyboardButton('Продолжить смотреть анкты', callback_data='profiles_ad')
    menu = types.InlineKeyboardButton('В меню', callback_data='menu')
    markup.add(watch, menu)
    return markup


def answer_on_like(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    like = types.InlineKeyboardButton('💗', callback_data=f'profiles|answer_like|{user_id}')
    dislike = types.InlineKeyboardButton('🚫', callback_data=f'profiles|answer_dislike|{user_id}')
    report = types.InlineKeyboardButton('Пожаловаться', callback_data=f'profiles|report|{user_id}')
    menu = types.InlineKeyboardButton('В меню', callback_data='menu')
    markup.add(like, dislike, report)
    markup.add(menu)
    return markup


def send_link_on_chat(user_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    link = types.InlineKeyboardButton('Профиль пользователя', url=f'tg://user?id={user_id}')
    menu = types.InlineKeyboardButton('В меню', callback_data='menuAfterLike')
    markup.add(link, menu)
    return markup


def go_to_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    menu = types.InlineKeyboardButton('В меню', callback_data='menu')
    markup.add(menu)
    return markup


def first_edit_photo():
    markup = types.InlineKeyboardMarkup(row_width=1)
    first = types.InlineKeyboardButton('Изменить фото/видео 1', callback_data='first_edit_photo|1')
    second = types.InlineKeyboardButton('Изменить фото/видео 2', callback_data='first_edit_photo|2')
    therd = types.InlineKeyboardButton('Изменить фото/видео 3', callback_data='first_edit_photo|3')
    confirm = types.InlineKeyboardButton('Подтвердить', callback_data='menu')
    markup.add(first, second, therd, confirm)
    return markup


def edit_photo():
    markup = types.InlineKeyboardMarkup(row_width=1)
    first = types.InlineKeyboardButton('Редактировать фото/видео 1', callback_data='edit_profile|edit_photo|1')
    second = types.InlineKeyboardButton('Редактировать фото/видео 2', callback_data='edit_profile|edit_photo|2')
    therd = types.InlineKeyboardButton('Редактировать фото/видео 3', callback_data='edit_profile|edit_photo|3')
    back = types.InlineKeyboardButton('Назад ⏪', callback_data='edit_profile')
    markup.add(first, second, therd, back)
    return markup


def go_back(path):
    markup = types.InlineKeyboardMarkup(row_width=2)
    back = types.InlineKeyboardButton('Назад ⏪', callback_data=path)
    markup.add(back)
    return markup


def create():
    markup = types.InlineKeyboardMarkup()
    create = types.InlineKeyboardButton('Создать анкету', callback_data='create')
    markup.add(create)
    return markup


def watch_like():
    markup = types.InlineKeyboardMarkup()
    create = types.InlineKeyboardButton('Смотреть анкеты 👀', callback_data='profiles|watch_like')
    markup.add(create)
    return markup


def continue_watch():
    markup = types.InlineKeyboardMarkup(row_width=1)
    watch = types.InlineKeyboardButton('Смотреть анкеты 👀', callback_data='profiles')
    menu = types.InlineKeyboardButton('В меню', callback_data='menu')
    markup.add(watch, menu)
    return markup


def report_type():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
    type1 = types.KeyboardButton('Нежелательный сексуальный контент🔞')
    type2 = types.KeyboardButton('Скам, мошенничество')
    type3 = types.KeyboardButton('Навязчивая реклама 🤬')
    type4 = types.KeyboardButton('Оскорбление, буллинг⛔️')
    type5 = types.KeyboardButton('Экстремизм, расизм🗿')
    markup.add(type1, type2, type3, type4, type5)
    return markup
