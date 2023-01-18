import pickle
import pandas as pd
import sys
import os
from  constants import ROW_ID, READ_REG_A, READ_REG_B, WRITE_REG, INSTRUCTION_TYPE
from constants import InstructionType


ALU_OP = ["shl", "shr", "add", "bsf", "pmovmskb", "psubb", "pslldq", "pcmpeqb", "or", "test", "lea", "add", "pxor", "sub", "and", "cmp", "xor"]
BR_OP = ["jz", "jnz", "jnbe", "jmp"]
LWSW_OP = ["movzx", "mov", "pop", "movsxd", "movdqa", "movlpd", "movhpd"
]

def main():
    assert len(sys.argv) == 2  # check if we got path as arg
    trc_path = sys.argv[1]
    assert os.path.exists(trc_path)  # check there is such file
    df = pd.DataFrame(columns=[ROW_ID, READ_REG_A, READ_REG_B, WRITE_REG, INSTRUCTION_TYPE])
    df.set_index(ROW_ID)

    previous_line = ""
    row_id = 0

    with open(trc_path) as f:
        for line in f:
            inst_type = 0
            inst_write_reg = ""
            read_reg_arr = []
            read_reg_a = ""
            read_reg_b = ""
            inst_type = 4
            same_line_as_before = False
            words = line.split()  # splits into known parts

            # remove redundant words
            words.remove("qword")
            words.remove("dword")
            words.remove("ptr")
            words.remove("byte")
            words.remove("xmmword")

            if line == previous_line:  # the last inst went to the mem, now to the calc part
                if words[1] in ALU_OP:
                    inst_type = InstructionType.ALU
                if words[1] in BR_OP:
                    inst_type = InstructionType.BRANCH
                same_line_as_before = True

            else:
                # if there is [ or 0x in one of the words that mean that we are accesing the memory first in order to get the value
                if any(map(lambda word: word.find('[') != -1, words)):
                    inst_type = InstructionType.LDST
                elif words[1] in ALU_OP:
                    inst_type = InstructionType.ALU
                elif words[1] in BR_OP:
                    inst_type = InstructionType.BRANCH

            for word in words[2:]:
                # the destination is located before the comma, but we need to check it not a mem address
                if word.find(',') != -1 and word.find('[') == -1:
                    inst_write_reg = word[:-1]  # take the dest reg without the comma

            for word in words[2:]:
                if not same_line_as_before:  # if it is the same line as before we don't need to read any register
                    if word.find('[') != -1:  # if we found a [] phrase with regs inside
                        extract_reg(word, read_reg_arr)
                    else:  # if we found a standalone reg as src
                        if word.find(',') != -1:  # if it is next to a comma
                            read_reg_arr.append(word[:-1])
                        else:
                            read_reg_arr.append(word)

            if len(read_reg_arr) == 2:
                read_reg_a = read_reg_arr[0]
                read_reg_b = read_reg_arr[1]
            elif len(read_reg_arr) == 1:
                read_reg_a = read_reg_arr[0]
                read_reg_b = ""
            else:
                read_reg_a = ""
                read_reg_b = ""
            previous_line = line

            # insert only known instructions
            if inst_type != 4:
                new_row = {ROW_ID: row_id, READ_REG_A: read_reg_a, READ_REG_B: read_reg_b,
                           WRITE_REG:inst_write_reg, INSTRUCTION_TYPE:inst_type}
                df2 = df.append(new_row)
                row_id += 1


def extract_reg(string: str, arr: list):
    string = string.replace(',', '')
    string = string.replace('+', ' ')
    string = string.replace('*', ' ')
    string = string.replace('-', ' ')
    sub_strings = string.split()  # splits into known parts
    for sub in sub_strings:
        if sub.find('0x') != -1:   # actual reg and not a number
            arr.append(sub)


if __name__ == "__main__":
    main()
