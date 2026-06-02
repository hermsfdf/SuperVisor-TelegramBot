import os
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def script_browse_kb(path: str):

	kb = []

	for item in os.listdir(path):
		full = os.path.join(path, item)

		if os.path.isdir(full):
			kb.append([InlineKeyboardButton(text=f"📁 {item}",	callback_data=f"dir:{item}")])

		elif item.endswith(".py"):
			kb.append([InlineKeyboardButton(text=f"📄 {item}", callback_data=f"select_file:{item}")])

	parent = os.path.dirname(path)

	if parent != path:
		kb.append([InlineKeyboardButton( text="⬅️ Back", callback_data="back")])

	return InlineKeyboardMarkup(inline_keyboard=kb)

def script_replace(path: str):
	return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⌨️ Replace File", callback_data=f"replace_script:{path}")]])

def scripts_keyboard(scripts: List[str]):

	kb = []

	for i, s in enumerate(scripts):

		name = os.path.basename(s)

		kb.append([
			InlineKeyboardButton(
				text=f"📄 {name}",
				callback_data=f"file:{i}"
			)
		])

	kb.append([
		InlineKeyboardButton(
			text="⚙️ Settings",
			callback_data="settings_use"
		)
	])

	return InlineKeyboardMarkup(inline_keyboard=kb)

def add_file_browse_kb(path: str):

	kb = []

	for item in os.listdir(path):
		full = os.path.join(path, item)


		if os.path.isdir(full):
			kb.append([InlineKeyboardButton(text=f"📁 {item}",	callback_data=f"dir:{item}")])

	parent = os.path.dirname(path)

	if parent != path:
		kb.append([InlineKeyboardButton( text="⬅️ Back", callback_data="back")])
		kb.append([InlineKeyboardButton(text="✅ Выбрать эту папку", callback_data="select_this_folder")])

	return InlineKeyboardMarkup(inline_keyboard=kb)
