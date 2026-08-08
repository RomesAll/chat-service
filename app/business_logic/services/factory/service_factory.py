from business_logic.database import Database


class ServiceFactory:
    """Фабрика сервисов"""

    def __init__(self, db: Database):
        self.db = db
        self._services = {}
        self._facades = {}

    def register(self, name: str, service_class):
        """Регистрирует обычный сервис"""
        self._services[name] = service_class(self.db)
        return self

    def register_facade(self, name: str, facade_class, *service_names):
        """
        Регистрирует фасадный сервис
        :param name: имя фасада
        :param facade_class: класс фасада
        :param service_names: имена сервисов, которые нужны фасаду
        """

        def create_facade():
            # Получаем все необходимые сервисы из фабрики
            services = [self._services[name] for name in service_names]
            return facade_class(self.db, *services)

        self._facades[name] = create_facade
        return self

    def get(self, name: str):
        if name in self._services:
            return self._services[name]
        if name in self._facades:
            # Создаем фасад при первом запросе и кешируем
            service = self._facades[name]()
            self._services[name] = service
            return service
        raise AttributeError(f"Сервис '{name}' не найден")

    def __getattr__(self, name):
        return self.get(name)