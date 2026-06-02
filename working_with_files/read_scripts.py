import os, json

from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from kernel import script_read
from keyboard.keyboard_files import script_replace

from config import TOKEN, ADMIN_ID

bot = Bot(token=TOKEN)

BASE_PATH = os.getcwd()
read_router = Router()

def load_scripts():
    if os.path.exists("script.json"):
        with open("script.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@read_router.callback_query(F.data.startswith("read_file:"))
async def read_function(call: CallbackQuery):
	if ADMIN_ID != call.from_user.id:
		return

	index = int(call.data.split(":")[1])

	AUTOSCRIPTS = load_scripts()

	if index < 0 or index >= len(AUTOSCRIPTS):
		await call.message.answer("Файл не найден")
		return

	script_path = AUTOSCRIPTS[index]

	text = await script_read(script_path)

	if len(text) <= 4000:
		await call.message.answer(
			f"```\n{text}\n```",
			reply_markup=script_replace(script_path),
			parse_mode="Markdown"
		)
		return

	file_name = os.path.basename(script_path).replace(".py", "_read.txt")
	tmp_path = os.path.join(BASE_PATH, file_name)

	with open(tmp_path, "w", encoding="utf-8") as f:
		f.write(text)

	await call.message.answer_document(
		FSInputFile(tmp_path),
		reply_markup=script_replace(script_path)
	)