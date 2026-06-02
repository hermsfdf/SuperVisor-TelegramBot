import asyncio
import os
import json
import sys
import tracemalloc

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from aiogram.client.telegram import TelegramAPIServer

from kernel import (
	start_supervisor,
	stats,
	manual_stopped,
	start_script,
	stop_script,
	restart_script,
)

from keyboard.keyboard import (
	scripts_keyboard, 
	scripts_keyboard_menu, 
	script_settings
)
from config import TOKEN, ADMIN_ID

# Импорты роутеров
from working_with_files.add_script_to_bot import script_to_bot
from working_with_files.upload_new_files import upload_router
from working_with_files.addition_new_script import new_script_router
from working_with_files.delete_script_with_bot import del_script_from_bot
from working_with_files.read_scripts import read_router
from working_with_files.working_with_zip import file_router
from working_with_files.replace_with_file import replace_router

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

tracemalloc.start()

# local_server = TelegramAPIServer.from_base_url("http://localhost:8081")  
# (используется для отправки файлов до 2 ГБ, не обязательно / used to send files up to 2 GB, not required)

# Локальный сервер Telegram (если поднят свой API сервер)

bot = Bot(token=TOKEN)
# Добавляем после токена: / Add after the token:
# session=AiohttpSession(api=local_server)
# ТОЛЬКО ЕСЛИ ВЫ ПОДНЯЛИ СВОЙ ЛОКАЛЬНЫЙ СЕРВЕР / ONLY if you have set up your own local Telegram server.

dp = Dispatcher()
main_router = Router()

def load_scripts():
	if os.path.exists("script.json"):
		with open("script.json", "r", encoding="utf-8") as f:
			return json.load(f)
	return []

@main_router.message(Command("start"))
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

@main_router.callback_query(F.data == "cmd_start")
async def cmd_start_info(call: CallbackQuery):
	if ADMIN_ID != call.from_user.id:
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

	await call.message.edit_text(
		text,
		parse_mode="html",
		reply_markup=scripts_keyboard(autoscripts)
	)

@main_router.callback_query(F.data == "settings_use")
async def settings_call(call: CallbackQuery):
	if ADMIN_ID != call.from_user.id:
		return

	text = "📊 <b>Settings</b>\n\n"

	await call.message.edit_text(
		text,
		parse_mode="html",
		reply_markup=script_settings()
	)

# --- START / STOP / RESTART

@main_router.callback_query(F.data.startswith("start:"))
async def start_cb(call: CallbackQuery):
	if ADMIN_ID != call.from_user.id:
		return

	index = int(call.data.split(":")[1])
	autoscripts = load_scripts()

	if index < 0 or index >= len(autoscripts):
		await call.answer("Скрипт не найден")
		return

	script = autoscripts[index]
	manual_stopped.discard(script)
	await start_script(script)
	await call.answer("Started")

@main_router.callback_query(F.data.startswith("stop:"))
async def stop_cb(call: CallbackQuery):
	if ADMIN_ID != call.from_user.id:
		return

	index = int(call.data.split(":")[1])
	autoscripts = load_scripts()

	if index < 0 or index >= len(autoscripts):
		await call.answer("Скрипт не найден")
		return

	script = autoscripts[index]
	await stop_script(script)
	await call.answer("Stopped")

@main_router.callback_query(F.data.startswith("restart:"))
async def restart_cb(call: CallbackQuery):
	if ADMIN_ID != call.from_user.id:
		return

	index = int(call.data.split(":")[1])
	autoscripts = load_scripts()

	if index < 0 or index >= len(autoscripts):
		await call.answer("Скрипт не найден")
		return

	script = autoscripts[index]
	await restart_script(script)
	await call.answer("Restarted")

@main_router.callback_query(F.data.startswith("file:"))
async def file_cb(call: CallbackQuery):
	if ADMIN_ID != call.from_user.id:
		return

	index = int(call.data.split(":")[1])
	autoscripts = load_scripts()
	
	if index < 0 or index >= len(autoscripts):
		await call.answer("Скрипт не найден")
		return

	script = autoscripts[index]
	st = stats.get(script)

	if not st:
		await call.answer("Нет информации")
		return

	text = (
		f"📄 <b>{script}</b>\n\n"
		f"Status: {st['status']}\n"
		f"PID: {st['pid']}\n"
		f"Tech Restarts: {st['tech_restarts']}\n"
		f"Auto Restarts: {st['auto_restarts']}\n"
		f"Last Error: {st['last_error']}"
	)

	await call.message.answer(
		text,
		parse_mode="html",
		reply_markup=scripts_keyboard_menu(index)
	)

async def notify(text: str):
	await bot.send_message(ADMIN_ID, text)

async def main():
	#Подключаем роутеры
	routers = [
		script_to_bot,
		new_script_router,
		del_script_from_bot,
		read_router,
		file_router,
		replace_router,
		upload_router,
		main_router
	]
	
	for router in routers:
		dp.include_router(router)

	#Передаем актуальный список при запуске
	autoscripts = load_scripts()
	asyncio.create_task(
		start_supervisor(autoscripts, notify)
	)

	print("[SUPERVISOR STARTED]")
	await dp.start_polling(bot)

if __name__ == "__main__":
	try:
		asyncio.run(main())
	finally:
		tracemalloc.stop()