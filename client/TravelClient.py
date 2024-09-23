import socket
import json
import sys

class TravelClient:
    def __init__(self, host='26.154.161.94', port=5000):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((host, port))
            self.session_token = None
            print("Conectado ao servidor com sucesso.")
        except ConnectionRefusedError:
            print("Erro: Não foi possível conectar ao servidor.")
            sys.exit(1)  # Encerra a execução se a conexão falhar
        except Exception as e:
            print(f"Erro inesperado: {e}")
            sys.exit(1)  # Encerra a execução em caso de erro

    def send_request(self, request_data):
        try:
            if self.session_token:
                request_data["session_token"] = self.session_token  # Adiciona o token de sessão se disponível
            request = json.dumps(request_data)
            self.client.send(request.encode('utf-8'))
            response = self.client.recv(4096).decode('utf-8')  # Buffer para 4096 bytes
            return json.loads(response)
        except socket.error as e:
            print(f"Erro de conexão com o servidor: {e}")
            self.close()  # Fecha a conexão corretamente
            sys.exit(1)  # Encerra a execução após o erro
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
        else:
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
            "command": "LIST",
            "session_token" : self.session_token
        }
        response = self.send_request(request_data)
        if response and response["status"] == "success":
            list_travel = response.get("travels", {})
            print("Trechos disponíveis:")
            for travel, seats in list_travel.items():
                print(f"Rota: {travel}")
                for seat in seats:
                    number, status = seat
                    print(f"  Assento {number}: {status}")
                print()
        else:
            print(f"Server response: {response.get('message', 'Erro desconhecido.')}")

    def list_travels_reserve(self):
        if not self.session_token:
            print("Erro: Você deve estar logado para listar os trechos.")
            return

        request_data = {
            "command": "LIST",
            "session_token" : self.session_token
        }
        response = self.send_request(request_data)
        if response and response["status"] == "success":
            list_travel = response.get("travels_values", {})
            print("Trechos disponíveis:")
            for i,travel in enumerate(list_travel.keys()):
                print(f"{i+1} - Rota: {travel}")
            return len(list_travel)
        else:
            print(f"Server response: {response.get('message', 'Erro desconhecido.')}")
        return 0


    def get_all_list(self):
        if not self.session_token:
            print("Erro: Você deve estar logado para reservar um assento.")
            return
        request_data_list = {
            "command": "LIST",
            "session_token": self.session_token,
        }
        return self.send_request(request_data_list)
    
    

    def reserve_seat(self, segment, seat_number):

        if not self.session_token:
            print("Erro: Você deve estar logado para reservar um assento.")
            return

        request_data_list = {
            "command": "LIST",
            "session_token": self.session_token,
        }
        response_list = self.send_request(request_data_list)
        list_travel = response_list.get("travels_values", {})

        second_key = list(list_travel.keys())[segment - 1]

        value_of_second_item = list_travel[second_key]

        request_data = {
            "command": "RESERVE",
            "segment_indices": value_of_second_item,
            "seat_number": seat_number
        }
        response = self.send_request(request_data)
        print(f"Server response: {response.get('message', 'Erro desconhecido.')}")

    def confirm_list(self):
        response = self.get_all_list()
        confirm_list = response.get('confirm_list', [])

        for i, item in enumerate(confirm_list):
            seat_number = item[0]
            trip = item[2] 
            print(f"{i+1}- Assento: {seat_number} Viagem: {trip}")
        
        return confirm_list
    
    def final_list(self):
        response = self.get_all_list()
        final_list = response.get('final_list', [])

        for i, item in enumerate(final_list):
            seat_number = item[0]
            trip = item[2] 
            print(f"{i+1}- Assento: {seat_number} Viagem: {trip}")
        
        return final_list

    def confirm_reservation(self, route, seat_number):
        if not self.session_token:
            print("Erro: Você deve estar logado para confirmar uma reserva.")
            return
        response_list = self.get_all_list()
        segment_indices = response_list.get("travels_values")
        request_data = {
            "command": "CONFIRM",
            "segment_indices": segment_indices[route],
            "seat_number": seat_number
        }
        response = self.send_request(request_data)
        print(f"Server response: {response.get('message', 'Erro desconhecido.')}")

    def cancel_reservation(self, route, seat_number):
        if not self.session_token:
            print("Erro: Você deve estar logado para confirmar uma reserva.")
            return

        response_list = self.get_all_list()
        segment_indices = response_list.get("travels_values")
        request_data = {
            "command": "CANCEL",
            "segment_indices": segment_indices[route],
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
            print("")
        finally:
            self.client.close()
            print("Conexão encerrada.")


# Exemplo de uso
if __name__ == "__main__":
    client = TravelClient()
    client.close()
