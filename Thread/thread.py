

class Thread(object):
    def __init__(self):
        """
        This is a thread object
        """
        pass

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

    def execute_instruction(self):
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
