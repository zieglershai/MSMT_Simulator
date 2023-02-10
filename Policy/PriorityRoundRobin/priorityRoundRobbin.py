from Policy.policy import Policy
from Clock.clock import Clock


class PriorityRoundRobbin(Policy):
    def __init__(self, priority_threads: list, normal_threads: list, quanta: int, clock: Clock):
        super().__init__(clock)
        self.num_threads = len(priority_threads) + len(normal_threads)
        self.quanta = quanta
        self.priority_threads = priority_threads
        self.normal_threads = normal_threads

    def get_threads_by_priority(self, threads=None):
        """
        return a list with one thread index to run
        :return:
        """
        cycle = self.clock.get_cycle()
        if cycle % self.quanta == 0:
            self.priority_threads.append(self.priority_threads.pop(0))
            self.normal_threads.append(self.normal_threads.pop(0))

        # TODO: what should we do here?
        return self.priority_threads + self.normal_threads
