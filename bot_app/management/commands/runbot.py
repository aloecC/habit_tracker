import os
import logging
from django.core.management.base import BaseCommand
from telegram.ext import ApplicationBuilder
from django.conf import settings
from django.core.management.base import BaseCommand

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot_app.views import (
    MENU,
    CREATE_REWARD_DESCRIPTION,
    cancel,
    create_reward_description,
    logger,
    start,
    check_user_and_call_next,
    get_django_habits,
    create_like_action_start,
    create_need_action_start,
    create_location_start,
    create_reward_start,
    VIEW_HABITS,
    CREATE_LIKE_ACTION_NAME,
    CREATE_LIKE_ACTION_DESCRIPTION,
    CREATE_NEED_ACTION_NAME,
    create_like_action_description,
    create_like_action_name,
    create_need_action_name,
    create_need_action_description,
    CREATE_NEED_ACTION_DESCRIPTION,
    create_location_name,
    CREATE_LOCATION_NAME,
    CREATE_REWARD_NAME,
    create_reward_name,
    create_nice_habit_start,
    CREATE_NICE_HABIT_SELECT_LIKE_ACTION,
    create_nice_habit_select_like_action,
    CREATE_NICE_HABIT_NEW_LIKE_ACTION_NAME,
    create_nice_habit_new_like_action_name,
    CREATE_NICE_HABIT_NEW_LIKE_ACTION_DESCRIPTION,
    create_nice_habit_new_like_action_description,
    CREATE_NICE_HABIT_SELECT_LOCATION,
    create_nice_habit_select_location,
    CREATE_LOCATION_DESCRIPTION,
    create_location_description,
    create_useful_habit_start,
    CREATE_USEFUL_HABIT_SELECT_NEED_ACTION,
    create_useful_habit_select_need_action,
    CREATE_USEFUL_HABIT_NEW_NEED_ACTION_NAME,
    create_useful_habit_new_need_action_name,
    CREATE_USEFUL_HABIT_NEW_NEED_ACTION_DESCRIPTION,
    create_useful_habit_new_need_action_description,
    CREATE_USEFUL_HABIT_SELECT_LOCATION,
    create_useful_habit_select_location,
    create_useful_habit_select_location_skip,
    CREATE_USEFUL_HABIT_SELECT_TIME,
    CREATE_USEFUL_HABIT_SELECT_PERIODICITY,
    create_useful_habit_select_time,
    create_useful_habit_select_periodicity,
    CREATE_USEFUL_HABIT_SELECT_REWARD_OR_NICE_HABIT,
    create_useful_habit_select_reward_or_nice_habit,
    CREATE_USEFUL_HABIT_SELECT_REWARD,
    create_useful_habit_select_reward,
    CREATE_USEFUL_HABIT_SELECT_NICE_HABIT,
    create_useful_habit_select_nice_habit,
    CREATE_USEFUL_HABIT_IS_PUBLIC,
    save_useful_habit,
    main_menu,
    create_stuff_handler,
    create_nice_habit_conv_handler,
    create_useful_habit_conv_handler,
)


class Command(BaseCommand):
    help = "Запуск Telegram бота"

    def handle(self, *args, **options):
        logger.info("Запуск Telegram бота...")
        application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

        application.add_handler(
            CommandHandler("start", start)
        )  # Start уже устанавливает django_user
        application.add_handler(CommandHandler("cancel", cancel))

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
