import pytest
import os

from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler

# Настройки Django для тестов
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


try:
    import django

    django.setup()

except ImportError:
    pass


class MockReward:
    def __init__(self, id, description, name, owner):
        self.id = id
        self.name = name
        self.description = description
        self.owner = owner


class MockNeedAction:
    def __init__(self, id, description, name, owner):
        self.id = id
        self.name = name
        self.description = description
        self.owner = owner


class MockLikeAction:
    def __init__(self, id, description, name, owner):
        self.id = id
        self.name = name
        self.description = description
        self.owner = owner


class MockLocation:
    def __init__(self, id, description, name, owner):
        self.id = id
        self.name = name
        self.description = description
        self.owner = owner


@pytest.fixture
def django_user(db):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(username='testuser', password='password')


class MockTelegramUser:
    def __init__(self, id, username):
        self.id = id
        self.username = username


@pytest.fixture
def mock_telegram_user():
    return MockTelegramUser(id=123456789, username="test_user")


@pytest.fixture
def mock_chat_id():
    return 987654321


# Fixture для симуляции контекста пользователя
class MockUserData:
    def __init__(self):
        self._data = {}

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __setitem__(self, key, value):
        self._data[key] = value

    def pop(self, key, default=None):
        return self._data.pop(key, default)


@pytest.fixture
def mock_context(mock_telegram_user, mock_chat_id):
    class MockContext:
        def __init__(self):
            self.user_data = MockUserData()
            self.args = []
            self.bot_data = {}
            self.chat_data = {}
            self.chat = MockChat(chat_id=mock_chat_id)
            self.user = mock_telegram_user

    class MockChat:
        def __init__(self, chat_id):
            self.id = chat_id

    return MockContext()


# Fixture для симуляции Update объекта
class MockUpdate:
    def __init__(self, message=None, callback_query=None, effective_user=None, effective_message=None):
        self.message = message
        self.callback_query = callback_query
        self.effective_user = effective_user
        self.effective_message = effective_message
        self.update_id = 12345


class MockMessage:
    def __init__(self, chat_id, text=None, from_user=None):
        self.chat_id = chat_id
        self.text = text
        self.from_user = from_user
        self.message_id = 1

    async def reply_text(self, text, reply_markup=None, parse_mode=None):
        print(f"[MockReply] {text}")  # Simulate sending a message
        return MockMessage(chat_id=self.chat_id, text=text)  # Simulate returned message object


class MockCallbackQuery:
    def __init__(self, data, from_user, message, chat_id):
        self.data = data
        self.from_user = from_user
        self.message = message
        self.id = "123"
        self.chat_id = chat_id

    async def answer(self, text=None, show_alert=False):
        print(f"[MockCallbackAnswer] {text if text else 'Answered'}")
        pass

    async def edit_message_text(self, text, reply_markup=None, parse_mode=None):
        print(f"[MockEditMessage] {text}")
        pass


@pytest.fixture
def mock_update(mock_telegram_user, mock_chat_id):
    message = MockMessage(chat_id=mock_chat_id, from_user=mock_telegram_user, text="Some text")
    return MockUpdate(message=message, effective_user=mock_telegram_user, effective_message=message)


@pytest.fixture
def mock_callback_query(mock_telegram_user, mock_chat_id):
    message = MockMessage(chat_id=mock_chat_id, from_user=mock_telegram_user)
    callback_query = MockCallbackQuery(data="test_data", from_user=mock_telegram_user, message=message,
                                       chat_id=mock_chat_id)
    return MockUpdate(callback_query=callback_query, effective_user=mock_telegram_user, effective_message=message)


async def call_handler(handler, update, context):
    if hasattr(handler, 'handle_update'):
        return await handler.handle_update(None, update, context)
    elif isinstance(handler, CommandHandler):
        return await handler.callback(update, context)
    elif isinstance(handler, MessageHandler):
        return await handler.callback(update, context)
    elif isinstance(handler, CallbackQueryHandler):
        return await handler.callback(update, context)
    else:
        return await handler(update, context)


from bot_app.views import create_useful_habit_conv_handler, create_nice_habit_conv_handler, create_stuff_handler, start

@pytest.fixture
def test_app():

    return {
        "create_useful_habit_conv_handler": create_useful_habit_conv_handler,
        "create_nice_habit_conv_handler": create_nice_habit_conv_handler,
        "create_stuff_handler": create_stuff_handler,
        "start_handler": CommandHandler("start", start)     }
