from .User import User

class UserService:
    def __init__(self, user_repository):
        self.repository = user_repository

    def cadastrar_usuario(self, name: str, email: str, cpf: str) -> User:
        if not name or not name.strip():
            raise ValueError("O nome é obrigatório.")

        if not email or not email.strip():
            raise ValueError("O e-mail é obrigatório.")

        if not cpf or not cpf.strip():
            raise ValueError("O CPF é obrigatório.")

        if "@" not in email or "." not in email:
            raise ValueError("O formato do e-mail é inválido.")

        if len(cpf) != 11 or not cpf.isdigit():
            raise ValueError("O CPF deve conter exatamente 11 números.")

        if self.repository.buscar_por_email(email):
            raise ValueError("Este e-mail já está em uso.")

        if self.repository.buscar_por_cpf(cpf):
            raise ValueError("Este CPF já está cadastrado.")

        novo_usuario = User(name=name, email=email, cpf=cpf)
        return self.repository.salvar(novo_usuario)
