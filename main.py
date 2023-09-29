import json
import hashlib

# Requisito: Persistência dos dados em arquivos de texto
# Arquivos para armazenar dados de usuários e carros
USERS_FILE = "users.json"
CARS_FILE = "cars.json"

# Variável global para rastrear o usuário logado
logged_in_user = None
logged_in_user_role = None

class ResultMonad:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    def bind(self, func):
        if self.value is not None:
            try:
                result = func(self.value)
                return ResultMonad(value=result)
            except Exception as e:
                return ResultMonad(error=str(e))
        else:
            return ResultMonad(error=self.error)

    def is_successful(self):
        return self.value is not None

    def is_failure(self):
        return self.error is not None

    def get_value(self):
        return self.value

    def get_error(self):
        return self.error

# Função para criptografar senhas
def encrypt_password(password):
    salt = "s3cr3t_s4lt"  # Salt para aumentar a segurança
    hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashed_password

# Função para ler todos os usuários cadastrados
def read_users():
    try:
        with open(USERS_FILE, 'r') as file:
            users = json.load(file)
            return users
    except FileNotFoundError:
        return []

# Função para atualizar os dados de um usuário
def update_user(username, new_password):
    users = read_users()
    for user in users:
        if user['username'] == username:
            user['password'] = encrypt_password(new_password)
            with open(USERS_FILE, 'w') as file:
                json.dump(users, file, indent=2)
            print(f"Senha atualizada com sucesso para o usuário: {username}")
            return
    print(f"Usuário não encontrado: {username}")

# Função para excluir um usuário
def delete_user(username):
    global logged_in_user_role
    
    users = read_users()
    
    if logged_in_user_role == 'admin' and username != logged_in_user:
        for user in users:
            if user['username'] == username:
                users.remove(user)
                with open(USERS_FILE, 'w') as file:
                    json.dump(users, file, indent=2)
                print(f"Usuário excluído com sucesso: {username}")
                return
        print(f"Usuário não encontrado: {username}")
    else:
        print("Apenas administradores podem excluir outros usuários e não podem excluir a si mesmos.")

# Função para ler todos os carros cadastrados
def read_cars():
    try:
        with open(CARS_FILE, 'r') as file:
            cars = json.load(file)
            return cars
    except FileNotFoundError:
        return []

# Função para atualizar os dados de um carro
def update_car(model, new_status):
    cars = read_cars()
    for car in cars:
        if car['model'] == model:
            car['is_rented'] = new_status
            with open(CARS_FILE, 'w') as file:
                json.dump(cars, file, indent=2)
            status = "alugado" if new_status else "disponível"
            print(f"Status do carro '{model}' atualizado para {status}")
            return
    print(f"Carro não encontrado: {model}")

# Função para excluir um carro
def delete_car(model):
    cars = read_cars()
    for car in cars:
        if car['model'] == model:
            cars.remove(car)
            with open(CARS_FILE, 'w') as file:
                json.dump(cars, file, indent=2)
            print(f"Carro excluído com sucesso: {model}")
            return
    print(f"Carro não encontrado: {model}")

# Função para listar carros disponíveis
def list_available_cars():
    try:
        with open(CARS_FILE, 'r') as file:
            cars = json.load(file)
            # Utilização de função lambda para verificar o status de aluguel dos carros
            check_availability = lambda car: not car['is_rented']
            available_cars = filter(check_availability, cars)
            available_cars = list(available_cars)
            if available_cars:
                print("Automóveis disponíveis para aluguel:")
                for car in available_cars:
                    print(f"Modelo: {car['model']}")
            else:
                print("Nenhum automóvel disponível para aluguel.")
    except FileNotFoundError:
        print("Nenhum automóvel cadastrado.")

# Função para alugar um carro
def rent_car(username, car_model):
    try:
        cars = read_cars()
        for car in cars:
            if car['model'] == car_model:
                if not car['is_rented']:
                    car['is_rented'] = True
                    with open(CARS_FILE, 'w') as file:
                        json.dump(cars, file, indent=2)
                    print(f"Carro '{car_model}' alugado com sucesso por {username}.")
                    return
                else:
                    print(f"Carro '{car_model}' já está alugado.")
                    return
        print(f"Carro não encontrado: {car_model}")
    except FileNotFoundError:
        print("Nenhum automóvel cadastrado.")

# Função para registrar um novo usuário
def register_user(username, password):
    try:
        with open(USERS_FILE, 'r') as file:
            users = json.load(file)
    except FileNotFoundError:
        users = []

    # Verificar se o usuário já existe
    for user in users:
        if user['username'] == username:
            print("Erro: O usuário já existe.")
            return

    # Criptografar a senha antes de armazená-la
    hashed_password = encrypt_password(password)

    # Adicionar o novo usuário
    users.append({"username": username, "password": hashed_password, "role": "user"})

    # Salvar os dados em um arquivo
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file, indent=2)
    print("Registro concluído com sucesso.")

# Função para fazer login de um usuário
def login_user(username, password):
    try:
        with open(USERS_FILE, 'r') as file:
            users = json.load(file)
    except FileNotFoundError:
        return ResultMonad(error="Nenhum usuário cadastrado.")

    for user in users:
        if user['username'] == username:
            hashed_password = encrypt_password(password)
            if user['password'] == hashed_password:
                return ResultMonad(value=user.get('role', 'user'))
            else:
                return ResultMonad(error="Senha incorreta.")
    
    return ResultMonad(error="Usuário não encontrado.")

# Função para criar um novo carro
def create_car(model):
    cars = read_cars()
    for car in cars:
        if car['model'] == model:
            print("Erro: O carro já existe.")
            return

    cars.append({"model": model, "is_rented": False})

    with open(CARS_FILE, 'w') as file:
        json.dump(cars, file, indent=2)
    print(f"Carro '{model}' criado com sucesso.")

# Função de Continuação
def continue_operation():
    input("Pressione Enter para continuar...")

# Closure para criar uma função de alta ordem
def create_user_closure():
    message = "Bem-vindo ao sistema. Faça login ou registre-se."
    
    def welcome_user(username):
        print(f"{message} Olá, {username}!")
    
    return welcome_user

# Função de Alta Ordem
def apply_to_each_user(users, func):
    for user in users:
        func(user)

# Monad (exemplo de uso)
def user_maybe(username):
    def bind(func):
        if username:
            return func(username)
        else:
            return None

    return bind

# Função principal
def main():
    global logged_in_user, logged_in_user_role
    
    while True:
        print("\nEscolha uma opção:")
        print("1. Registrar um novo usuário")
        print("2. Fazer login de um usuário")
        print("3. Listar carros disponíveis")
        print("4. Alugar um carro")
        print("5. Atualizar a senha do usuário")
        print("6. Excluir um usuário")
        print("7. Listar todos os carros cadastrados")
        print("8. Atualizar o status de um carro")
        print("9. Excluir um carro")
        print("10. Criar um novo carro")
        print("0. Sair")

        choice = input("Digite o número da opção desejada: ")

        if choice == "1":
            username = input("Digite o nome de usuário: ")
            password = input("Digite a senha: ")
            register_user(username, password)
        if choice == "2":
            username = input("Digite o nome de usuário: ")
            password = input("Digite a senha: ")
            login_result = login_user(username, password)

            if login_result.is_successful():
                logged_in_user_role = login_result.get_value()
                logged_in_user = username
                print(f"Você está logado como {logged_in_user} ({logged_in_user_role}).")
            else:
                print(f"Login falhou: {login_result.get_error()}")
        elif choice == "3":
            list_available_cars()
            continue_operation()  # Função de Continuação
        elif choice == "4":
            if 'logged_in_user_role' in globals():
                if logged_in_user_role == 'admin' or logged_in_user_role == 'user':
                    car_model = input("Digite o modelo do carro que deseja alugar: ")
                    rent_car(logged_in_user, car_model)
                    continue_operation()  # Função de Continuação
            else:
                print("Faça login antes de alugar um carro.")
        elif choice == "5":
            if 'logged_in_user_role' in globals():
                if logged_in_user_role == 'admin' or logged_in_user_role == 'user':
                    new_password = input("Digite a nova senha: ")
                    update_user(logged_in_user, new_password)
                    continue_operation()  # Função de Continuação
            else:
                print("Faça login antes de atualizar a senha do usuário.")
        elif choice == "6":
            if 'logged_in_user' in globals():
                if logged_in_user_role == 'admin':
                    username_to_delete = input("Digite o nome de usuário que deseja excluir: ")
                    delete_user(username_to_delete)
                    continue_operation()  # Função de Continuação
                else:
                    print("Apenas administradores podem excluir usuários.")
            else:
                print("Faça login antes de excluir um usuário.")
        elif choice == "7":
            if 'logged_in_user_role' in globals():
                if logged_in_user_role == 'admin' or logged_in_user_role == 'user':
                    print("Listando todos os carros cadastrados:")
                    all_cars = read_cars()
                    for car in all_cars:
                        status = "alugado" if car['is_rented'] else "disponível"
                        print(f"Modelo: {car['model']}, Status: {status}")
                    continue_operation()  # Função de Continuação
            else:
                print("Faça login antes de listar todos os carros cadastrados.")
        elif choice == "8":
            if 'logged_in_user' in globals():
                if logged_in_user == 'admin':
                    car_model = input("Digite o modelo do carro que deseja atualizar: ")
                    new_status = input("Digite o novo status (1 para alugado, 0 para disponível): ")
                    new_status = bool(int(new_status))
                    update_car(car_model, new_status)
                    continue_operation()  # Função de Continuação
                else:
                    print("Apenas administradores podem atualizar o status dos carros.")
            else:
                print("Faça login antes de atualizar o status de um carro.")
        elif choice == "9":
            if 'logged_in_user' in globals():
                if logged_in_user == 'admin':
                    car_model = input("Digite o modelo do carro que deseja excluir: ")
                    delete_car(car_model)
                    continue_operation()  # Função de Continuação
                else:
                    print("Apenas administradores podem excluir carros.")
            else:
                print("Faça login antes de excluir um carro.")
        elif choice == "10":
            if 'logged_in_user' in globals() and logged_in_user == 'admin':
                car_model = input("Digite o modelo do novo carro: ")
                create_car(car_model)
                continue_operation()  # Função de Continuação
            else:
                print("Apenas administradores podem criar novos carros.")
        elif choice == "0":
            print("Saindo do programa.")
            break
        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")

if __name__ == "__main__":
    main()