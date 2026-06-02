from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import TOKEN

from states.states_with_file import FileState

from config import ADMIN_ID

bot = Bot(token=TOKEN)

replace_router = Router()

@replace_router.callback_query(F.data.startswith("replace_script:"))
async def replace_file(call: CallbackQuery, state: FSMContext):
	if ADMIN_ID != call.from_user.id:
		return

	path = call.data.split("replace_script:")[1]

	await state.update_data(target_path=path)
	await state.set_state(FileState.wait_file_replace)
	if call.message.from_user.is_bot and call.message.text:
		await call.message.edit_text("📤 Отправь новый .py файл для замены")
	else:
		await call.message.answer("📤 Отправь новый .py файл для замены")
	await call.answer()


@replace_router.message(FileState.wait_file_replace, F.document)
async def upload_file_to_replace(message: Message, state: FSMContext, bot: Bot):
	if ADMIN_ID != message.from_user.id:
		return
		
	data = await state.get_data()
	target_path = data.get("target_path")

	file_name = message.document.file_name

	if not file_name.endswith(".py"):
		await message.answer("Только .py файлы")
		return

	if not target_path:
		await message.answer("Ошибка: файл не выбран")
		await state.clear()
		return

	await bot.download(
		message.document,
		destination=target_path
	)

	await message.answer(f"✅ Файл заменен:\n{target_path}")

	await state.clear()