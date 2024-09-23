from user import User
import threading
import time


class TravelSegment:
    def __init__(self, origin: str, destination: str, max_seats: int):
        self.origin = origin
        self.destination = destination
        self.max_seats = max_seats
        self.seats = {}
        self.final_seats = {} 
        self.seat_locks = {seat_number: threading.Lock() for seat_number in range(1, max_seats + 1)}
        self.confirmation_threads = {}

    def reserve_seat(self, user: User, seat_number: int) -> bool:
        """Inicia o processo de reserva de um assento para este trecho."""
        if not (1 <= seat_number <= self.max_seats):
            print(f"O assento {seat_number} não existe.")
            return False

        lock = self.seat_locks[seat_number]
        if not lock.acquire(blocking=False):
            print(f"O assento {seat_number} está bloqueado para reserva.")
            return False

        try:
            if seat_number in self.final_seats:
                print(f"O assento {seat_number} já está ocupado por {self.final_seats[seat_number].username}.")
                return False

            if seat_number in self.seats:
                print(f"O assento {seat_number} já está reservado temporariamente.")
                return False

            print(f"O assento {seat_number} está reservado para {user.username} no trecho {self.origin}-{self.destination}. Aguardando confirmação...")
            self.seats[seat_number] = user 

            confirmation_thread = threading.Thread(target=self.confirmation_timer, args=(user, seat_number))
            confirmation_thread.start()
            self.confirmation_threads[seat_number] = confirmation_thread

            return True
        finally:
            lock.release()

    def confirmation_timer(self, user: User, seat_number: int):
        """Aguarda 30 segundos para confirmação da reserva. Se não for confirmado, libera o assento."""
        time.sleep(30)
        lock = self.seat_locks[seat_number]

        with lock:
            if self.seats.get(seat_number) is user:
                print(f"O tempo para confirmação do assento {seat_number} por {user.username} expirou. Liberando o assento.")
                del self.seats[seat_number]

    def confirm_reservation(self, user: User, seat_number: int) -> bool:
        """Confirma a reserva do assento para o usuário."""
        print('Aqui')
        lock = self.seat_locks[seat_number]
        with lock:
            print('Aqui')
            if self.seats.get(seat_number) is user:
                print(f"O assento {seat_number} foi confirmado para {user.username}.")
                self.final_seats[seat_number] = self.seats.pop(seat_number)
                return True
            else:
                print(f"Somente o usuário que reservou pode confirmar. {user.username} não é o dono da reserva do assento {seat_number}.")
                return False

    def cancel_reservation(self, user: User, seat_number: int) -> bool:
        """Cancela a reserva do assento e libera o assento, se o usuário for o dono da reserva."""
        lock = self.seat_locks[seat_number]
        with lock:
            if seat_number in self.final_seats and self.final_seats[seat_number] is user:
                print(f"Reserva do assento {seat_number} cancelada para {user.username}.")
                del self.final_seats[seat_number]
                return True
            elif seat_number in self.seats and self.seats[seat_number] is user:
                print(f"Reserva temporária do assento {seat_number} cancelada para {user.username}.")
                del self.seats[seat_number]
                return True
            else:
                print(f"{user.username} não tem permissão para cancelar o assento {seat_number}.")
                return False


    def cancel_reservation_seg(self, seat_number: int) -> bool:
        """Cancela a reserva do assento temporário e libera o assento."""
        if seat_number in self.seats:
            user = self.seats.pop(seat_number)
            print(f"Reserva do assento {seat_number} cancelada para {user.username}.")
            return True

        print(f"O assento {seat_number} não está reservado temporariamente.")
        return False

    def list_occupied_seats(self):
        """Retorna uma lista de tuplas com assentos ocupados e seus respectivos usuários."""
        return [(seat_number, user.username) for seat_number, user in self.final_seats.items()]
    
    def list_seats_status(self):
        """Retorna o status de todos os assentos do trecho."""
        seat_status = []
        for seat_number in range(1, self.max_seats + 1):
            if seat_number in self.final_seats:
                seat_status.append((seat_number, "Vendido"))
            elif seat_number in self.seats:
                seat_status.append((seat_number, "Ocupado Temporariamente"))
            else:
                seat_status.append((seat_number, "Disponível"))
        return seat_status


class Travel:
    def __init__(self, segments:list):
        self.segments = segments

    def reserve_seat(self, user: User, seat_number: int, segment_indices: list[int]) -> bool:
        """Reserva um assento em múltiplos trechos."""
        for i in segment_indices:
            if not self.segments[i].reserve_seat(user, seat_number):

                for j in segment_indices[:i]:
                    self.segments[j].cancel_reservation_seg(seat_number)
                return False
        return True

    def confirm(self, user: User, seat_number: int, segment_indices: list[int]) -> bool:
        """Confirma a reserva de assento para múltiplos trechos."""
        confirmed = True
        for i in segment_indices:
            if not self.segments[i].confirm_reservation(user, seat_number):
                confirmed = False
        return confirmed

    def cancel_reservation(self, seat_number: int, segment_indices: list[int], user: User) -> bool:
        """Cancela a reserva do assento em múltiplos trechos, apenas se o usuário for o dono da reserva."""
        success = True
        for i in segment_indices:
            if not self.segments[i].cancel_reservation(user, seat_number):
                success = False
        return success

    
    def list_all_final_seats(self, user: User):
        """Lista todos os assentos confirmados em todos os trechos da viagem, combinando a origem do primeiro 
        segmento com o destino do último para cada número de assento."""
        
        seat_tracker = {}  # Dicionário para rastrear o último segmento por número de assento

        for segment in self.segments:
            # Obtém os assentos ocupados no segmento
            occupied_seats = segment.list_occupied_seats()
            for seat_number, username in occupied_seats:
                # Verifica se o assento foi reservado pelo usuário específico
                if username == user.username:
                    # Atualiza o dicionário para cada número de assento encontrado, mantendo o último segmento
                    if seat_number in seat_tracker:
                        seat_tracker[seat_number]['destination'] = segment.destination
                    else:
                        # Se o assento não foi registrado, adicionar a origem e o destino
                        seat_tracker[seat_number] = {
                            'origin': segment.origin,
                            'destination': segment.destination,
                            'username': username
                        }

        # Monta a lista final de assentos com origem-destino combinado
        all_final_seats = [
            (seat_number, data['username'], f"{data['origin']}-{data['destination']}")
            for seat_number, data in seat_tracker.items()
        ]

        return all_final_seats

    
    
    def list_all_seats(self):
        """Retorna o status de todos os assentos para todos os segmentos."""
        seats_status = {}
        for segment in self.segments:
            segment_name = f"{segment.origin}-{segment.destination}"
            seats_status[segment_name] = segment.list_seats_status()
        return seats_status
    
    def list_all_values(self):
        travel_values = {}
        # Iterar por todos os segmentos da viagem
        for i in range(len(self.segments)):
            for j in range(i, len(self.segments)):
                reserved_segments = list(range(i, j + 1))
                origin = self.segments[i].origin
                destination = self.segments[j].destination
                segment_name = f"{origin}-{destination}"

                travel_values[segment_name] = reserved_segments

        return travel_values
    
    def list_seats_for_confirmation(self, user):
        """Retorna a lista final de assentos temporariamente reservados pelo usuário, mantendo apenas o último segmento 
        com o mesmo número de assento, e combinando a origem do primeiro segmento com o destino do último."""
        
        seat_tracker = {}  # Dicionário para rastrear o último segmento por número de assento
        
        for segment in self.segments:
            for seat_number, seat_user in segment.seats.items():
                if seat_user.username == user.username:
                    # Atualiza o dicionário para cada número de assento encontrado, mantendo o último segmento
                    if seat_number in seat_tracker:
                        # Se o assento já foi registrado, atualizar o destino do último segmento
                        seat_tracker[seat_number]['destination'] = segment.destination
                    else:
                        # Se o assento não foi registrado, adicionar a origem e o destino
                        seat_tracker[seat_number] = {
                            'origin': segment.origin,
                            'destination': segment.destination,
                            'username': seat_user.username
                        }

        seats_for_confirmation = [
            (seat_number, data['username'], f"{data['origin']}-{data['destination']}")
            for seat_number, data in seat_tracker.items()
        ]
        
        return seats_for_confirmation





def simulate_reservation(travel, user, seat_number, segment_indices):
    # Tenta reservar o assento
    reservation_success = travel.reserve_seat(user, seat_number, segment_indices)
    if reservation_success:
        # Tenta confirmar a reserva
        confirmation_success = travel.confirm_reservation(user, seat_number, segment_indices)
        if confirmation_success:
            print(f"{user.username} confirmou o assento {seat_number} nos segmentos {segment_indices}.")
        else:
            print(f"{user.username} falhou ao confirmar o assento {seat_number} nos segmentos {segment_indices}.")
    else:
        print(f"{user.username} falhou ao reservar o assento {seat_number} nos segmentos {segment_indices}.")


# Função principal para configurar o teste de concorrência
def main():
    # Cria segmentos de viagem
    segments = [
        TravelSegment('Belém', 'Fortaleza', 10),
        TravelSegment('Fortaleza', 'São Paulo', 10),
        TravelSegment('São Paulo', 'Curitiba', 10),
    ]

    # Cria a viagem com os segmentos definidos
    travel = Travel(segments)

    # Cria usuários
    user1 = User('Nalbert', 'User One', 'password1')
    user2 = User('Pedro', 'User Two', 'password2')
    user3 = User('Carol', 'User Three', 'password3')

    # Define assentos e segmentos para cada usuário tentar reservar
    seat_number = 10
    segment_indices = [0, 1, 2]  # Usuários vão tentar reservar nos mesmos segmentos

    # Cria threads para simular reservas simultâneas
    threads = [
        threading.Thread(target=simulate_reservation, args=(travel, user1, seat_number, segment_indices)),
        threading.Thread(target=simulate_reservation, args=(travel, user2, seat_number, segment_indices)),
        threading.Thread(target=simulate_reservation, args=(travel, user3, seat_number, segment_indices)),
    ]

    # Inicia as threads
    for thread in threads:
        thread.start()

    # Aguarda a conclusão de todas as threads
    for thread in threads:
        thread.join()

    # Lista todos os assentos confirmados após as operações
    final_seats = travel.list_all_final_seats(user1)
    print(final_seats)
    

# Executa o teste
if __name__ == "__main__":
    main()