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
        lock = self.seat_locks[seat_number]
        with lock:
            if self.seats.get(seat_number) is user:
                print(f"O assento {seat_number} foi confirmado para {user.username}.")
                self.final_seats[seat_number] = self.seats.pop(seat_number)
                return True

            print(f"O assento {seat_number} não pode ser confirmado para {user.username}.")
            return False

    def cancel_reservation(self, seat_number: int) -> bool:
        """Cancela a reserva do assento e libera o assento."""
        if seat_number in self.final_seats:
            user = self.final_seats.pop(seat_number)
            print(f"Reserva do assento {seat_number} cancelada para {user.username}.")
            return True

        print(f"O assento {seat_number} não está ocupado.")
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


class Travel:
    def __init__(self, segments):
        self.segments = segments

    def reserve_seat(self, user: User, seat_number: int, segment_indices: list[int]) -> bool:
        """Reserva um assento em múltiplos trechos."""
        for i in segment_indices:
            if not self.segments[i].reserve_seat(user, seat_number):

                for j in segment_indices[:i]:
                    self.segments[j].cancel_reservation_seg(seat_number)
                return False
        return True

    def confirm_reservation(self, user: User, seat_number: int, segment_indices: list[int]) -> bool:
        """Confirma a reserva de assento para múltiplos trechos."""
        confirmed = True
        for i in segment_indices:
            if not self.segments[i].confirm_reservation(user, seat_number):
                confirmed = False
        return confirmed

    def cancel_reservation(self, seat_number: int, segment_indices: list[int]) -> bool:
        """Cancela a reserva do assento em múltiplos trechos."""
        for i in segment_indices:
            self.segments[i].cancel_reservation(seat_number)
        return True
    
    def list_all_final_seats(self):
        """Lista todos os assentos confirmados em todos os trechos da viagem."""
        all_final_seats = []
        for i, segment in enumerate(self.segments):
            occupied_seats = segment.list_occupied_seats()
            for seat_number, username in occupied_seats:
                all_final_seats.append((seat_number, username, segment.origin, segment.destination))
        return all_final_seats


if __name__ == "__main__":
    segments = [
        TravelSegment('Belém', 'Fortaleza', 10),
        TravelSegment('Fortaleza', 'São Paulo', 10),
        TravelSegment('São Paulo', 'Curitiba', 10),
    ]

    travel = Travel(segments)
    user1 = User('Nalbert', 'User One', 'password1')
    user2 = User('Pedro', 'User Two', 'password2')

    travel.reserve_seat(user1, 2, [1, 2])
    travel.reserve_seat(user2, 2, [0,1]) 
    travel.confirm_reservation(user1, 2, [0, 1, 2])
    travel.confirm_reservation(user2, 2, [0, 1, 2])

    final_seats = travel.list_all_final_seats()
    print("Assentos confirmados:")
    for seat in final_seats:
        print(f"Assento {seat[0]} ocupado por {seat[1]} no trecho {seat[2]}-{seat[3]}")
