from telebot import types
import uuid
import logging

logger = logging.getLogger(__name__)

def generate_markup(current, path, shared_key=None):
    markup = types.InlineKeyboardMarkup()

    # Кнопка "Вверх", если мы не в корне
    if path:
        callback_data = "up" if not shared_key else f"shared_up:{shared_key}"
        markup.add(types.InlineKeyboardButton("⬆️ Вверх", callback_data=callback_data))

    # Кнопки для папок
    for folder in current["folders"]:
        callback_data = f"folder:{folder}" if not shared_key else f"shared_folder:{shared_key}:{folder}"
        markup.add(types.InlineKeyboardButton(f"📁 {folder}", callback_data=callback_data))

    # Кнопки для файлов
    for idx, file in enumerate(current["files"], start=1):
        display_name = {
            "text": f"📝 Текст {idx}",
            "document": f"📄 Документ {idx}",
            "photo": f"🖼️ Фото {idx}",
            "video": f"🎬 Видео {idx}",
            "audio": f"🎵 Аудио {idx}"
        }.get(file["type"], f"📁 Файл {idx}")

        short_id = file.get("short_id")
        if not short_id:
            logger.error(f"Файл без short_id: {file}")
            continue

        callback_data = f"file:{short_id}" if not shared_key else f"shared_file:{shared_key}:{short_id}"
        markup.add(types.InlineKeyboardButton(display_name, callback_data=callback_data))

    # Кнопка "Вернуть Все"
    callback_data = "retrieve_all" if not shared_key else f"shared_retrieve_all:{shared_key}"
    markup.add(types.InlineKeyboardButton("📤 Вернуть Все", callback_data=callback_data))

    return markup