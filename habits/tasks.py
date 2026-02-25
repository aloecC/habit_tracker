import datetime
import logging
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from smtplib import SMTPException
from telegram import Bot
from telegram.error import TelegramError
import html
from .models import HabitUseful

logger = logging.getLogger(__name__)
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)


@shared_task(bind=True, default_retry_delay=300, max_retries=5)
def send_habit_reminder(self):
    """
    Отложенная задача для отправки напоминаний о полезных привычках в Telegram.
    """
    try:
        now = timezone.localtime(timezone.now())
        today = now.date()
        current_time_for_comparison = now.time().replace(second=0, microsecond=0)

        habits_to_check = HabitUseful.objects.filter(
            time_of_day__hour=current_time_for_comparison.hour,
            time_of_day__minute=current_time_for_comparison.minute
        )

        if not habits_to_check.exists():
            logger.debug(f"[{now}] Нет привычек для отправки напоминаний в Telegram в {current_time_for_comparison}.")
            return

        for habit in habits_to_check:
            try:
                days_passed = (today - habit.created_at).days

                if days_passed % habit.periodicity == 0:
                    user = habit.user

                    chat_id = None
                    if hasattr(user, 'telegram_chat_id') and user.telegram_chat_id:  # Если поле прямо на User
                        chat_id = user.telegram_chat_id

                    if not chat_id:
                        logger.warning(
                            f"[{now}] Нет Telegram Chat ID для пользователя {user.username} (ID привычки: {habit.id}). Пропускаем.")
                        continue

                    # Экранируем имя пользователя и название действия для безопасности
                    safe_username = html.escape(user.username)
                    safe_action = html.escape(habit.action.name if habit.action else 'Без действия')

                    message_parts = [
                        f"<b>Привет, {safe_username}!</b>",
                        f"Напоминание: пора выполнить привычку '<b>{safe_action}</b>'.",
                        f"📍 <b>Место:</b> {habit.location.name if habit.location else 'не указано'}.",
                        f"⏰ <b>Время:</b> {habit.time_of_day.strftime('%H:%M')}"
                    ]

                    if habit.reward:
                        message_parts.append(f"🏆 <b>Твоя награда:</b> {habit.reward.name}")
                    elif habit.nice_habit:
                        message_parts.append(f"✨ <b>Затем можно:</b> {habit.nice_habit.action.name}")

                    message = "\n".join(message_parts)

                    # Отправка сообщения через Telegram Bot API
                    # Используем parse_mode='HTML' для форматирования
                    bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode='HTML'
                    )
                    logger.info(f"[{now}] Напоминание в Telegram успешно отправлено для привычки ID: {habit.id}, Пользователю: {user.username} (Chat ID: {chat_id})")

            except TelegramError as e: # Ловим специфические ошибки Telegram
                logger.error(f"[{now}] Ошибка Telegram API для привычки ID: {habit.id}, Пользователь: {user.username}. Ошибка: {e}")
                self.retry(exc=e) # Повторяем задачу, если это сетевая проблема или временная ошибка API
            except Exception as e:
                # Любая другая непредвиденная ошибка
                logger.error(f"[{now}] Непредвиденная ошибка при обработке привычки ID: {habit.id}. Ошибка: {e}", exc_info=True)

    except Exception as e:
        # Глобальная ошибка (например, проблемы с БД)
        logger.critical(f"[{now}] Глобальная ошибка в задаче send_habit_reminder: {e}", exc_info=True)
