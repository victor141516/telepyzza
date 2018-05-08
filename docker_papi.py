import docker
from docker_jr import Pyterpreted
from apistar import App, Route, http
import os
import requests
import subprocess
import threading
import telebot
import time


TG_TOKEN = os.environ['TG_TOKEN']
DOCKER_NETWORK = os.environ['DOCKER_NETWORK']
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', False)
DOCKER_CONTAINER_NAME_PREFIX = 'docker_jr_'
client = docker.from_env()
bot = telebot.TeleBot(TG_TOKEN)
interpreters = {}


def update_message(promt_message, interpreter, bot):
    output = interpreter.get_output()
    message = ''
    for each in output:
        if each is None:
            continue
        message = f'{message}\n\n{each["result"]}'
        bot.edit_message_text(
            f'```{message}```',
            message_id=promt_message.message_id,
            chat_id=promt_message.chat.id,
            parse_mode='Markdown')


def show_loader(promt_message, interpreters, bot):
    while True:
        for x in range(0, 3):
            if promt_message.chat.id in interpreters:
                bot.edit_message_text(
                    '`>>>`',
                    message_id=promt_message.message_id,
                    chat_id=promt_message.chat.id,
                    parse_mode='Markdown')
                return
            time.sleep(0.5)
            try:
                bot.edit_message_text(
                    f'`{" " * x}.`',
                    message_id=promt_message.message_id,
                    chat_id=promt_message.chat.id,
                    parse_mode='Markdown')
            except telebot.apihelper.ApiException:
                pass


@bot.message_handler(commands=['start'])
def start_interpreter(message):
    promt_message = bot.send_message(message.chat.id, '`.`', parse_mode='Markdown')
    loader = threading.Thread(target=show_loader, args=(promt_message, interpreters, bot))
    loader.start()

    container_name = f'{DOCKER_CONTAINER_NAME_PREFIX}{message.chat.id}'
    try:
        container = client.containers.get(container_name)
        print(f'{container_name} - Container already exists')
    except docker.errors.NotFound:
        print(f'{container_name} - Container doesn\'t exists')
        subprocess.run(['docker', 'run', '-dit', '--network', DOCKER_NETWORK, '--name', container_name, 'python:3-alpine', 'python'])
        container = client.containers.get(container_name)
        print(f'{container_name} - Container created')
    container.stop()

    print(f'{container_name} - Creating interpreter')
    interpreters[message.chat.id] = Pyterpreted(f'docker start -ia {container_name}')
    print(f'{container_name} - Interpreted creater')
    print(f'{container_name} - Waiting for loader to stop')
    loader.join()
    print(f'{container_name} - Loader end')
    print(f'{container_name} - Begin interpreter')
    t = threading.Thread(target=update_message, args=(promt_message, interpreters[message.chat.id], bot))
    t.start()


@bot.message_handler(commands=['pip'])
def pip_manage(message):
    max_message_size = 4096
    container_name = f'{DOCKER_CONTAINER_NAME_PREFIX}{message.chat.id}'
    available_pip_commands_with_packages = ['install', 'uninstall']
    available_pip_commands_without_packages = ['list']
    raw_command = message.text.split()[1:]

    action = raw_command[0]
    if action not in available_pip_commands_with_packages + available_pip_commands_without_packages:
        bot.reply_to(message, f'pip available commands are: {", ".join(available_pip_commands_with_packages + available_pip_commands_without_packages)}')
        return

    packages = ' '.join(raw_command[1:])
    if any([operator in packages for operator in ['&&', '||', ';']]):
        bot.reply_to(message, f'Oh you!')
        return

    if action in available_pip_commands_with_packages:
        if action == 'uninstall':
            output = subprocess.check_output(['docker', 'exec', container_name, 'pip', action, '-y', ] + packages.split()).decode('utf-8')
        else:
            output = subprocess.check_output(['docker', 'exec', container_name, 'pip', action, ] + packages.split()).decode('utf-8')
        splitted_messages = [output[i:i+max_message_size] for i in range(0, len(output), max_message_size)]
        for each in splitted_messages:
            bot.reply_to(message, f'```{each}```', parse_mode='Markdown')
        return

    if action in available_pip_commands_without_packages:
        output = subprocess.check_output(['docker', 'exec', container_name, 'pip', action]).decode('utf-8')
        splitted_messages = [output[i:i+max_message_size] for i in range(0, len(output), max_message_size)]
        for each in splitted_messages:
            bot.reply_to(message, f'```{each}```', parse_mode='Markdown')
        return


@bot.message_handler(func=lambda m: True)
def run_python_line(message):
    if message.chat.id not in interpreters:
        bot.reply_to(message, 'Send /start first')
    else:
        if interpreters[message.chat.id].add_command(message.text) is False:
            bot.reply_to(message, f'Max {interpreters[message.chat.id].max_queued_commands} commands queued reached')
            return

        try:
            bot.delete_message(message.chat.id, message.message_id)
        except telebot.apihelper.ApiException:
            pass


def route_to_jr(user_path, request: http.Request):
    pieces = user_path.split('/')
    chat_id = pieces[0]
    container_name = f'{DOCKER_CONTAINER_NAME_PREFIX}{chat_id}'
    path = f'/{"/".join(pieces[1:])}'
    print(f'http://{container_name}{path}')
    requests_response = requests.request(request.method, f'http://{container_name}{path}', headers=dict(request.headers), data=request.body)
    return http.Response(requests_response.text, headers=requests_response.headers)


def set_webhook():
    webhook = bot.get_webhook_info()
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + "/bot")
    return '!'


routes = [
    Route('/', method='GET', handler=set_webhook),
    Route('/u/{+user_path}', method='GET', handler=route_to_jr),
]
app = App(routes=routes)

if WEBHOOK_URL is False:
    bot.polling(none_stop=True, interval=0, timeout=20)
    app.serve('0.0.0.0', 8000)
