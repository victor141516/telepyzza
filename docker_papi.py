import docker
from docker_jr import Pyterpreted
import os
import subprocess
import threading
import telebot
import time


TG_TOKEN = os.environ['TG_TOKEN']
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

    container_name = f'{DOCKER_CONTAINER_NAME_PREFIX}{message.from_user.id}'
    try:
        container = client.containers.get(container_name)
        print(f'{container_name} - Container already exists')
    except docker.errors.NotFound:
        print(f'{container_name} - Container doesn\'t exists')
        subprocess.run(['docker', 'run', '-dit', '--name', container_name, 'python:3-alpine', 'python'])
        container = client.containers.get(container_name)
        print(f'{container_name} - Container created')
    container.stop()

    print(f'{container_name} - Creating interpreter')
    interpreters[message.from_user.id] = Pyterpreted(f'docker start -ia {container_name}')
    print(f'{container_name} - Interpreted creater')
    print(f'{container_name} - Waiting for loader to stop')
    loader.join()
    print(f'{container_name} - Loader end')
    print(f'{container_name} - Begin interpreter')
    t = threading.Thread(target=update_message, args=(promt_message, interpreters[message.from_user.id], bot))
    t.start()


@bot.message_handler(func=lambda m: True)
def run_python_line(message):
    if message.from_user.id not in interpreters:
        bot.reply_to(message, 'Send /start first')
    else:
        interpreters[message.from_user.id].add_command(message.text)

bot.polling()
