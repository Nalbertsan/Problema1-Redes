import socket
import json

class TravelClient:
    def __init__(self, host='localhost', port=5050):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((host, port))
            self.session_token = None
            self.list = []
            print("Conectado ao servidor com sucesso.")
        except ConnectionRefusedError:
            print("Erro: Não foi possível conectar ao servidor.")
        except Exception as e:
            print(f"Erro inesperado: {e}")

    def send_request(self, request_data):
        try:
            if self.session_token:
                request_data["session_token"] = self.session_token  # Adiciona o token de sessão se disponível
            request = json.dumps(request_data)
            self.client.send(request.encode('utf-8'))
            response = self.client.recv(4096).decode('utf-8')  # Buffer para 4096 bytes
            return json.loads(response)
        except json.JSONDecodeError:
            print("Erro: Resposta inválida do servidor.")
        except Exception as e:
            print(f"Erro na comunicação com o servidor: {e}")
            return {"status": "error", "message": "Erro na comunicação com o servidor."}

    def register(self, username, name, password):
        request_data = {
            "command": "REGISTER",
            "username": username,
            "name": name,
            "password": password
        }
        response = self.send_request(request_data)
        if response and response["status"] == "success":
            self.session_token = response.get("session_token")
            print("Registro bem-sucedido.")
        print(f"Server response: {response.get('message', 'Erro desconhecido.')}")

    def login(self, username, password):
        request_data = {
            "command": "LOGIN",
            "username": username,
            "password": password
        }
        response = self.send_request(request_data)
        if response and response["status"] == "success":
            self.session_token = response.get("session_token")
            print("Login bem-sucedido.")
        else:
            print(f"Server response: {response.get('message', 'Erro desconhecido.')}")

    def list_travels(self):
        if not self.session_token:
            print("Erro: Você deve estar logado para listar os trechos.")
            return

        request_data = {
            "command": "LIST"
        }
        response = self.send_request(request_data)
        if response and response["status"] == "success":
            self.list = response.get("travels", [])
            print("Trechos disponíveis:")
            for travel in response.get("travels", []):
                print(f" - {travel}")
        else:
            print(f"Server response: {response.get('message', 'Erro desconhecido.')}")

    def reserve_seat(self, route, seat_number):
        if not self.session_token:
            print("Erro: Você deve estar logado para reservar um assento.")
            return

        request_data = {
            "command": "RESERVE",
            "route": route,
            "seat_number": seat_number
        }
        response = self.send_request(request_data)
        print(f"Server response: {response.get('message', 'Erro desconhecido.')}")

    def confirm_reservation(self, route, seat_number):
        if not self.session_token:
            print("Erro: Você deve estar logado para confirmar uma reserva.")
            return

        request_data = {
            "command": "CONFIRM",
            "route": route,
            "seat_number": seat_number
        }
        response = self.send_request(request_data)
        print(f"Server response: {response.get('message', 'Erro desconhecido.')}")

    def cancel_reservation(self, route, seat_number):
        if not self.session_token:
            print("Erro: Você deve estar logado para cancelar uma reserva.")
            return

        request_data = {
            "command": "CANCEL",
            "route": route,
            "seat_number": seat_number
        }
        response = self.send_request(request_data)
        print(f"Server response: {response.get('message', 'Erro desconhecido.')}")

    def close(self):
        try:
            if self.session_token:
                request_data = {
                    "command": "LOGOUT",
                    "session_token": self.session_token,
                }
                response = self.send_request(request_data)
                print(f"Logout response: {response.get('message', 'Erro desconhecido.')}")
        except Exception as e:
            print(f"Erro ao encerrar a sessão: {e}")
        finally:
            self.client.close()
            print("Conexão encerrada.")
