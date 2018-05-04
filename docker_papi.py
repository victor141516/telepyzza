import docker
from docker_jr import Pyterpreted
import os
import subprocess
import threading
import telebot


TG_TOKEN = os.environ['TG_TOKEN']
DOCKER_CONTAINER_NAME_PREFIX = 'docker_jr_'
client = docker.from_env()
bot = telebot.TeleBot(TG_TOKEN)
interpreters = {}


def update_message(message, interpreter):
    messages = interpreter.get_output()
    for message in messages:
        bot.edit_message(message.id, message.text + message)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    container_name = f'{DOCKER_CONTAINER_NAME_PREFIX}{message.from_user.id}'
    try:
        container = client.containers.get(container_name)
    except docker.errors.NotFound:
        subprocess.run(['docker', 'run', '-dit', '--name', container_name, 'python:3-alpine', 'python'])
        container = client.containers.get(container_name)

    interpreters[message.from_user.id] = Pyterpreted(f'docker start -ia {container_name}')
    t = threading.Thread(target=update_message, args=(message.id, interpreters['container_name'], bot))
    t.start()


@bot.message_handler(func=lambda m: True)
def run_python_line(message):
    interpreters[message.from_user.id].add_command(message.text)

bot.polling()
