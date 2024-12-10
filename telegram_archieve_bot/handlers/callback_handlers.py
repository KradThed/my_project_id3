from telebot.types import CallbackQuery
from utils.data_manager import load_data, save_data, init_user
from utils.navigation import navigate_to_path
from utils.keyboards import generate_markup
import telebot
import logging

logger = logging.getLogger(__name__)

def register_callback_handlers(bot: telebot.TeleBot):
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call: CallbackQuery):
        user_id = str(call.message.chat.id)
        data = load_data()
        init_user(data, user_id)

        if call.data == "up":
            # Код для перехода на уровень выше
            if data["users"][user_id]["current_path"]:
                popped = data["users"][user_id]["current_path"].pop()
                bot.answer_callback_query(call.id, f"Вернулись из папки '{popped}'.")
            else:
                bot.answer_callback_query(call.id, "Вы уже в корневой папке.")
        elif call.data.startswith("folder:"):
            # Код для перехода в другую папку
            folder_name = call.data.split(":", 1)[1]
            current = navigate_to_path(data["users"][user_id]["structure"], data["users"][user_id]["current_path"])
            if folder_name in current["folders"]:
                data["users"][user_id]["current_path"].append(folder_name)
                bot.answer_callback_query(call.id, f"Перешли в папку '{folder_name}'.")
            else:
                bot.answer_callback_query(call.id, "Папка не найдена.")
        elif call.data.startswith("file:"):
            # Код для получения файла по short_id
            short_id = call.data.split(":", 1)[1]
            file_info = None
            for file in navigate_to_path(data["users"][user_id]["structure"], data["users"][user_id]["current_path"])["files"]:
                if file.get("short_id") == short_id:
                    file_info = file
                    break
            if not file_info:
                bot.answer_callback_query(call.id, "Файл не найден.")
                return
            # Отправляем файл
            try:
                if file_info["type"] == "text":
                    bot.send_message(call.message.chat.id, file_info["content"])
                elif file_info["type"] == "document":
                    bot.send_document(call.message.chat.id, file_info["file_id"])
                elif file_info["type"] == "photo":
                    bot.send_photo(call.message.chat.id, file_info["file_id"])
                elif file_info["type"] == "video":
                    bot.send_video(call.message.chat.id, file_info["file_id"])
                elif file_info["type"] == "audio":
                    bot.send_audio(call.message.chat.id, file_info["file_id"])
                bot.answer_callback_query(call.id, "Файл отправлен.")
            except Exception as e:
                logger.error(f"Ошибка при отправке файла: {e}")
                bot.answer_callback_query(call.id, f"Ошибка при отправке файла: {str(e)}")
        elif call.data == "retrieve_all":
            # Код для получения всех файлов в текущей папке
            current = navigate_to_path(data["users"][user_id]["structure"], data["users"][user_id]["current_path"])
            try:
                for file in current["files"]:
                    if file["type"] == "text":
                        bot.send_message(call.message.chat.id, f"Текст: {file['content']}")
                    elif file["type"] == "document":
                        bot.send_document(call.message.chat.id, file["file_id"])
                    elif file["type"] == "photo":
                        bot.send_photo(call.message.chat.id, file["file_id"])
                    elif file["type"] == "video":
                        bot.send_video(call.message.chat.id, file["file_id"])
                    elif file["type"] == "audio":
                        bot.send_audio(call.message.chat.id, file["file_id"])
                    else:
                        bot.send_message(call.message.chat.id, "Неизвестный тип файла.")
                bot.answer_callback_query(call.id, "Все файлы отправлены.")
            except Exception as e:
                logger.error(f"Ошибка при отправке файлов: {e}")
                bot.answer_callback_query(call.id, f"Ошибка при отправке файлов: {str(e)}")
        else:
            bot.answer_callback_query(call.id, "Неизвестная команда.")

        # Обновляем папочную структуру после действия, если это необходимо
        if call.data.startswith("folder:") or call.data == "up":
            current = navigate_to_path(data["users"][user_id]["structure"], data["users"][user_id]["current_path"])
            markup = generate_markup(current, data["users"][user_id]["current_path"])
            try:
                bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                              message_id=call.message.message_id,
                                              reply_markup=markup)
            except telebot.apihelper.ApiTelegramException as e:
                if "message is not modified" in str(e):
                    # Игнорируем ошибку, если сообщение не изменилось
                    pass
                else:
                    logger.error(f"Ошибка обновления клавиатуры: {e}")
                    bot.send_message(call.message.chat.id, f"Ошибка обновления клавиатуры: {str(e)}")

        save_data(data)