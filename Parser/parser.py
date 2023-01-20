import pickle
import pandas as pd
import sys
import os
from constants import ROW_ID, READ_REG_A, READ_REG_B, WRITE_REG, INSTRUCTION_TYPE
from constants import InstructionType
from tqdm import tqdm
import warnings

ALU_OP = ["shl", "bt", "cpuid", "punpcklbw", "mov", "setz", "rol", "por", "psrldq", "cmovb", "cmovbe", "setbe", "punpcklwd", "pminub",
          "not", "pshufd", "pcmpeqb", "sbb", "imul", "mul", "cmovnz", "setnz", "cmovz", "xchg", "sar", "cdqe", "rdtsc",
          "shr", "add", "bsf", "pmovmskb", "psubb", "pslldq", "shl", "pcmpeqb", "or", "test", "lea", "add", "pxor",
          "sub", "and", "cmp", "xor", "neg", "movq", "cmovb", "movsx", "cmovbe", "movaps", "movlpd", "movdqu", "movd",
           "movsxd", "movdqa", "movups", "movlpd", "movhpd", "movzx", "pcmpeqb"]
BR_OP = ["jz", "jnz", "js", "jnbe", "jnb", "jmp", "jnle", "jbe", "jb", "jle", "jns", "jl"]
LWSW_OP = ["movzx", "pcmpeqb", "mov", "pop", "movq", "cmovb", "movsx", "cmovbe", "movaps", "movlpd", "movdqu", "movd",
           "movsxd", "movdqa", "movups", "movlpd", "movhpd", "push", ]
# TODO: is jmp a conditional jmp or not?
# TODO: what is the type of rdtsc ()read time stamp
# TODO: stosb is displaying a lot in deep trc should we ignore it?


def main():
    assert len(sys.argv) == 2  # check if we got path as arg
    trc_path = sys.argv[1]
    assert os.path.exists(trc_path)  # check there is such file
    df = pd.DataFrame(columns=[ROW_ID, READ_REG_A, READ_REG_B, WRITE_REG, INSTRUCTION_TYPE])

    warnings.filterwarnings("ignore")

    previous_line = ""
    row_id = 0
    chunk_counter = 0
    with open(trc_path) as f:
        num_lines = len(f.readlines())

    with open(trc_path) as f:
        for line in tqdm(f, total=num_lines):
            inst_write_reg = ""
            read_reg_arr = []
            read_reg_a = ""
            read_reg_b = ""
            inst_type = 4
            same_line_as_before = False
            words = line.split()  # splits into known parts
            calc_inner_part = False
            # remove redundant words
            if "qword" in words:
                words.remove("qword")
            if "dword" in words:
                words.remove("dword")
            if "ptr" in words:
                words.remove("ptr")
            if "byte" in words:
                words.remove("byte")
            if "xmmword" in words:
                words.remove("xmmword")
            if words[1] == "ret":
                continue

            if "stosb" in words:
                # continue
                if "byte" == words[3]:
                    read_reg_a = "al"
                if "word" == words[3]:
                    read_reg_a = "ax"
                if "dword " == words[3]:
                    read_reg_a = "eax"

                read_reg_b = "ax"
                inst_type = InstructionType.LDST
                new_row = {ROW_ID: row_id, READ_REG_A: read_reg_a, READ_REG_B: read_reg_b,
                           WRITE_REG: inst_write_reg, INSTRUCTION_TYPE: inst_type}
                df = df.append(new_row, ignore_index=True)
                row_id += 1
                continue
            # find the type of the instruction
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
                    calc_inner_part = True
                elif words[1] == "pop" or words[1] == "push":
                    inst_type = InstructionType.LDST
                elif words[1] in ALU_OP:
                    inst_type = InstructionType.ALU
                elif words[1] in BR_OP:
                    inst_type = InstructionType.BRANCH

            # find the writing target of the instruction
            if not calc_inner_part or "mov" in words[1] or words[1] == "lea":
                for word in words[2:]:
                    # the destination is located before the after the op and before the comma,
                    # but we need to check it not a mem address if so we don't hav ea dependency
                    if word.find(',') != -1 and word.find('[') == -1:
                        inst_write_reg = word[:-1]  # take the dest reg without the comma
                if words[1] == "pop":  # unique command behavior
                    inst_write_reg = words[2]


            # find the src of the regs
            if not same_line_as_before:  # if it is the same line as before we don't need to read any register
                for word in words[2:]:
                    if word.find('[') != -1:  # if we found a [] phrase with regs inside
                        extract_reg(word, read_reg_arr)
                    elif "0x" not in word and (not calc_inner_part or "mov" in words[1]):  # if we found a standalone reg as src
                        if word.find(',') != -1:  # if it is next to a comma remove it
                            if "mov" not in words[1]:  # and if its a mov op there is no need to read the first one
                                read_reg_arr.append(word[:-1])
                        else:
                            read_reg_arr.append(word)
            else:
                read_reg_arr.append(words[2][:-1])

            if len(read_reg_arr) == 2:
                read_reg_a = read_reg_arr[0]
                read_reg_b = read_reg_arr[1]
            elif len(read_reg_arr) == 1:
                read_reg_a = read_reg_arr[0]
                read_reg_b = ""
            else:
                read_reg_a = ""
                read_reg_b = ""

            # insert only known instructions into the dataframe
            if inst_type != 4:
                new_row = {ROW_ID: row_id, READ_REG_A: read_reg_a, READ_REG_B: read_reg_b,
                           WRITE_REG: inst_write_reg, INSTRUCTION_TYPE: inst_type}
                df = df.append(new_row, ignore_index=True)
                row_id += 1
            previous_line = line

            if row_id % 10000 == 9999:
                with open("output_trc/" + trc_path.replace(".trc", f"_{chunk_counter}.pkl"), "wb") as data_f:
                    # df.set_index(ROW_ID)
                    pickle.dump(df, data_f)
                chunk_counter += 1
                df = pd.DataFrame(columns=[ROW_ID, READ_REG_A, READ_REG_B, WRITE_REG, INSTRUCTION_TYPE])
    with open("output_trc/" + trc_path.replace(".trc", f"_{chunk_counter}.pkl"), "wb") as data_f:
        # df.set_index(ROW_ID)
        pickle.dump(df, data_f)


def extract_reg(string: str, arr: list):
    string = string.replace(',', '')
    string = string.replace('+', ' ')
    string = string.replace('*', ' ')
    string = string.replace('-', ' ')
    string = string.replace('[', ' ')
    string = string.replace(']', ' ')

    sub_strings = string.split()  # splits into known parts
    for sub in sub_strings:
        if sub.find('0x') == -1:  # actual reg and not a number
            arr.append(sub)


if __name__ == "__main__":
    main()
