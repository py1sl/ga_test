""" """

import numpy as np
import gacore
import process_results


def calc_fitness(flist):
    ave_fit = 0
    ave_ndose = 0
    ave_pdose = 0
    max_fit = 0
    min_ndose = 0
    min_pdose = 0
    fit = []
    ndose = []
    pdose = []

    summ_data = [ave_fit, ave_ndose, ave_pdose, max_fit, min_ndose, min_pdose]

    return summ_data


def generate_new_pop(psize, fitness):
    """ """
    pop = []
    return pop


if __name__ == "__main__"  :

    condata, old_pop = gacore.read_control_file()
    indata = gacore.read_input_file(condata[0])
    gen = int(condata[1]) + 1
    ofile_list = gacore.get_output_file_list()
    fitness, summary_data = calc_fitness(ofile_list)
    new_pop = generate_new_pop(fitness)
    gacore.gen_tidy(condata[1], old_pop)
