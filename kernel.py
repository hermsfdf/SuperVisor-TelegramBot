import asyncio
import sys
import json
import os
import time
from collections import defaultdict, deque

from config import RESTART_LIMIT, RESTART_WINDOW, CHECK_DELAY

processes = {}
tasks = defaultdict(list)
manual_stopped = set()

restart_history = defaultdict(deque)

stats = defaultdict(lambda: {
	"status": "stopped",
	"pid": None,
	"started_at": None,
	"last_crash": None,
	"tech_restarts": 0,
	"auto_restarts": 0,
	"last_error": None
})

os.makedirs("logs", exist_ok=True)


def write_json_log(script: str, data: dict):
	safe_name = script.replace(":", "_").replace("\\", "_").replace("/", "_")
	path = f"logs/{safe_name}.json"

	with open(path, "a", encoding="utf-8") as f:
		f.write(json.dumps(data, ensure_ascii=False) + "\n")


def log_event(script: str, status: str, auto=False, error=None):
	data = {
		"Script": script,
		"Status": status,
		"Time": time.strftime("%Y-%m-%d %H:%M:%S"),
		"PID": stats[script]["pid"],
		"Tech_Restarts": stats[script]["tech_restarts"],
		"Auto_Restarts": stats[script]["auto_restarts"],
		"AutoRestart": auto,
		"Error": error
	}

	write_json_log(script, data)


async def stream_reader(stream, script, stream_type):
	while True:
		line = await stream.readline()
		if not line:
			break

		text = line.decode(errors="ignore").rstrip()

		write_json_log(script, {
			"Script": script,
			"Type": stream_type,
			"Time": time.strftime("%Y-%m-%d %H:%M:%S"),
			"Message": text
		})

		if stream_type == "stderr":
			stats[script]["last_error"] = text

		print(f"[{script}][{stream_type}] {text}")


async def start_script(script: str):
	if script in processes:
		proc = processes[script]
		if proc.returncode is None:
			return

	if not os.path.exists(script):
		print(f"[ERROR] File not found: {script}")
		return

	proc = await asyncio.create_subprocess_exec(
		sys.executable,
		script,
		stdout=asyncio.subprocess.PIPE,
		stderr=asyncio.subprocess.PIPE
	)

	processes[script] = proc

	stats[script]["status"] = "running"
	stats[script]["pid"] = proc.pid
	stats[script]["started_at"] = time.time()

	manual_stopped.discard(script)

	log_event(script, "STARTED")

	tasks[script].extend([
		asyncio.create_task(stream_reader(proc.stdout, script, "stdout")),
		asyncio.create_task(stream_reader(proc.stderr, script, "stderr"))
	])

	print(f"[START] {script} PID={proc.pid}")

def script_read(script_path: str):
	with open(script_path, "r", encoding="utf-8") as f:
		return f.read()
		
async def stop_script(script: str):
	proc = processes.get(script)

	manual_stopped.add(script)

	if not proc:
		return

	if proc.returncode is None:
		proc.terminate()

		try:
			await asyncio.wait_for(proc.wait(), timeout=10)
		except asyncio.TimeoutError:
			proc.kill()

	stats[script]["status"] = "stopped"

	log_event(script, "STOPPED")

	processes.pop(script, None)

	for t in tasks.get(script, []):
		t.cancel()

	tasks[script] = []

	print(f"[STOP] {script}")


async def restart_script(script: str, auto=False):
	await stop_script(script)
	await asyncio.sleep(1)

	if auto:
		stats[script]["auto_restarts"] += 1
	else:
		stats[script]["tech_restarts"] += 1

	log_event(script, "RESTART", auto=auto)

	await start_script(script)


async def monitor_script(script: str, notify_func=None):
	while True:

		if script in manual_stopped:
			await asyncio.sleep(CHECK_DELAY)
			continue

		proc = processes.get(script)

		if not proc:
			await start_script(script)
			await asyncio.sleep(CHECK_DELAY)
			continue

		try:
			await asyncio.wait_for(proc.wait(), timeout=0.1)
		except asyncio.TimeoutError:
			await asyncio.sleep(CHECK_DELAY)
			continue

		code = proc.returncode

		stats[script]["status"] = "crashed"
		stats[script]["last_crash"] = time.time()

		error = stats[script]["last_error"]

		log_event(script, f"CRASHED (code={code})", auto=True, error=error)

		print(f"[CRASH] {script} CODE={code}")

		now = time.time()
		history = restart_history[script]

		while history and now - history[0] > RESTART_WINDOW:
			history.popleft()

		history.append(now)

		if len(history) >= RESTART_LIMIT:
			stats[script]["status"] = "FAILED_LIMIT"

			log_event(script, "DISABLED (too many crashes)", auto=True)

			restart_history.pop(script, None)
			manual_stopped.add(script)

			if notify_func:
				try:
					await notify_func(
						f"❌ {script} отключён (слишком много падений)"
					)
				except:
					pass

			continue

		backoff = min(2 ** len(history), 30)
		await asyncio.sleep(backoff)

		await restart_script(script, auto=True)


async def start_supervisor(scripts: list[str], notify_func=None):
	for script in scripts:
		await start_script(script)

		task = asyncio.create_task(
			monitor_script(script, notify_func)
		)

		tasks[script].append(task)
