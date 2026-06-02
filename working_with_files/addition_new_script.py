import os

from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.states_with_file import FileState

from config import TOKEN, ADMIN_ID

bot = Bot(token=TOKEN)

new_script_router = Router()

@new_script_router.callback_query(F.data == "adding_folder_name")
async def create_folder_name(call: CallbackQuery, state: FSMContext):
	if ADMIN_ID != call.from_user.id:
		return

	await state.set_state(FileState.wait_folder_name)

	await call.message.edit_text("📤 Отправь название новой папки")
	await call.answer()

@new_script_router.message(FileState.wait_folder_name)
async def get_file_name(message: Message, state: FSMContext):
	if ADMIN_ID != message.from_user.id:
		return

	name_text = message.text
	os.mkdir(name_text)

	await state.update_data(folder_name=name_text)
	await state.set_state(FileState.wait_sending_script)

	await message.answer(f"Папка {name_text} - создана. Отправь файл .py")
 
@new_script_router.message(FileState.wait_sending_script, F.document)
async def upload_file_to_file(message: Message, state: FSMContext):
	if ADMIN_ID != message.from_user.id:
		return

	data = await state.get_data()
	name_text = data.get("folder_name")

	file_name = message.document.file_name
	os.makedirs(name_text, exist_ok=True)

	await bot.download(message.document, destination=os.path.join(name_text, file_name))

	await message.answer(f"{file_name} сохранен в {name_text}")

	await state.clear()