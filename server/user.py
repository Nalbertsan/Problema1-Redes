from collections import deque
import hashlib

class User:
    def __init__(self, username: str, name: str, password: str):
        self.username = username
        self.name = name
        self.password_hash = self._hash_password(password)
        self.is_registered = False
        self.travels = []

    def __str__(self):
        return f"User(username={self.username}, name={self.name})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, User):
            return self.username == other.username
        return False

    def _hash_password(self, password: str) -> str:
        """Gera um hash seguro da senha."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self) -> bool:
        """Registra o usuário se ainda não estiver registrado."""
        if not self.is_registered:
            self.is_registered = True
            print(f"Usuário {self.username} cadastrado com sucesso.")
            return True
        print(f"Usuário {self.username} já está cadastrado.")
        return False

    def login(self, password: str) -> bool:
        """Verifica a senha e realiza o login do usuário."""
        if self.is_registered:
            if self._hash_password(password) == self.password_hash:
                print(f"Login bem-sucedido para o usuário {self.username}.")
                return True
            print("Senha incorreta.")
            return False
        print("Usuário não está cadastrado.")
        return False
