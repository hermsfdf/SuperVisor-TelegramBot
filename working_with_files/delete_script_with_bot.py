import json
import os

from aiogram import F, Router
from aiogram.types import CallbackQuery

from kernel import stop_script

from keyboard.keyboard import script_disable 

from config import ADMIN_ID

del_script_from_bot = Router()

def load_scripts():
	if os.path.exists("script.json"):
		with open("script.json", "r", encoding="utf-8") as f:
			return json.load(f)
	return []


@del_script_from_bot.callback_query(F.data == "delete_script_from_bot")
async def show_delete_menu(call: CallbackQuery):
	if ADMIN_ID != call.from_user.id:
		return

	autoscripts = load_scripts()
	
	if not autoscripts:
		await call.answer("Список скриптов пуст!", show_alert=True)
		return

	text = "🗑 <b>Выберите скрипт для удаления:</b>\n\n" + "\n".join([f"<code>{s}</code>" for s in autoscripts])

	await call.message.edit_text(
		text, 
		parse_mode="html", 
		reply_markup=script_disable(autoscripts)
	)
	await call.answer()


@del_script_from_bot.callback_query(F.data.startswith("delete_script:"))
async def process_delete_script(call: CallbackQuery):
	if ADMIN_ID != call.from_user.id:
		return

	index = int(call.data.split(":")[1])

	autoscripts = load_scripts()

	if index < 0 or index >= len(autoscripts):
		await call.message.answer("⚠️ Скрипт не найден в списке.")
		await call.answer()
		return

	script = autoscripts[index]

	del autoscripts[index]

	with open("script.json", "w", encoding="utf-8") as file:
		json.dump(autoscripts, file, ensure_ascii=False, indent=4)

	await call.message.answer(f"✅ Успешно удалено из базы бота:\n<code>{script}</code>", parse_mode="html")
	await call.answer()
	
	await stop_script(script)