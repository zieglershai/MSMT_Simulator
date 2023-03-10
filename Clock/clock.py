
class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Clock(metaclass=SingletonMeta):
    def __init__(self):
        self.__cycle = 0

    def get_cycle(self):
        return self.__cycle

    def step(self):
        self.__cycle += 1

    def reset(self):
        self.__cycle = 0
