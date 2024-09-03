from TravelClient import TravelClient

client = TravelClient()

def require_login():
    """Verifica se o usuário está logado."""
    if client.session_token is None:
        print("Você precisa estar logado para realizar essa ação.")
        return False
    return True

def safe_input(prompt):
    """Função para obter entrada do usuário de forma segura."""
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print("\nEntrada interrompida pelo usuário.")
        return None

def main_menu():
    """Exibe o menu principal e gerencia as opções do usuário."""
    while True:
        try:
            if client.session_token is None:
                print("\nMenu:")
                print("1. Registrar usuário")
                print("2. Login")
                print("3. Sair")
                
                choice = safe_input("Escolha uma opção: ")
                if choice is None:
                    continue

                if choice == '1':
                    username = safe_input("Digite o nome de usuário: ")
                    name = safe_input("Digite seu nome: ")
                    password = safe_input("Digite a senha: ")
                    if username and name and password:
                        client.register(username, name, password)
                    else:
                        print("Erro: Todos os campos são obrigatórios.")

                elif choice == '2':
                    username = safe_input("Digite o nome de usuário: ")
                    password = safe_input("Digite a senha: ")
                    if username and password:
                        client.login(username, password)
                    else:
                        print("Erro: Nome de usuário e senha são obrigatórios.")

                elif choice == '3':
                    print("Saindo...")
                    client.close()
                    break
                
                else:
                    print("Opção inválida. Tente novamente.")
            else:
                print("\nMenu (Logado):")
                print("1. Listar trechos disponíveis")
                print("2. Reservar assento")
                print("3. Confirmar reserva")
                print("4. Cancelar reserva")
                print("5. Sair")
                
                choice = safe_input("Escolha uma opção: ")
                if choice is None:
                    continue

                if choice == '1' and require_login():
                    client.list_travels()

                elif choice == '2' and require_login():
                    route = safe_input("Digite o trecho (por exemplo, 'Belem-Fortaleza'): ")
                    seat_number = safe_input("Digite o número do assento: ")
                    if route and seat_number:
                        client.reserve_seat(route, seat_number)

                elif choice == '3' and require_login():
                    route = safe_input("Digite o trecho da reserva a confirmar (por exemplo, 'Belem-Fortaleza'): ")
                    seat_number = safe_input("Digite o número do assento a confirmar: ")
                    if route and seat_number:
                        client.confirm_reservation(route, seat_number)

                elif choice == '4' and require_login():
                    route = safe_input("Digite o trecho da reserva a cancelar (por exemplo, 'Belem-Fortaleza'): ")
                    seat_number = safe_input("Digite o número do assento: ")
                    if route and seat_number:
                        client.cancel_reservation(route, seat_number)

                elif choice == '5':
                    print("Saindo...")
                    client.close()
                    break

                else:
                    print("Opção inválida. Tente novamente.")
        
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
            continue

# Executa o menu principal
if __name__ == "__main__":
    main_menu()
