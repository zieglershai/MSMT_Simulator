import pickle
from constants import ROW_ID, FINISH_CYCLE
from Clock.clock import Clock


class Thread(object):
    def __init__(self, trace_df_path: str, window_size: int, clock: Clock):
        """
        This is a thread object
        :param trace_df_path: path to a pickle with the parsed instructions in a DF
        """
        self.clock = clock
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
        instruction_window = self.instructions.loc[(self.instruction, self.instruction + self.window_size), :]
        return instruction_window

    def step(self):
        """
        run cycle step
        :return:
        """
        self.instruction = self.instructions[(self.instructions[FINISH_CYCLE] is not None) &
                                             (self.instructions[FINISH_CYCLE] < self.clock.get_cycle())].iloc[0]

    def set_instruction_finish_cycle(self, instruction_id, instruction_cycles):
        """
        set instruction run cycle
        :return: boolean of true or false
        """
        instruction_row = self.instructions.loc[instruction_id]
        instruction_row[FINISH_CYCLE] = self.clock.get_cycle() + instruction_cycles

    def check_if_done(self):
        """
        check if all instructions have run
        :return:
        """
        return self.instruction + 1 == self.total_instructions

    def get_progress(self):
        return 100 * self.instruction / float(self.total_instructions)
