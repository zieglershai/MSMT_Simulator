from Policy.policy import Policy
from Clock.clock import Clock


class RoundRobbin(Policy):
    def __init__(self, num_threads: int, quanta: int, clock: Clock):
        super().__init__(clock)
        self.num_threads = num_threads
        self.quanta = quanta
        self.priority_list = [i for i in range(num_threads)]

    def get_threads_by_priority(self):
        """
        return a list with one thread index to run
        :return:
        """
        cycle = self.clock.get_cycle()
        if cycle % self.quanta == 0:
            self.priority_list.append(self.priority_list.pop(0))

        # TODO: what should we do here?
        return self.priority_list
