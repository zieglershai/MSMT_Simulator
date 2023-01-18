from Policy.policy import Policy


class RoundRobbin(Policy):
    def __init__(self):
        super().__init__()
        pass

    def get_threads_by_priority(self):
        """
        return a list with one thread index to run
        :return:
        """
        pass
