from aiogram.fsm.state import State, StatesGroup

class FileState(StatesGroup):
	wait_file_replace = State()
	wait_zip_file = State()
	wait_folder_name = State()
	wait_sending_script = State()
	script_browse = State()
	select_upload_folder = State()
	wait_sending_script = State()
	wait_send_file = State()
