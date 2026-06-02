import os

from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


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


def script_disable(scripts: List[str]):

	kb = []

	for i, s in enumerate(scripts):

		name = os.path.basename(s)

		kb.append([
			InlineKeyboardButton(
				text=f"🗑 {name}",
				callback_data=f"delete_script:{i}"
			)
		])

	return InlineKeyboardMarkup(inline_keyboard=kb)



def script_replace_kb(path: str):

	kb = []

	for item in os.listdir(path):

		full = os.path.join(path, item)

		if os.path.isdir(full):

			kb.append([
				InlineKeyboardButton(
					text=f"📁 {item}",
					callback_data=f"dir:{item}"
				)
			])

		elif item.endswith(".py"):

			kb.append([
				InlineKeyboardButton(
					text=f"📄 {item}",
					callback_data=f"select_file_replace:{item}"
				)
			])

	parent = os.path.dirname(path)

	if parent != path:
		kb.append([
			InlineKeyboardButton(
				text="⬅️ Back",
				callback_data="back"
			)
		])

	return InlineKeyboardMarkup(inline_keyboard=kb)

def script_settings():

	return InlineKeyboardMarkup(inline_keyboard=[
		[
			InlineKeyboardButton(
				text="➕ Add a script to the bot",
				callback_data="add_to_bot"
			)
		],
		[		
		InlineKeyboardButton(
			text="➕ Add file to folder",
			callback_data="upload_script"
			)
		],
		[
			InlineKeyboardButton(
				text="📁 Create Folder and Add File",
				callback_data="adding_folder_name"
			)
		],
		[
			InlineKeyboardButton(
				text="⛔ Remove the script from the bot",
				callback_data="delete_script_from_bot"
			)
		],
		[
			InlineKeyboardButton(
				text="📝 Extracting zip",
				callback_data="get_zip"
			)
		],
		[
			InlineKeyboardButton(
				text="⬅️ Back to manager",
				callback_data="cmd_start"
			)
		]
	])

def scripts_keyboard_menu(index: int):

	return InlineKeyboardMarkup(inline_keyboard=[

		[
			InlineKeyboardButton(
				text="▶️ Start",
				callback_data=f"start:{index}"
			),

			InlineKeyboardButton(
				text="⛔ Stop",
				callback_data=f"stop:{index}"
			)
		],

		[
			InlineKeyboardButton(
				text="🔄 Restart",
				callback_data=f"restart:{index}"
			)
		],

		[
			InlineKeyboardButton(
				text="📖 Read File",
				callback_data=f"read_file:{index}"
			)
		]
	])