import asyncio
import datetime
import html  # Для экранирования
import logging
import re

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove, Update)
from telegram.error import TelegramError
from telegram.ext import CallbackQueryHandler  # Добавляем CallbackQueryHandler
from telegram.ext import (Application, CommandHandler, ContextTypes,
                          ConversationHandler, MessageHandler, filters)

from habits.models import (HabitNice, HabitUseful, LikeAction, Location,
                           NeedAction, Reward)

User = get_user_model()
logger = logging.getLogger("bot_app")


(
    MENU,
    CREATE_LIKE_ACTION_NAME,
    CREATE_LIKE_ACTION_DESCRIPTION,
    CREATE_NEED_ACTION_NAME,
    CREATE_NEED_ACTION_DESCRIPTION,
    CREATE_LOCATION_NAME,
    CREATE_LOCATION_DESCRIPTION,
    CREATE_REWARD_NAME,
    CREATE_REWARD_DESCRIPTION,
    CREATE_NICE_HABIT_SELECT_LIKE_ACTION,
    CREATE_NICE_HABIT_NEW_LIKE_ACTION_NAME,
    CREATE_NICE_HABIT_NEW_LIKE_ACTION_DESCRIPTION,
    CREATE_NICE_HABIT_SELECT_LOCATION,
    CREATE_NICE_HABIT_NEW_LOCATION_NAME,
    CREATE_NICE_HABIT_NEW_LOCATION_DESCRIPTION,
    CREATE_USEFUL_HABIT_SELECT_NEED_ACTION,
    CREATE_USEFUL_HABIT_NEW_NEED_ACTION_NAME,
    CREATE_USEFUL_HABIT_NEW_NEED_ACTION_DESCRIPTION,
    CREATE_USEFUL_HABIT_SELECT_LOCATION,
    CREATE_USEFUL_HABIT_NEW_LOCATION_NAME,
    CREATE_USEFUL_HABIT_NEW_LOCATION_DESCRIPTION,
    CREATE_USEFUL_HABIT_SELECT_TIME,
    CREATE_USEFUL_HABIT_SELECT_PERIODICITY,
    CREATE_USEFUL_HABIT_SELECT_REWARD_OR_NICE_HABIT,
    CREATE_USEFUL_HABIT_SELECT_REWARD,
    CREATE_USEFUL_HABIT_SELECT_NICE_HABIT,
    CREATE_USEFUL_HABIT_IS_PUBLIC,
) = range(
    27
)  # Увеличиваем диапазон

# Хелперы для клавиатур
MAIN_MENU_KEYBOARD = [
    ["➕ Добавить любимое действие", "➕ Добавить нужное действие"],
    ["➕ Добавить локацию", "➕ Добавить награду"],
    ["✨ Создать приятную привычку", "📝 Создать полезную привычку"],
    ["📊 Мои привычки", "⚙️ Настройки"],
]

PERIODICITY_KEYBOARD = [
    ["1 день", "2 дня", "3 дня"],
    ["4 дня", "5 дней", "6 дней", "7 дней"],
]

PUBLIC_CHOICE_KEYBOARD = [["Да", "Нет"]]


# Общие хелперы
async def get_django_user_and_update_chat_id(telegram_user, chat_id):
    """Получает или создает пользователя Django и обновляет chat_id."""
    user, created = await User.objects.aget_or_create(
        username=telegram_user.username, defaults={"telegram_chat_id": chat_id}
    )
    if not created and not user.telegram_chat_id:
        user.telegram_chat_id = chat_id
        await user.asave()
        logger.info(f"Обновлен Telegram Chat ID для {user.username}: {chat_id}")
    elif created:
        logger.info(
            f"Создан новый пользователь Django: {user.username} с Chat ID: {chat_id}"
        )
    return user


async def check_user_and_call_next(
    update: Update, context: ContextTypes.DEFAULT_TYPE, next_handler_func
) -> int:
    """
    Проверяет, что пользователь Django существует в context.user_data.
    Если нет, получает/создает его. Затем вызывает переданный next_handler_func.
    """
    django_user = context.user_data.get("django_user")

    if not django_user:
        telegram_user = update.effective_user
        chat_id = (
            update.message.chat_id
            if update.message
            else (
                update.callback_query.message.chat_id
                if update.callback_query and update.callback_query.message
                else None
            )
        )

        if not telegram_user or not telegram_user.username or not chat_id:
            logger.warning(
                f"Не удалось получить telegram_user или chat_id для проверки Django пользователя. Update: {update.update_id}"
            )
            await (update.effective_message or update.message).reply_text(
                "Извините, для работы с ботом ваш Telegram аккаунт должен иметь Username и Chat ID."
                "Пожалуйста, установите его в настройках Telegram и попробуйте снова, или начните с /start."
            )
            return ConversationHandler.END  # Завершаем диалог

        django_user = await get_django_user_and_update_chat_id(telegram_user, chat_id)
        context.user_data["django_user"] = django_user
        logger.info(
            f"Django user {django_user.username} (ID: {django_user.id}) установлен в user_data."
        )

    # Теперь, когда django_user гарантированно есть, вызываем реальный обработчик
    return await next_handler_func(update, context)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик команды /start."""
    telegram_user = update.effective_user
    chat_id = update.message.chat_id

    if not telegram_user.username:
        await update.message.reply_text(
            "Извините, для работы с ботом ваш Telegram аккаунт должен иметь Username."
            "Пожалуйста, установите его в настройках Telegram и попробуйте снова."
        )
        return ConversationHandler.END

    django_user = await get_django_user_and_update_chat_id(telegram_user, chat_id)
    context.user_data["django_user"] = django_user

    await update.message.reply_html(
        f"<b>Привет, {html.escape(django_user.username)}!</b> Я твой помощник в формировании полезных привычек."
        f"\n\nИспользуй меню ниже, чтобы начать.",
        reply_markup=ReplyKeyboardMarkup(
            MAIN_MENU_KEYBOARD, resize_keyboard=True, one_time_keyboard=False
        ),
    )
    return MENU


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик для главного меню."""
    await update.message.reply_text(
        "Выбери опцию:",
        reply_markup=ReplyKeyboardMarkup(
            MAIN_MENU_KEYBOARD, resize_keyboard=True, one_time_keyboard=False
        ),
    )
    return MENU


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отменяет текущий диалог."""
    await update.message.reply_text(
        "Действие отменено.",
        reply_markup=ReplyKeyboardMarkup(
            MAIN_MENU_KEYBOARD, resize_keyboard=True, one_time_keyboard=False
        ),
    )
    return MENU


# Создание LikeAction, NeedAction, Location, Reward


# LikeAction
async def create_like_action_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        "Введите название нового любимого действия (например, 'Читать книгу'):",
        reply_markup=ReplyKeyboardRemove(),
    )
    return CREATE_LIKE_ACTION_NAME


async def create_like_action_name(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    action_name = update.message.text
    django_user = context.user_data["django_user"]
    like_actions = await sync_to_async(
        lambda: LikeAction.objects.filter(name=action_name, owner=django_user).exists()
    )()
    if like_actions:
        await update.message.reply_text(
            f"Любимое действие с названием '{action_name}' уже существует. Введите другое название."
        )
        return CREATE_LIKE_ACTION_NAME
    context.user_data["new_like_action_name"] = action_name
    await update.message.reply_text(
        "Введите описание действия (необязательно, можно пропустить, введите '-'):"
    )
    return CREATE_LIKE_ACTION_DESCRIPTION


async def create_like_action_description(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    action_description = update.message.text
    if action_description == "-":
        action_description = ""
    django_user = context.user_data["django_user"]
    action_name = context.user_data["new_like_action_name"]

    await sync_to_async(transaction.atomic)()  # Начинаем транзакцию асинхронно
    await sync_to_async(LikeAction.objects.create)(
        name=action_name, description=action_description, owner=django_user
    )

    await update.message.reply_text(
        f"Любимое действие '{action_name}' успешно создано!",
        reply_markup=ReplyKeyboardMarkup(
            MAIN_MENU_KEYBOARD, resize_keyboard=True, one_time_keyboard=False
        ),
    )
    return MENU


# NeedAction
async def create_need_action_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        "Введите название нового нужного действия (например, 'Пробежка'):",
        reply_markup=ReplyKeyboardRemove(),
    )
    return CREATE_NEED_ACTION_NAME


async def create_need_action_name(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    action_name = update.message.text
    django_user = context.user_data["django_user"]
    need_actions = await sync_to_async(
        lambda: NeedAction.objects.filter(name=action_name, owner=django_user).exists()
    )()
    if need_actions:
        await update.message.reply_text(
            f"Нужное действие с названием '{action_name}' уже существует. Введите другое название."
        )
        return CREATE_NEED_ACTION_NAME
    context.user_data["new_need_action_name"] = action_name
    await update.message.reply_text(
        "Введите описание действия (необязательно, можно пропустить, введите '-'):"
    )
    return CREATE_NEED_ACTION_DESCRIPTION


async def create_need_action_description(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    action_description = update.message.text
    if action_description == "-":
        action_description = ""
    django_user = context.user_data["django_user"]
    action_name = context.user_data["new_need_action_name"]

    await sync_to_async(transaction.atomic)()  # Начинаем транзакцию асинхронно
    await sync_to_async(NeedAction.objects.create)(
        name=action_name, description=action_description, owner=django_user
    )

    await update.message.reply_text(
        f"Нужное действие '{action_name}' успешно создано!",
        reply_markup=ReplyKeyboardMarkup(
            MAIN_MENU_KEYBOARD, resize_keyboard=True, one_time_keyboard=False
        ),
    )
    return MENU


# Location
async def create_location_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        "Введите название новой локации (например, 'Дом'):",
        reply_markup=ReplyKeyboardRemove(),
    )
    return CREATE_LOCATION_NAME


async def create_location_name(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    location_name = update.message.text
    django_user = context.user_data["django_user"]
    locations = await sync_to_async(
        lambda: Location.objects.filter(name=location_name, owner=django_user).exists()
    )()
    if locations:
        await update.message.reply_text(
            f"Локация с названием '{location_name}' уже существует. Введите другое название."
        )
        return CREATE_LOCATION_NAME
    context.user_data["new_location_name"] = location_name
    await update.message.reply_text(
        "Введите описание локации (необязательно, можно пропустить, введите '-'):"
    )
    return CREATE_LOCATION_DESCRIPTION


async def create_location_description(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    location_description = update.message.text
    if location_description == "-":
        location_description = ""
    django_user = context.user_data["django_user"]
    location_name = context.user_data["new_location_name"]

    await sync_to_async(transaction.atomic)()
    await sync_to_async(Location.objects.create)(
        name=location_name, description=location_description, owner=django_user
    )

    await update.message.reply_text(
        f"Локация '{location_name}' успешно создана!",
        reply_markup=ReplyKeyboardMarkup(
            MAIN_MENU_KEYBOARD, resize_keyboard=True, one_time_keyboard=False
        ),
    )
    return MENU

    # with transaction.atomic():
    #    await Location.objects.acreate(name=location_name, description=location_description, owner=django_user)
    # await update.message.reply_text(f"Локация '{location_name}' успешно создана!",
    #                                reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True,
    #                                                                one_time_keyboard=False))
    # return MENU


# Reward
async def create_reward_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        "Введите название нового вознаграждения (например, 'Чашка кофе'):",
        reply_markup=ReplyKeyboardRemove(),
    )
    return CREATE_REWARD_NAME


async def create_reward_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reward_name = update.message.text
    django_user = context.user_data["django_user"]

    rewards = await sync_to_async(
        lambda: Reward.objects.filter(name=reward_name, owner=django_user).exists()
    )()
    if rewards:
        await update.message.reply_text(
            f"Вознаграждение с названием '{reward_name}' уже существует. Введите другое название"
        )
        return CREATE_REWARD_NAME
    context.user_data["new_reward_name"] = reward_name
    await update.message.reply_text(
        "Введите описание вознаграждения (необязательно, можно пропустить, введите '-':"
    )
    return CREATE_REWARD_DESCRIPTION


async def create_reward_description(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    reward_description = update.message.text
    if reward_description == "-":
        reward_description = ""
    django_user = context.user_data["django_user"]
    reward_name = context.user_data["new_reward_name"]

    await sync_to_async(transaction.atomic)()
    await sync_to_async(Reward.objects.create)(
        name=reward_name, description=reward_description, owner=django_user
    )

    await update.message.reply_text(
        f"Вознаграждение '{reward_name}' успешно создано!",
        reply_markup=ReplyKeyboardMarkup(
            MAIN_MENU_KEYBOARD, resize_keyboard=True, one_time_keyboard=False
        ),
    )
    return MENU


# HabitNice
async def create_nice_habit_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    django_user = context.user_data["django_user"]
    # like_actions = await LikeAction.objects.filter(owner=django_user).values_list('name', 'id').all()

    like_actions = await sync_to_async(LikeAction.objects.filter)(owner=django_user)
    like_actions = await sync_to_async(like_actions.values_list)("name", "id")
    like_actions = await sync_to_async(like_actions.all)()

    keyboard = []
    if like_actions:
        for name, _id in like_actions:
            keyboard.append(
                [InlineKeyboardButton(name, callback_data=f"select_like_action_{_id}")]
            )

    keyboard.append(
        [
            InlineKeyboardButton(
                "➕ Создать новое любимое действие",
                callback_data="create_new_like_action",
            )
        ]
    )

    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

    await update.message.reply_text(
        "Выберите любимое действие для приятной привычки или создайте новое:",
        reply_markup=reply_markup,
    )
    return CREATE_NICE_HABIT_SELECT_LIKE_ACTION


async def create_nice_habit_select_like_action(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "create_new_like_action":
        await query.edit_message_text("Введите название нового любимого действия:")
        return CREATE_NICE_HABIT_NEW_LIKE_ACTION_NAME
    else:
        like_action_id = int(query.data.split("_")[3])
        context.user_data["nice_habit_like_action_id"] = like_action_id
        await query.edit_message_text(
            "Любимое действие выбрано. Теперь выберите локацию для приятной привычки (можно пропустить, введите '-')."
        )
        return await create_nice_habit_select_location_prompt(update, context)


async def create_nice_habit_new_like_action_name(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    action_name = update.message.text
    django_user = context.user_data["django_user"]
    like_action_exists = await sync_to_async(
        lambda: LikeAction.objects.filter(name=action_name, owner=django_user).exists()
    )()

    if like_action_exists:
        await update.message.reply_text(
            f"Любимое действие с названием '{action_name}' уже существует. Введите другое название."
        )
        return CREATE_NICE_HABIT_NEW_LIKE_ACTION_NAME
    context.user_data["new_nice_habit_like_action_name"] = action_name
    await update.message.reply_text(
        "Введите описание для нового любимого действия (необязательно, можно пропустить, введите '-'):"
    )
    return CREATE_NICE_HABIT_NEW_LIKE_ACTION_DESCRIPTION


async def create_nice_habit_new_like_action_description(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    action_description = update.message.text
    if action_description == "-":
        action_description = ""

    django_user = context.user_data["django_user"]
    action_name = context.user_data["new_nice_habit_like_action_name"]

    await sync_to_async(transaction.atomic)()

    new_action = await sync_to_async(LikeAction.objects.create)(
        name=action_name, description=action_description, owner=django_user
    )
    context.user_data["nice_habit_like_action_id"] = new_action.id
    await update.message.reply_text(
        f"Любимое действие '{new_action.name}' успешно создано и выбрано для привычки. Теперь выберите локацию."
    )
    return await create_nice_habit_select_location_prompt(update, context)


async def create_nice_habit_select_location_prompt(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    django_user = context.user_data["django_user"]

    locations = await sync_to_async(Location.objects.filter)(owner=django_user)
    locations = await sync_to_async(locations.values_list)("name", "id")
    locations = await sync_to_async(locations.all)()

    keyboard = []
    if locations:
        for name, _id in locations:
            keyboard.append(
                [InlineKeyboardButton(name, callback_data=f"select_location_{_id}")]
            )

    keyboard.append(
        [
            InlineKeyboardButton(
                "➕ Создать новую локацию", callback_data="create_new_location"
            )
        ]
    )

    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

    await update.effective_message.reply_text(
        "Выберите локацию для приятной привычки (можно пропустить, введите '-') или создайте новую:",
        reply_markup=reply_markup,
    )
    return CREATE_NICE_HABIT_SELECT_LOCATION


async def create_nice_habit_select_location(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "create_new_location":
        await query.edit_message_text("Введите название новой локации:")
        context.user_data["caller_state"] = (
            CREATE_NICE_HABIT_SELECT_LOCATION  # Чтобы знать куда вернуться
        )
        return CREATE_LOCATION_NAME  # Переиспользовать состояние создания локации
    else:
        location_id = int(query.data.split("_")[2])
        context.user_data["nice_habit_location_id"] = location_id
        await query.edit_message_text("Локация выбрана. Создаем приятную привычку...")
        return await save_nice_habit(update, context)


async def save_nice_habit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    django_user = context.user_data["django_user"]
    like_action_id = context.user_data.get("nice_habit_like_action_id")
    location_id = context.user_data.get("nice_habit_location_id")

    like_action = await sync_to_async(LikeAction.objects.get)(id=like_action_id) if like_action_id else None
    location = await sync_to_async(Location.objects.get)(id=location_id) if location_id else None
    try:
        await sync_to_async(transaction.atomic)()
        await sync_to_async(HabitNice.objects.create)(
            user=django_user,
            like_action=like_action,
            location=location,
            is_pleasant=True,  # Приятная привычка всегда pleasant
        )
        #like_action = (
        #    await LikeAction.objects.aget(id=like_action_id) if like_action_id else None
        #)
        #location = await Location.objects.aget(id=location_id) if location_id else None

        await (update.effective_message or update.message).reply_text(
            "🎉 Приятная привычка успешно создана!",
            reply_markup=ReplyKeyboardMarkup(
                MAIN_MENU_KEYBOARD, resize_keyboard=True, one_time_keyboard=False
            ),
        )
        logger.info(
            f"Создана приятная привычка для пользователя {django_user.username}: {like_action.name if like_action else 'Без действия'}"
        )

    except Exception as e:
        logger.error(
            f"Ошибка при создании приятной привычки для пользователя {django_user.username}: {e}",
            exc_info=True,
        )
        await (update.effective_message or update.message).reply_text(
            "Произошла ошибка при создании приятной привычки. Пожалуйста, попробуйте снова или свяжитесь с поддержкой.",
            reply_markup=ReplyKeyboardMarkup(
                MAIN_MENU_KEYBOARD, resize_keyboard=True, one_time_keyboard=False
            ),
        )

    return MENU


# HabitUseful
async def create_useful_habit_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    django_user = context.user_data["django_user"]

    need_actions = await sync_to_async(NeedAction.objects.filter)(owner=django_user)
    need_actions = await sync_to_async(need_actions.values_list)("name", "id")
    need_actions = await sync_to_async(need_actions.all)()

    keyboard = []
    if need_actions:
        for name, _id in need_actions:
            keyboard.append(
                [InlineKeyboardButton(name, callback_data=f"select_need_action_{_id}")]
            )

    keyboard.append(
        [
            InlineKeyboardButton(
                "➕ Создать новое нужное действие",
                callback_data="create_new_need_action",
            )
        ]
    )

    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

    await update.message.reply_text(
        "Выберите нужное действие для привычки или создайте новое:",
        reply_markup=reply_markup,
    )
    if not need_actions:  # Если нет действий, сразу предлагаем создать
        return await create_useful_habit_new_need_action_name_prompt(
            update,
            context,
            "У вас пока нет созданных нужных действий. Пожалуйста, сначала создайте его.",
        )

    return CREATE_USEFUL_HABIT_SELECT_NEED_ACTION


async def create_useful_habit_select_need_action(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "create_new_need_action":
        return await create_useful_habit_new_need_action_name_prompt(
            update, context, "Введите название нового нужного действия:"
        )
    else:
        need_action_id = int(query.data.split("_")[3])
        context.user_data["useful_habit_need_action_id"] = need_action_id
        await query.edit_message_text(
            "Действие выбрано. Теперь выберите локацию для привычки."
        )
        return await create_useful_habit_select_location_prompt(update, context)


async def create_useful_habit_new_need_action_name_prompt(
    update: Update, context: ContextTypes.DEFAULT_TYPE, prompt_text: str
) -> int:
    await (update.effective_message or update.message).reply_text(prompt_text)
    return CREATE_USEFUL_HABIT_NEW_NEED_ACTION_NAME


async def create_useful_habit_new_need_action_name(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    action_name = update.message.text
    django_user = context.user_data["django_user"]
    # Используем sync_to_async для фильтрации
    like_action_exists = await sync_to_async(lambda: NeedAction.objects.filter(name=action_name, owner=django_user).exists())()
    if like_action_exists:
        await update.message.reply_text(
            f"Нужное действие с названием '{action_name}' уже существует. Введите другое название."
        )
        return CREATE_USEFUL_HABIT_NEW_NEED_ACTION_NAME
    context.user_data["new_useful_habit_need_action_name"] = action_name
    await update.message.reply_text(
        "Введите описание для нового нужного действия (необязательно, можно пропустить, введите '-'):"
    )
    return CREATE_USEFUL_HABIT_NEW_NEED_ACTION_DESCRIPTION


async def create_useful_habit_new_need_action_description(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    action_description = update.message.text
    if action_description == "-":
        action_description = ""

    django_user = context.user_data["django_user"]
    action_name = context.user_data["new_useful_habit_need_action_name"]

    await sync_to_async(transaction.atomic)()
    new_action = await sync_to_async(NeedAction.objects.create)(
        name=action_name, description=action_description, owner=django_user
    )

    context.user_data["useful_habit_need_action_id"] = new_action.id
    await update.message.reply_text(
        f"Нужное действие '{new_action.name}' успешно создано и выбрано для привычки. Теперь выберите локацию."
    )
    return await create_useful_habit_select_location_prompt(update, context)


async def create_useful_habit_select_location_prompt(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    django_user = context.user_data["django_user"]

    locations = await sync_to_async(Location.objects.filter)(owner=django_user)
    locations = await sync_to_async(locations.values_list)('name', 'id')
    locations = await sync_to_async(locations.all)()

    keyboard = []
    if locations:
        for name, _id in locations:
            keyboard.append(
                [InlineKeyboardButton(name, callback_data=f"select_location_{_id}")]
            )

    keyboard.append(
        [
            InlineKeyboardButton(
                "➕ Создать новую локацию", callback_data="create_new_location"
            )
        ]
    )

    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

    await (
        update.effective_message or update.message
    ).reply_text(  # Отвечаем либо на query, либо на message
        "Выберите локацию для привычки (можно пропустить /skip) или создайте новую:",
        reply_markup=reply_markup,
    )
    return CREATE_USEFUL_HABIT_SELECT_LOCATION


async def create_useful_habit_select_location(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "create_new_location":
        await query.edit_message_text("Введите название новой локации:")
        context.user_data["caller_state"] = (
            CREATE_USEFUL_HABIT_SELECT_LOCATION  # Чтобы знать куда вернуться
        )
        return CREATE_LOCATION_NAME
    else:
        location_id = int(query.data.split("_")[2])
        context.user_data["useful_habit_location_id"] = location_id
        await query.edit_message_text(
            "Локация выбрана. Теперь введите время выполнения привычки в формате ЧЧ:ММ (например, 08:30)."
        )
        return CREATE_USEFUL_HABIT_SELECT_TIME


async def create_useful_habit_select_time(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    time_str = update.message.text
    time_pattern = r"^(?:2[0-3]|[01]?[0-9]):(?:[0-5]?[0-9])$"
    if not re.fullmatch(time_pattern, time_str):
        await update.message.reply_text(
            "Неверный формат времени. Пожалуйста, введите в формате ЧЧ:ММ (например, 08:30)."
        )
        return CREATE_USEFUL_HABIT_SELECT_TIME

    try:
        time_obj = datetime.datetime.strptime(time_str, "%H:%M").time()
        context.user_data["useful_habit_time_of_day"] = time_obj
        await update.message.reply_text(
            "Отлично! Теперь выберите периодичность привычки:",
            reply_markup=ReplyKeyboardMarkup(
                PERIODICITY_KEYBOARD, resize_keyboard=True, one_time_keyboard=True
            ),
        )
        return CREATE_USEFUL_HABIT_SELECT_PERIODICITY
    except ValueError:
        await update.message.reply_text(
            "Неверный формат времени. Пожалуйста, введите в формате ЧЧ:ММ (например, 08:30)."
        )
        return CREATE_USEFUL_HABIT_SELECT_TIME


async def create_useful_habit_select_periodicity(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    periodicity_text = update.message.text
    periodicity_map = {str(i): i for i in range(1, 8)}  # "1" -> 1, "7" -> 7
    periodicity_map.update(
        {
            "1 день": 1,
            "2 дня": 2,
            "3 дня": 3,
            "4 дня": 4,
            "5 дней": 5,
            "6 дней": 6,
            "7 дней": 7,
            "неделю": 7,
            "каждую неделю": 7,
        }
    )

    periodicity = periodicity_map.get(periodicity_text.lower())

    if periodicity is None:
        await update.message.reply_text(
            "Неверная периодичность. Выберите число от 1 до 7 или 'каждую неделю'."
        )
        return CREATE_USEFUL_HABIT_SELECT_PERIODICITY

    context.user_data["useful_habit_periodicity"] = periodicity

    await update.message.reply_text(
        "Что будет после выполнения привычки? Выберите 'Вознаграждение' или 'Приятную привычку':",
        reply_markup=ReplyKeyboardMarkup(
            [["🏆 Вознаграждение", "✨ Приятная привычка"]],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )
    return CREATE_USEFUL_HABIT_SELECT_REWARD_OR_NICE_HABIT


async def create_useful_habit_select_reward_or_nice_habit(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    choice = update.message.text
    django_user = context.user_data["django_user"]

    if choice == "🏆 Вознаграждение":
        rewards = await sync_to_async(Reward.objects.filter)(owner=django_user)
        rewards = await sync_to_async(rewards.values_list)('name', 'id')
        rewards = await sync_to_async(rewards.all)()

        keyboard = []
        if rewards:
            for name, _id in rewards:
                keyboard.append(
                    [InlineKeyboardButton(name, callback_data=f"select_reward_{_id}")]
                )
        keyboard.append(
            [
                InlineKeyboardButton(
                    "➕ Создать новое вознаграждение", callback_data="create_new_reward"
                )
            ]
        )
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Выберите вознаграждение или создайте новое (можно пропустить, введите '-'):",
            reply_markup=reply_markup,
        )
        return CREATE_USEFUL_HABIT_SELECT_REWARD
    elif choice == "✨ Приятная привычка":
        nice_habits = await sync_to_async(
            lambda: list(HabitNice.objects.filter(user=django_user).select_related("like_action")))()

        #nice_habits = (
        #    await HabitNice.objects.filter(user=django_user)
         #   .select_related("like_action")
        #    .aall()
        #)
        keyboard = []
        if nice_habits:
            for nh in nice_habits:
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            (
                                nh.like_action.name
                                if nh.like_action
                                else f"Приятная привычка ID:{nh.id}"
                            ),
                            callback_data=f"select_nice_habit_{nh.id}",
                        )
                    ]
                )

        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        await update.message.reply_text(
            "Выберите приятную привычку (можно пропустить, введите '-'):",
            reply_markup=reply_markup,
        )
        if not nice_habits:
            await update.message.reply_text(
                "У вас пока нет приятных привычек. Сначала создайте их или выберите 'Вознаграждение'."
            )
            return CREATE_USEFUL_HABIT_SELECT_REWARD_OR_NICE_HABIT
        return CREATE_USEFUL_HABIT_SELECT_NICE_HABIT
    else:
        await update.message.reply_text(
            "Неверный выбор. Пожалуйста, выберите 'Вознаграждение' или 'Приятную привычку'."
        )
        return CREATE_USEFUL_HABIT_SELECT_REWARD_OR_NICE_HABIT


async def create_useful_habit_select_reward(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "create_new_reward":
        await query.edit_message_text("Введите название нового вознаграждения:")
        context.user_data["caller_state"] = (
            CREATE_USEFUL_HABIT_SELECT_REWARD  # Чтобы знать куда вернуться
        )
        return CREATE_REWARD_NAME  # Переиспользовать состояние создания награды
    else:
        reward_id = int(query.data.split("_")[2])
        context.user_data["useful_habit_reward_id"] = reward_id
        context.user_data["useful_habit_nice_habit_id"] = None
        await query.edit_message_text(
            "Вознаграждение выбрано. Хотите, чтобы другие пользователи могли использовать вашу привычку? (Да/Нет)",
            reply_markup=ReplyKeyboardMarkup(
                PUBLIC_CHOICE_KEYBOARD, resize_keyboard=True, one_time_keyboard=True
            ),
        )
        return CREATE_USEFUL_HABIT_IS_PUBLIC


async def create_useful_habit_select_nice_habit(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    nice_habit_id = int(query.data.split("_")[3])
    context.user_data["useful_habit_nice_habit_id"] = nice_habit_id
    context.user_data["useful_habit_reward_id"] = None
    await query.edit_message_text(
        "Приятная привычка выбрана. Хотите, чтобы другие пользователи могли использовать вашу привычку? (Да/Нет)",
        reply_markup=ReplyKeyboardMarkup(
            PUBLIC_CHOICE_KEYBOARD, resize_keyboard=True, one_time_keyboard=True
        ),
    )
    return CREATE_USEFUL_HABIT_IS_PUBLIC


async def save_useful_habit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    is_public_choice = update.message.text.lower()
    context.user_data["useful_habit_is_public"] = is_public_choice == "да"

    django_user = context.user_data["django_user"]
    need_action_id = context.user_data.get("useful_habit_need_action_id")
    location_id = context.user_data.get("useful_habit_location_id")
    time_of_day = context.user_data.get("useful_habit_time_of_day")
    periodicity = context.user_data.get("useful_habit_periodicity")
    reward_id = context.user_data.get("useful_habit_reward_id")
    nice_habit_id = context.user_data.get("useful_habit_nice_habit_id")
    is_public = context.user_data.get("useful_habit_is_public", False)

    try:
        need_action = (
            await sync_to_async(NeedAction.objects.get)(id=need_action_id) if need_action_id else None
        )
        location = await sync_to_async(Location.objects.get)(id=location_id) if location_id else None
        reward = await sync_to_async(Reward.objects.get)(id=reward_id) if reward_id else None
        nice_habit = (
            await sync_to_async(HabitNice.objects.get)(id=nice_habit_id) if nice_habit_id else None
        )

        await sync_to_async(transaction.atomic)()
        await sync_to_async(HabitUseful.objects.create)(
            user=django_user,
            need_action=need_action,
            location=location,
            time_of_day=time_of_day,
            periodicity=periodicity,
            reward=reward,
            nice_habit=nice_habit,
            is_public=is_public,
        )

        await update.message.reply_text(
            "🎉 Полезная привычка успешно создана! Напоминания будут приходить согласно расписанию.",
            reply_markup=ReplyKeyboardMarkup(
                MAIN_MENU_KEYBOARD, resize_keyboard=True, one_time_keyboard=False
            ),
        )
        logger.info(
            f"Создана полезная привычка для пользователя {django_user.username}: {need_action.name if need_action else 'Без действия'}"
        )

    except Exception as e:
        logger.error(
            f"Ошибка при создании полезной привычки для пользователя {django_user.username}: {e}",
            exc_info=True,
        )
        await update.message.reply_text(
            "Произошла ошибка при создании полезной привычки. Пожалуйста, попробуйте снова или свяжитесь с поддержкой.",
            reply_markup=ReplyKeyboardMarkup(
                MAIN_MENU_KEYBOARD, resize_keyboard=True, one_time_keyboard=False
            ),
        )

    return MENU


class Command(BaseCommand):
    help = "Запуск Telegram бота"

    def handle(self, *args, **options):
        logger.info("Запуск Telegram бота...")
        application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

        application.add_handler(
            CommandHandler("start", start)
        )  # Start уже устанавливает django_user
        application.add_handler(CommandHandler("cancel", cancel))

        # --- Conversation Handler для создания Action, Location, Reward ---
        create_stuff_handler = ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex(r"^➕ Добавить любимое действие$"),
                    lambda u, c: check_user_and_call_next(
                        u, c, create_like_action_start
                    ),
                ),
                MessageHandler(
                    filters.Regex(r"^➕ Добавить нужное действие$"),
                    lambda u, c: check_user_and_call_next(
                        u, c, create_need_action_start
                    ),
                ),
                MessageHandler(
                    filters.Regex(r"^➕ Добавить локацию$"),
                    lambda u, c: check_user_and_call_next(u, c, create_location_start),
                ),
                MessageHandler(
                    filters.Regex(r"^➕ Добавить награду$"),
                    lambda u, c: check_user_and_call_next(u, c, create_reward_start),
                ),
            ],
            states={
                CREATE_LIKE_ACTION_NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, create_like_action_name
                    )
                ],
                CREATE_LIKE_ACTION_DESCRIPTION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, create_like_action_description
                    )
                ],
                CREATE_NEED_ACTION_NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, create_need_action_name
                    )
                ],
                CREATE_NEED_ACTION_DESCRIPTION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, create_need_action_description
                    )
                ],
                CREATE_LOCATION_NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, create_location_name
                    )
                ],
                CREATE_LOCATION_DESCRIPTION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, create_location_description
                    )
                ],
                CREATE_REWARD_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, create_reward_name)
                ],
                CREATE_REWARD_DESCRIPTION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, create_reward_description
                    )
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
            map_to_parent={MENU: MENU},
        )

        # --- Conversation Handler для создания приятной привычки (HabitNice) ---
        create_nice_habit_conv_handler = ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex(r"^✨ Создать приятную привычку$"),
                    lambda u, c: check_user_and_call_next(
                        u, c, create_nice_habit_start
                    ),
                )
            ],
            states={
                CREATE_NICE_HABIT_SELECT_LIKE_ACTION: [
                    CallbackQueryHandler(
                        lambda u, c: check_user_and_call_next(
                            u, c, create_nice_habit_select_like_action
                        )
                    )
                ],
                CREATE_NICE_HABIT_NEW_LIKE_ACTION_NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        lambda u, c: check_user_and_call_next(
                            u, c, create_nice_habit_new_like_action_name
                        ),
                    )
                ],
                CREATE_NICE_HABIT_NEW_LIKE_ACTION_DESCRIPTION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        lambda u, c: check_user_and_call_next(
                            u, c, create_nice_habit_new_like_action_description
                        ),
                    )
                ],
                CREATE_NICE_HABIT_SELECT_LOCATION: [
                    CallbackQueryHandler(
                        lambda u, c: check_user_and_call_next(
                            u, c, create_nice_habit_select_location
                        )
                    )
                ],
                CREATE_LOCATION_NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        lambda u, c: check_user_and_call_next(
                            u, c, create_location_name
                        ),
                    )
                ],
                CREATE_LOCATION_DESCRIPTION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        lambda u, c: check_user_and_call_next(
                            u, c, create_location_description
                        ),
                    )
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
            map_to_parent={MENU: MENU},
        )


        # --- Conversation Handler для создания полезной привычки (HabitUseful) ---
        create_useful_habit_conv_handler = ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex(r"^📝 Создать полезную привычку$"),
                    lambda u, c: check_user_and_call_next(
                        u, c, create_useful_habit_start
                    ),
                )
            ],
            states={
                CREATE_USEFUL_HABIT_SELECT_NEED_ACTION: [
                    CallbackQueryHandler(
                        lambda u, c: check_user_and_call_next(
                            u, c, create_useful_habit_select_need_action
                        )
                    )
                ],
                CREATE_USEFUL_HABIT_NEW_NEED_ACTION_NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        lambda u, c: check_user_and_call_next(
                            u, c, create_useful_habit_new_need_action_name
                        ),
                    )
                ],
                CREATE_USEFUL_HABIT_NEW_NEED_ACTION_DESCRIPTION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        lambda u, c: check_user_and_call_next(
                            u, c, create_useful_habit_new_need_action_description
                        ),
                    )
                ],
                CREATE_USEFUL_HABIT_SELECT_LOCATION: [
                    CallbackQueryHandler(
                        lambda u, c: check_user_and_call_next(
                            u, c, create_useful_habit_select_location
                        )
                    ),
                    MessageHandler(
                        filters.Regex(r"(?i)^/skip$"),
                        lambda u, c: check_user_and_call_next(
                            u, c, create_useful_habit_select_location_skip
                        ),
                    ),
                ],
                CREATE_USEFUL_HABIT_SELECT_TIME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        lambda u, c: check_user_and_call_next(
                            u, c, create_useful_habit_select_time
                        ),
                    )
                ],
                CREATE_USEFUL_HABIT_SELECT_PERIODICITY: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        lambda u, c: check_user_and_call_next(
                            u, c, create_useful_habit_select_periodicity
                        ),
                    )
                ],
                CREATE_USEFUL_HABIT_SELECT_REWARD_OR_NICE_HABIT: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        lambda u, c: check_user_and_call_next(
                            u, c, create_useful_habit_select_reward_or_nice_habit
                        ),
                    )
                ],
                CREATE_USEFUL_HABIT_SELECT_REWARD: [
                    CallbackQueryHandler(
                        lambda u, c: check_user_and_call_next(
                            u, c, create_useful_habit_select_reward
                        )
                    )
                ],
                CREATE_USEFUL_HABIT_SELECT_NICE_HABIT: [
                    CallbackQueryHandler(
                        lambda u, c: check_user_and_call_next(
                            u, c, create_useful_habit_select_nice_habit
                        )
                    )
                ],
                CREATE_USEFUL_HABIT_IS_PUBLIC: [
                    MessageHandler(
                        filters.Regex("^(Да|Нет)$"),
                        lambda u, c: check_user_and_call_next(u, c, save_useful_habit),
                    )
                ],
                CREATE_REWARD_NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        lambda u, c: check_user_and_call_next(u, c, create_reward_name),
                    )
                ],
                CREATE_REWARD_DESCRIPTION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        lambda u, c: check_user_and_call_next(
                            u, c, create_reward_description
                        ),
                    )
                ],
                CREATE_LOCATION_NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        lambda u, c: check_user_and_call_next(
                            u, c, create_location_name
                        ),
                    )
                ],
                CREATE_LOCATION_DESCRIPTION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        lambda u, c: check_user_and_call_next(
                            u, c, create_location_description
                        ),
                    )
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
            map_to_parent={MENU: MENU},
        )

        application.add_handler(create_stuff_handler)
        application.add_handler(create_nice_habit_conv_handler)
        application.add_handler(create_useful_habit_conv_handler)
        application.add_handler(
            MessageHandler(filters.Text(["📊 Мои привычки", "⚙️ Настройки"]), main_menu)
        )
        # Default handler для сообщений, которые не были обработаны
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)
        )

        logger.info("Telegram бот запущен.")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        logger.info("Telegram бот остановлен.")


async def create_useful_habit_select_location_skip(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await (update.effective_message or update.message).reply_text(
        "Вы пропустили выбор локации. Теперь введите время выполнения привычки в формате ЧЧ:ММ (например, 08:30)."
    )
    context.user_data["useful_habit_location_id"] = None
    return CREATE_USEFUL_HABIT_SELECT_TIME
