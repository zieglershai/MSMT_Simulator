from Policy.policy import Policy
from Clock.clock import Clock


class RoundRobbin(Policy):
    def __init__(self, num_threads, quanta, clock):
        super().__init__(clock)
        self.num_threads = num_threads
        self.quanta = quanta
        self.priority_list = [i for i in num_threads]

    def get_threads_by_priority(self):
        """
        return a list with one thread index to run
        :return:
        """
        pass
