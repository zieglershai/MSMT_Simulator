

class Scheduler(object):
    def __init__(self, config_file_path: str, trace_folder: str):
        """
        This is the main class that will run the simulation
        """
        self.parse_input(config_file_path, trace_folder)
        self.create_threads()

    def parse_input(self, config_file_path: str, trace_folder: str):
        """
        Parse the config:
            set:
                1. window size
                2. penalties
                3. execution units - number and latency
                4. miss rate
                5. scheduling policy
        :param config_file_path:
        :param trace_folder:
        :return:
        """
        pass

    def create_threads(self):
        """
        after configuration set, create thread objects
        :return:
        """
        pass

    def step(self):
        """
        this function adds a cycle to all the elements of the simulator
        :return:
        """
        pass

    def get_threads_by_priority(self):
        """
        This function returns a list of the threads index
        ordered by the current priority to get instructions from
        :return:
        """
        pass

    def check_if_all_threads_are_done(self):
        """
        Checks if all the threads are finished running
        :return:
        """
        pass

    def run(self):
        """
        Main run loop
        :return:
        """
        pass

    def get_unexecuted_instruction_window_from_thread(self):
        """

        :return: (int, enum)
        """
        pass

    def set_instruction_ran_on_thread(self, instruction: int):
        """

        :return:
        """
        pass

    def execute_instruction(self):
        """
        try to execute command
        :return: boolean of true or false
        """
        pass

