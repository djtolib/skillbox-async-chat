#
# Серверное приложение для соединений
#
import asyncio
from asyncio import transports
Users = []
Messages = []


class ServerProtocol(asyncio.Protocol):
    login: str = None
    server: 'Server'
    transport: transports.Transport

    def __init__(self, server: 'Server'):
        self.server = server

    def data_received(self, data: bytes):
        decoded = data.decode()
        decoded.replace("\r\n", "")
        if self.login is not None:
            self.send_message(decoded)
        else:
            if decoded.startswith("login:"):
                self.login = decoded.replace("login:", "")
                if self.login not in Users:
                    Users.append(self.login)
                    self.transport.write(
                        f"Привет, {self.login}!\n".encode()
                    )
                    if len(Messages) != 0:
                        sep = "\n"
                        self.transport.write("Ранее обсуждалось:\n"
                                             f"{sep.join(Messages)}".encode())
                else:
                    self.login = ""
                    self.transport.write("Логин занят. Выберите другой логин. \n"
                                         "P.S. Кто первым встал, у того и тапки) \n".encode())
            else:
                self.transport.write("Неправильный логин\n".encode())

    def connection_made(self, transport: transports.Transport):
        self.server.clients.append(self)
        self.transport = transport
        print("Пришел новый клиент")

    def connection_lost(self, exception):
        if self.login in Users:
            Users.remove(self.login)
        self.server.clients.remove(self)
        print("Клиент вышел")

    def send_message(self, content: str):
        message = f"{self.login}: {content}\n"
        print("cont:"+message)
        Messages.append(message)
        if len(Messages) > 10:
            Messages.pop(0)
        for user in self.server.clients:
            user.transport.write(message.encode())


class Server:
    clients: list

    def __init__(self):
        self.clients = []

    def build_protocol(self):
        return ServerProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.build_protocol,
            '127.0.0.1',
            8888
        )

        print("Сервер запущен ...")

        await coroutine.serve_forever()


process = Server()

try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("Сервер остановлен вручную")
