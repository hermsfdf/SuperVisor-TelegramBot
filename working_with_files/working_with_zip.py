import zipfile, os

from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import TOKEN

from states.states_with_file import FileState
from config import ADMIN_ID

bot = Bot(token=TOKEN)

BASE_PATH = os.getcwd()
file_router = Router()

@file_router.callback_query(F.data == "get_zip")
async def get_zip_file(call: CallbackQuery, state: FSMContext):
	if ADMIN_ID != call.from_user.id:
		return
	await state.set_state(FileState.wait_zip_file)

	await call.message.edit_text("📤 Отправь ZIP архив.")
	await call.answer()

@file_router.message(FileState.wait_zip_file, F.document)
async def zip_handler(message: Message, state: FSMContext, bot):
	if ADMIN_ID != message.from_user.id:
		return
		
	document = message.document

	folder_name = os.path.splitext(document.file_name)[0]
	save_dir = os.path.join(BASE_PATH, folder_name)

	os.makedirs(save_dir, exist_ok=True)

	#путь куда сохраняем zip
	zip_path = os.path.join(save_dir, document.file_name)

	#кккачиваем файл
	file = await bot.get_file(document.file_id)
	await bot.download_file(file.file_path, destination=zip_path)

	#распаковка
	with zipfile.ZipFile(zip_path, 'r') as zip_ref:
		zip_ref.extractall(save_dir)

	await state.update_data(zip_folder=save_dir)

	await message.answer(f"📦 ZIP распакован в папку:{folder_name}")