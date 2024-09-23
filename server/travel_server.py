import socket
import sys
import threading
import json
from travel import Travel, TravelSegment
from user import User



def get_local_ip():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except Exception as e:
        sys.stderr.write(f"Erro ao obter o IP: {e}\n")
        sys.exit(1)

ip = get_local_ip()
print(f"O IP local da máquina é: {ip}")

class TravelServer:
    def __init__(self, host=ip, port=5000):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(5)
        print(f"Server started on {host}:{port}")

        segments = [
            TravelSegment('Belém', 'Fortaleza', 3),
            TravelSegment('Fortaleza', 'São Paulo', 3),
            TravelSegment('São Paulo', 'Curitiba', 3),
        ]
        self.travel = Travel(segments)
        self.users = {}
        self.sessions = {}
        self.user_sessions = {}

    def handle_client(self, client_socket):
        session_token = None
        try:
            while True:
                try:
                    request = client_socket.recv(1024).decode('utf-8')
                    if not request:
                        break
                    request_data = json.loads(request)
                    session_token = request_data.get("session_token")
                    response_data = self.process_request(request_data)
                    response = json.dumps(response_data)
                    client_socket.send(response.encode('utf-8'))
                except ConnectionResetError:
                    print(f"Conexão perdida com o cliente {session_token}, possivelmente fechado inesperadamente.")
                    break
                except json.JSONDecodeError:
                    print("Erro ao decodificar o JSON. Ignorando mensagem corrompida.")
        except Exception as e:
            print(f"Erro no manuseio do cliente: {e}")
        finally:
            if session_token:
                self.logout_user_by_token(session_token)
            client_socket.close()
            print(f"Conexão fechada para o cliente {session_token}")

    def process_request(self, request_data):
        command = request_data.get("command")
        if command == "REGISTER":
            return self.register_user(request_data)
        elif command == "LOGIN":
            return self.login_user(request_data)
        elif command == "LOGOUT":
            return self.logout_user(request_data)
        elif command in ["LIST", "RESERVE", "CANCEL", "CONFIRM"]:
            session_token = request_data.get("session_token")
            if self.validate_session(session_token):
                if command == "LIST":
                    return self.list_travels(session_token)
                elif command == "RESERVE":
                    return self.reserve_seat(request_data)
                elif command == "CANCEL":
                    return self.cancel_reservation(request_data)
                elif command == "CONFIRM":
                    return self.confirm_reservation(request_data)
            else:
                return {"status": "error", "message": "Ação não permitida. Usuário não logado."}
        else:
            return {"status": "error", "message": "UNKNOWN COMMAND"}

    def register_user(self, data):
        username = data["username"]
        name = data["name"]
        password = data["password"]

        if username in self.users:
            return {"status": "error", "message": "Usuário já registrado."}

        user = User(username, name, password)
        user.register()
        self.users[username] = user
        session_token = self.create_session(username)
        return {"status": "success", "message": f"Usuário {username} registrado e logado com sucesso.", "session_token": session_token}

    def login_user(self, data):
        username = data["username"]
        password = data["password"]

        user = self.users.get(username)
        if not user:
            return {"status": "error", "message": "Usuário não encontrado."}

        if username in self.user_sessions:
            return {"status": "error", "message": "Usuário já está logado em outro dispositivo."}

        if user.login(password):
            session_token = self.create_session(username)
            return {"status": "success", "message": f"Login bem-sucedido para {username}.", "session_token": session_token}
        return {"status": "error", "message": "Falha no login."}

    def create_session(self, username):
        session_token = f"{username}_session_token"
        self.sessions[session_token] = username
        self.user_sessions[username] = session_token
        return session_token

    def validate_session(self, session_token):
        return session_token in self.sessions

    def logout_user(self, data):
        session_token = data.get("session_token")
        self.logout_user_by_token(session_token)

    def logout_user_by_token(self, session_token):
        username = self.sessions.pop(session_token, None)
        if username:
            self.user_sessions.pop(username, None)
            print(f"Usuário {username} deslogado e sessão {session_token} removida.")

    def list_travels(self, session_token):
        username = self.sessions.get(session_token)
        user = self.users.get(username)
        if not user:
            return {"status": "error", "message": "Usuário não encontrado."}
        return {"status": "success", "travels": self.travel.list_all_seats(), "travels_values": self.travel.list_all_values(), "confirm_list":self.travel.list_seats_for_confirmation(user), "final_list":self.travel.list_all_final_seats(user)}

    def reserve_seat(self, data):
        username = self.sessions.get(data["session_token"])
        seat_number = int(data["seat_number"])
        segment_indices = data["segment_indices"]

        user = self.users.get(username)
        if not user:
            return {"status": "error", "message": "Usuário não encontrado."}

        if self.travel.reserve_seat(user, seat_number, segment_indices):
            return {"status": "success", "message": f"Assento {seat_number} reservado temporariamente para {username}. Confirme em 30 segundos."}
        else:
            return {"status": "error", "message": f"Falha ao reservar assento {seat_number} nos trechos especificados."}

    def confirm_reservation(self, data):
        username = self.sessions.get(data["session_token"])
        seat_number = int(data["seat_number"])
        segment_indices = data["segment_indices"]

        user = self.users.get(username)
        if not user:
            return {"status": "error", "message": "Usuário não encontrado."}
        print(user)
        if self.travel.confirm(user, seat_number, segment_indices):
            return {"status": "success", "message": f"Reserva do assento {seat_number} confirmada para {username} nos trechos especificados."}
        return {"status": "error", "message": f"Falha ao confirmar a reserva do assento {seat_number} nos trechos especificados."}

    def cancel_reservation(self, data):
        username = self.sessions.get(data["session_token"])
        seat_number = int(data["seat_number"])
        segment_indices = data["segment_indices"]

        user = self.users.get(username)
        if not user:
            return {"status": "error", "message": "Usuário não encontrado."}

        if self.travel.cancel_reservation(seat_number, segment_indices, user):
            return {"status": "success", "message": f"Reserva do assento {seat_number} cancelada nos trechos especificados."}
        return {"status": "error", "message": "Falha ao cancelar a reserva."}

    def start(self):
        print('Servidor pronto para aceitar conexões...')
        while True:
            try:
                print('Aguardando conexão...')
                client_socket, addr = self.server.accept()
                print(f"Conexão aceita de {addr}")
                client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_handler.start()
            except Exception as e:
                print(f"Erro durante a aceitação de conexão: {e}")


if __name__ == "__main__":
    server = TravelServer()
    server.start()
