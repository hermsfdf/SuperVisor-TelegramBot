import json
import os

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from kernel import start_script, stats
from states.states_with_file import FileState
from keyboard.keyboard_files import script_browse_kb, scripts_keyboard

from config import ADMIN_ID

BASE_PATH = os.getcwd()
script_to_bot = Router()

def load_scripts():
	if os.path.exists("script.json"):
		with open("script.json", "r", encoding="utf-8") as f:
			return json.load(f)
	return []

@script_to_bot.callback_query(F.data == "add_to_bot")
async def add_auto_scripts(call: CallbackQuery, state: FSMContext):
	if ADMIN_ID != call.from_user.id:
		return

	await state.update_data(path=BASE_PATH)
	await state.set_state(FileState.script_browse)
	
	await call.message.answer(
		"Выберите файл или папку:", 
		reply_markup=script_browse_kb(BASE_PATH)
	)
	await call.answer()

@script_to_bot.message(Command("start"))
async def cmd_info(message: Message):
	if ADMIN_ID != message.from_user.id:
		return

	autoscripts = load_scripts()
	text = "📊 <b>Supervisor Status</b>\n\n"

	for s in autoscripts:
		if s not in stats:
			continue
		st = stats[s]
		text += (
			f"📄 <b>{s}</b>\n"
			f"Status: {st['status']}\n"
			f"PID: {st['pid']}\n"
			f"Tech Restarts: {st['tech_restarts']}\n"
			f"Auto Restarts: {st['auto_restarts']}\n"
			f"Last Error: {st['last_error']}\n\n"
		)

	await message.answer(
		text,
		parse_mode="html",
		reply_markup=scripts_keyboard(autoscripts)
	)

#xtндлер для клика по папке
@script_to_bot.callback_query(FileState.script_browse, F.data.startswith("dir:"))
async def browse_dir_callback(call: CallbackQuery, state: FSMContext):
	if ADMIN_ID != call.from_user.id:
		return

	data = await state.get_data()
	current_path = data.get("path", BASE_PATH)
	
	dir_name = call.data.split(":")[1]
	new_path = os.path.join(current_path, dir_name)
	
	if os.path.isdir(new_path):
		await state.update_data(path=new_path)
		await call.message.edit_text(
			f"Текущая папка: {os.path.basename(new_path)}",
			reply_markup=script_browse_kb(new_path)
		)
	await call.answer()

@script_to_bot.callback_query(FileState.script_browse, F.data == "back")
async def browse_back_callback(call: CallbackQuery, state: FSMContext):
	if ADMIN_ID != call.from_user.id:
		return
	data = await state.get_data()
	current_path = data.get("path", BASE_PATH)
	
	parent_path = os.path.dirname(current_path)
	
	await state.update_data(path=parent_path)
	await call.message.edit_text(
		f"Текущая папка: {os.path.basename(parent_path) or parent_path}",
		reply_markup=script_browse_kb(parent_path)
	)
	await call.answer()

@script_to_bot.callback_query(FileState.script_browse, F.data.startswith("select_file:"))
async def browse_file_callback(call: CallbackQuery, state: FSMContext):
	if ADMIN_ID != call.from_user.id:
		return

	data = await state.get_data()
	current_path = data.get("path", BASE_PATH)
	
	file_name = call.data.split(":")[1]
	full_path = os.path.join(current_path, file_name)
	
	autoscripts = load_scripts()
	
	if full_path not in autoscripts:
		autoscripts.append(full_path)
		
		with open("script.json", "w", encoding="utf-8") as f:
			json.dump(autoscripts, f, ensure_ascii=False, indent=4)
			
		await call.message.edit_text(f"✅ Добавлен и запущен: {full_path}")
		await start_script(full_path)
	else:
		await call.message.edit_text("⚠️ Этот скрипт уже есть в списке.")
		
	await call.answer()
	await state.clear()

@script_to_bot.message(FileState.script_browse)
async def script_browse(message: Message, state: FSMContext):
	if ADMIN_ID != message.from_user.id:
		return
	
	data = await state.get_data()
	path = data.get("path", BASE_PATH)

	name = message.text
	full_path = os.path.join(path, name)
	
	autoscripts = load_scripts()

	if os.path.isdir(full_path):
		files = []
		for item in os.listdir(full_path):
			item_path = os.path.join(full_path, item)
			if os.path.isdir(item_path):
				files.append(f"📁 {item}")
			elif item.endswith(".py"):
				files.append(f"📄 {item}")

		await state.update_data(path=full_path)
		await message.answer("\n".join(files))
		return

	if name.endswith(".py"):
		if full_path not in autoscripts:
			autoscripts.append(full_path)
			with open("script.json", "w", encoding="utf-8") as f:
				json.dump(autoscripts, f, ensure_ascii=False, indent=4)

			await message.answer(f"Добавлен: {full_path}")
			await start_script(full_path)
		else:
			await message.answer("Уже есть")

		await state.clear()