import socket
import time



class BaseModule:
    RECV_LEN = 1024
    BEEP_MESSAGE = bytearray([255, 65, 1, 1, 255])
    
    def __init__(self, s: socket.socket):
        self.socket = s
        pass

    def _send(self, message: bytearray, sleep_time: float):
        try:
            self.socket.sendall(message)
        except socket.error as e:
            print(f"Ошибка сокета: {e}")
        time.sleep(sleep_time)
        
    def _get_respone(self) -> bytes:
        try:
            data = self.s.recv(RECV_LEN)
            if not data:
                print(f"Данные от сокета не пришли: {e}")
                
            return data
        except socket.error as e:
            print(f"Ошибка сокета: {e}")
            

    def __send_command(self, command: bytearray) -> bool:
        try:
            print(f"Отправка команды: {command}")
            # Отправляем команду
            self.socket.sendall(command)

            # Добавляем небольшой задержку между отправками команд
            time.sleep(0.5)

            return True
        except socket.error as e:
            print(f"Ошибка сокета: {e}")
            return False