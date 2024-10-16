import sys
import os
import keyboard

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from move import Move

import socket
import time

host = "192.168.2.106"

port = 2055

# Создаем сокет
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f"Соединение с {host}:{port}")

# Устанавливаем соединение
s.connect((host, port))
move = Move(s.dup())


def on_press_w():
    move.forward()
    print("Нажата клавиша W")

def on_press_a():
    move.left()
    print("Нажата клавиша A")

def on_press_s():
    move.back()
    print("Нажата клавиша S")

def on_press_d():
    move.right()
    print("Нажата клавиша D")

def on_release():
    move.stop()
    print("Клавиша отпущена")

# Регистрация обработчиков нажатий
keyboard.on_press_key('w', lambda _: on_press_w())
keyboard.on_press_key('a', lambda _: on_press_a())
keyboard.on_press_key('s', lambda _: on_press_s())
keyboard.on_press_key('d', lambda _: on_press_d())

# Регистрация обработчиков отпусканий
keyboard.on_release_key('w', lambda _: on_release())
keyboard.on_release_key('a', lambda _: on_release())
keyboard.on_release_key('s', lambda _: on_release())
keyboard.on_release_key('d', lambda _: on_release())

# Запуск прослушивателя
keyboard.wait()

s.close()
print("Соединение закрыто")
