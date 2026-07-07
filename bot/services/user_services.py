from bot.repositories.user import UserRepository



class UserService:

    def __init__(self, user_repo : UserRepository) -> None:
        """
        Конструктор для сервиса пользователей который будет проверять все ошибки и вызывать метода репозиторий.
        В него мы будем кладем обьект репозиторий который будет работать с базами данных даже если не все методы работают с БД.
        """
        self.user_repo = user_repo

    
    async def chek