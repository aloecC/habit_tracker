import logging
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove, Update)
from telegram.ext import (Application, ApplicationBuilder,
                          CallbackQueryHandler, CommandHandler, ContextTypes,
                          ConversationHandler, MessageHandler, filters)

from bot_app.views import (CREATE_LIKE_ACTION_DESCRIPTION,
                           CREATE_LIKE_ACTION_NAME,
                           CREATE_LOCATION_DESCRIPTION, CREATE_LOCATION_NAME,
                           CREATE_NEED_ACTION_DESCRIPTION,
                           CREATE_NEED_ACTION_NAME,
                           CREATE_NICE_HABIT_NEW_LIKE_ACTION_DESCRIPTION,
                           CREATE_NICE_HABIT_NEW_LIKE_ACTION_NAME,
                           CREATE_NICE_HABIT_SELECT_LIKE_ACTION,
                           CREATE_NICE_HABIT_SELECT_LOCATION,
                           CREATE_REWARD_DESCRIPTION, CREATE_REWARD_NAME,
                           CREATE_USEFUL_HABIT_IS_PUBLIC,
                           CREATE_USEFUL_HABIT_NEW_NEED_ACTION_DESCRIPTION,
                           CREATE_USEFUL_HABIT_NEW_NEED_ACTION_NAME,
                           CREATE_USEFUL_HABIT_SELECT_LOCATION,
                           CREATE_USEFUL_HABIT_SELECT_NEED_ACTION,
                           CREATE_USEFUL_HABIT_SELECT_NICE_HABIT,
                           CREATE_USEFUL_HABIT_SELECT_PERIODICITY,
                           CREATE_USEFUL_HABIT_SELECT_REWARD,
                           CREATE_USEFUL_HABIT_SELECT_REWARD_OR_NICE_HABIT,
                           CREATE_USEFUL_HABIT_SELECT_TIME, MENU, VIEW_HABITS,
                           cancel, check_user_and_call_next,
                           create_like_action_description,
                           create_like_action_name, create_like_action_start,
                           create_location_description, create_location_name,
                           create_location_start,
                           create_need_action_description,
                           create_need_action_name, create_need_action_start,
                           create_nice_habit_conv_handler,
                           create_nice_habit_new_like_action_description,
                           create_nice_habit_new_like_action_name,
                           create_nice_habit_select_like_action,
                           create_nice_habit_select_location,
                           create_nice_habit_start, create_reward_description,
                           create_reward_name, create_reward_start,
                           create_stuff_handler,
                           create_useful_habit_conv_handler,
                           create_useful_habit_new_need_action_description,
                           create_useful_habit_new_need_action_name,
                           create_useful_habit_select_location,
                           create_useful_habit_select_location_skip,
                           create_useful_habit_select_need_action,
                           create_useful_habit_select_nice_habit,
                           create_useful_habit_select_periodicity,
                           create_useful_habit_select_reward,
                           create_useful_habit_select_reward_or_nice_habit,
                           create_useful_habit_select_time,
                           create_useful_habit_start, get_django_habits,
                           logger, main_menu, save_useful_habit, start)


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
