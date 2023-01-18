import pickle


class Thread(object):
    def __init__(self, trace_df_path: str, window_size: int):
        """
        This is a thread object
        :param trace_df_path: path to a pickle with the parsed instructions in a DF
        """
        self.window_size = window_size
        with open(trace_df_path, 'rb') as f:
            self.instructions = pickle.load(f)
        self.final_cycle = None
        self.instruction = 0
        self.total_instructions = len(self.instructions.index)

    def get_unexecuted_instructions(self):
        """
        get a df of instructions that need to run
        :return:
        """
        pass

    def step(self):
        """
        run cycle step
        :return:
        """
        pass

    def set_instruction_finish_cycle(self, instruction_id, instruction_cycles):
        """
        set instruction run cycle
        :return: boolean of true or false
        """
        pass

    def check_if_done(self):
        """
        check if all instructions have run
        :return:
        """
        pass

    def get_progress(self):
        return 100 * self.instructions / float(self.total_instructions)
