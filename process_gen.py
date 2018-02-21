""" """

import numpy as np
import random
import gacore
import process_results


def calc_fitness(flist):
    ave_fit = 0
    ave_ndose = 0
    ave_pdose = 0
    fit = {}
    ndoses = []
    pdoses = []

    for f in flist:
        flines = gacore.get_lines(f)
        ndose, nerr = process_results.get_tally_res(flines, " 4")
        pdose, perr = process_results.get_tally_res(flines, "14")
        fitness = 1.0/(ndose + pdose)
        fdict = {f: fitness}
        fit.update(fdict)
        ndoses.append(ndose)
        pdoses.append(pdose)

    max_fit = max(fit.values())
    min_ndose = min(ndoses)
    min_pdose = min(pdoses)
    ave_fit = sum(fit.values()) / (1.0 * len(fit))
    ave_ndose = sum(ndoses) / (1.0 * len(ndoses))
    ave_pdose = sum(pdoses) / (1.0 * len(pdoses))

    summ_data = [ave_fit, ave_ndose, ave_pdose, max_fit, min_ndose, min_pdose]

    return fit, summ_data


def mate(p1, p2, fitness):
    """ """
    arr = []
    p1_fit = fitness[p1]
    p2_fit = fitness[p2]
    p1_prob = p1_fit / (p1_fit + p2_fit)
    p1 = gacore.convert_to_seq(p1)
    p2 = gacore.convert_to_seq(p2)

    i = 0
    while i < len(p1):
        rn = np.random.random()
        if rn < p1_prob:
            arr.append(p1[i])
        else:
            arr.append(p2[i])
        i = i + 1

    return arr


def generate_new_pop(psize, fitness, indata):
    """ """
    pop = []
    mutate_arr = []
    mats = {0: " ", 1: -2.66, 2: -2.3, 3: -5.9, 4: -8.96, 5: -19.3,
            6: -11.35, 7: -0.93, 8: -7.15, 9: -7.82, 10: -0.998207}
    i = 0
    mcnp_tmp = gacore.get_lines(indata[0])
    while i < psize:
        p1 = random.choice(list(fitness.keys()))
        p2 = random.choice(list(fitness.keys()))
        arr = mate(p1, p2, fitness)
        arr, mcount = mutate(arr, indata[6])
        fname = gacore.write_mcnp_file(arr, mcnp_tmp, indata[8],
                                       indata[7], mats)
        # check if already in this pop
        if fname in pop:
            i = i - 1
        else:
            pop.append(fname)
            mutate_arr.append(mcount)
        i = i + 1
    return pop, mutate_arr


def mutate(arr, mutate_prob):
    """ """
    mutate_count = 0
    new_arr = []
    for g in arr:
        rn = np.random.random()
        if rn < mutate_prob:
            new_arr.append(np.random.randint(0, 10))
            mutate_count = mutate_count + 1
        else:
            new_arr.append(g)

    return new_arr, mutate_count


def cull(fit_dict, ave_fit, threshold):
    """remove a fraction of population below threshold """
    cvalue = ave_fit * threshold
    c_count = 0

    new_fit_dict = {}
    for seq, val in fit_dict.items():
        if val > cvalue:
            fdict = {seq: val}
            new_fit_dict.update(fdict)
        else:
            c_count = c_count + 1

    return new_fit_dict, c_count


if __name__ == "__main__":

    condata, old_pop = gacore.read_control_file()
    indata = gacore.read_input_file(condata[0])
    gen = int(condata[1]) + 1
    ofile_list = gacore.get_output_file_list()
    fitness, summary_data = calc_fitness(ofile_list)
    fitness, c_count = cull(fitness, summary_data[0], indata[9])
    gacore.gen_tidy(condata[1], old_pop)
    new_pop, mlist = generate_new_pop(indata[1], fitness, indata)

    gacore.write_run_scripts(new_pop, indata[5], indata[3], indata[2],
                             indata[4])
    gacore.write_control_file(gen, new_pop, condata[0])

    data = str(gen) + ", " + str(summary_data[0]) + ", " + str(
           summary_data[1]) + ", " + str(summary_data[2])
    gacore.update_results("results.txt", data)
