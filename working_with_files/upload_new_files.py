import os

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboard.keyboard_files import add_file_browse_kb
from states.states_with_file import FileState

from config import ADMIN_ID

BASE_PATH = os.getcwd()

upload_router = Router()

@upload_router.callback_query(F.data == "upload_script")
async def upload_script(call: CallbackQuery, state: FSMContext):
	if ADMIN_ID != call.from_user.id:
		return

	await state.update_data(path=BASE_PATH)
	await state.set_state(FileState.select_upload_folder)

	await call.message.answer("📁 Выберите папку для загрузки .py файла:", reply_markup=add_file_browse_kb(BASE_PATH))

	await call.answer()

@upload_router.callback_query(FileState.select_upload_folder, F.data.startswith("dir:"))
async def open_dir(call: CallbackQuery, state: FSMContext):
	if ADMIN_ID != call.from_user.id:
		return

	data = await state.get_data()
	current_path = data["path"]

	folder = call.data.split(":", 1)[1]
	new_path = os.path.join(current_path, folder)

	if os.path.isdir(new_path):
		await state.update_data(path=new_path)

		await call.message.edit_text(
			f"📁 {new_path}",
			reply_markup=add_file_browse_kb(new_path)
		)

	await call.answer()

@upload_router.callback_query(FileState.select_upload_folder, F.data == "back")
async def go_back(call: CallbackQuery, state: FSMContext):
	if ADMIN_ID != call.from_user.id:
		return

	data = await state.get_data()
	current_path = data["path"]

	parent = os.path.dirname(current_path)

	if not parent:
		parent = BASE_PATH
	await state.update_data(path=parent)

	await call.message.edit_text(f"📁 {parent}", reply_markup=add_file_browse_kb(parent))

	await call.answer()

@upload_router.callback_query(FileState.select_upload_folder, F.data == "select_this_folder")
async def select_folder(call: CallbackQuery, state: FSMContext):
	if ADMIN_ID != call.from_user.id:
		return

	data = await state.get_data()

	await state.set_state(FileState.wait_send_file)

	await call.message.edit_text(
		f"📤 Отправь .py файл\n\n📁 Папка: {data['path']}"
	)

	await call.answer()

@upload_router.message(FileState.wait_send_file, F.document)
async def upload_file(message: Message, state: FSMContext):
	if ADMIN_ID != message.from_user.id:
		return
		
	data = await state.get_data()
	path = data.get("path")

	if not path:
		await message.answer("❌ Сначала выбери папку")
		return

	file_name = message.document.file_name

	if not (file_name.endswith(".py") or file_name.endswith(".session") or file_name.endswith(".json")):
		await message.answer("❌ Разрешены только .py, .session, .json")
		return


	os.makedirs(path, exist_ok=True)

	await message.bot.download(
		message.document,
		destination=os.path.join(path, file_name)
	)

	await message.answer(f"✅ Файл сохранен:\n📄 {file_name}\n📁 {path}")

	await state.clear()