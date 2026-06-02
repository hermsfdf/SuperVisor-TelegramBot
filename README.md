# SuperVisor-TelegramBot
Реализовал инструмент управления ботами для полноценного управление Python-скриптами через Telegram Bot.
Он подходит если вам нужно быстро получить информацию со своего удаленного сервера (VPS, VDS) на ОС Windows и/или (и да я знаю что линукс это ядро) Linux. (MacOS не тестировал)

По пунктам:
- Создаёте бот через @BotFather
- Берете токен и вставляете его в config.py (TOKEN = 'Ваш токен')
- После копируете свой Telegram_id через бота @FIND_MY_ID_BOT / Кастомный клиент Telegram. И его вставляете в ADMIN_ID без скобок.
- После запуска супервайзера в созданном боте отправляем /start боту, чтобы подключить скрипты заходим в settings (ниже расписаны кнопки для добавления) скрипты можно подключать из любой директории.

Возможности Супервайзера:
- Просмотр через бота работу скрипта (возможные ошибки, статус)
- Быстрый запуск большого количества скриптов. Добавляйте скрипты через бота кнопкой "Add a script to the bot".
- Создание новой папки и добавление нужного скрипта в нее через кнопку Create Folder and Add File.
- Добавление файлов с расширением json, session, py в любую папку на системе через кнопку Add File to Folder.
- Удаление скрипта с базы бота (не будет подлежать замене, запуском/перезапуском и автозапуску, удаляется из системы управления) через кнопку Remove the script from the bot
- Распаковка ZIP-архива в папку с bot.py. Чтобы отправлять архивы больше двух МБ нужно иметь свой telegram-bot-api (Локальный сервер тг) https://github.com/tdlib/telegram-bot-api, в коде показан пример как подвязать сервер к боту.


I have implemented a tool for managing bots that provides full control over Python scripts via a Telegram Bot.
It is suitable if you need quick access to information from your remote server (VPS, VDS) on Windows and/or Linux OS (and yes, I know Linux is a kernel). (macOS not tested)

Steps:
- Create a bot via @BotFather
- Get the token and paste it into config.py (TOKEN = 'Your token')
-  Then copy your Telegram ID using @FIND_MY_ID_BOT or a custom Telegram client and insert it into ADMIN_ID without brackets
After starting the supervisor, send /start to your bot. To connect scripts, go to settings (button list is described below). Scripts can be connected from any directory
Supervisor features:
- View script status and logs via the bot (possible errors, status)
- Quick launch of multiple scripts. Add scripts using the "Add a script to the bot" button
- Create a new folder and add a script to it using the "Create Folder and Add File" button
- Add files with extensions .json, .session, .py to any folder on the system using the "Add File to Folder" button
- Remove a script from the bot database (it will no longer be subject to replacement, startup/restart, and autostart; it is removed from the management system) using the "Remove the script from the bot" button
- Unpack ZIP archives into the folder with bot.py. To send archives larger than 2 MB, you need your own Telegram Bot API (local Telegram server): https://github.com/tdlib/telegram-bot-api. The code includes an example of how to connect the bot to a local server.
