import pickle
from constants import ROW_ID, FINISH_CYCLE, READ_REG_A, READ_REG_B, WRITE_REG, INSTRUCTION_TYPE, InstructionType
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
            # self.instructions.set_index(ROW_ID)
        self.instructions[FINISH_CYCLE] = -1
        self.final_cycle = None
        self.soe_ready_on = 0
        self.instruction = 0
        self.total_instructions = len(self.instructions.index)
        self.sleep_return = 0

    def get_unexecuted_instructions(self):
        """
        get a df of instructions that need to run
        :return:
        """
        instruction_window = self.instructions.loc[self.instruction: self.instruction + self.window_size-1].copy()
        if self.sleep_return > self.clock.get_cycle():
            return instruction_window.loc[0:-1]
        write_regs = set()
        # TODO: make sure that we are in-order within the window_ooo - Yes
        commands = 0
        for i, row in instruction_window.iterrows():
            commands += 1
            # TODO: make sure we need to stop the window_ooo after LDST - No only on miss!!!
            # if row[READ_REG_A] in write_regs or row[READ_REG_B] in write_regs or \
            #         row[INSTRUCTION_TYPE] == InstructionType.LDST:
            #     break  # Todo break only on miss

            if row[READ_REG_A] in write_regs or row[READ_REG_B] in write_regs:
                break  # Todo break only on miss
            if row[WRITE_REG] != "":
                write_regs.add(row[WRITE_REG])

        instruction_window = instruction_window.loc[self.instruction: self.instruction + commands-1]
        # TODO: make sure this works
        instruction_window = instruction_window[instruction_window[FINISH_CYCLE] == -1]

        return instruction_window

    def step(self):
        """
        run cycle step
        :return:
        """
        # TODO: make sure this works
        try:
            self.instruction = self.instructions[(self.instructions[FINISH_CYCLE] == -1) |
                                             (self.instructions[FINISH_CYCLE] > self.clock.get_cycle())].iloc[0][ROW_ID]
        except IndexError:
            assert(len(self.instructions[(self.instructions[FINISH_CYCLE] != -1) &
                                         (self.instructions[FINISH_CYCLE] <= self.clock.get_cycle())]) ==
                   self.total_instructions,
                   "Index error even though not empty")
            self.instruction = self.total_instructions
            self.final_cycle = self.clock.get_cycle()

    def set_instruction_finish_cycle(self, instruction_id, instruction_cycles):
        """
        set instruction run cycle
        :return: boolean of true or false
        """
        # instruction_row = self.instructions.loc[instruction_id]
        # instruction_row[FINISH_CYCLE] = self.clock.get_cycle() + instruction_cycles

        self.instructions.at[instruction_id, FINISH_CYCLE] = self.clock.get_cycle() + instruction_cycles

    def check_if_done(self):
        """
        check if all instructions have run
        :return:
        """
        return self.instruction == self.total_instructions

    def get_progress(self):
        return 100 * self.instruction / float(self.total_instructions)

    def set_cache_miss(self, cycle):
        """
        set switch on event return time
        :return:
        """
        self.soe_ready_on = self.clock.get_cycle() + cycle

    def sleep_on_soe_enter_l_one(self, penalty):
        self.sleep_return = self.clock.get_cycle() + penalty

    def ready(self):
        """

        :return: true if the thread is ready
        """
        return self.soe_ready_on <= self.clock.get_cycle()

    def prefetch(self, prefetch_cycles: int):
        """

        :return: true if the thread is prefetcehd
        """
        return self.soe_ready_on + prefetch_cycles <= self.clock.get_cycle()
