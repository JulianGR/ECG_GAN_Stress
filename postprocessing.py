import csv
from math import ceil
import pandas as pd
import numpy as np
import os

UPPER_THRESHOLD = 0.55
UNDER_THRESHOLD = 0.35


def get_max(file_name):
    with open(file_name, newline='', encoding='utf-8') as csvfile:
        file = csv.reader(csvfile)
        data_unp = list(file)
        data = np.array(data_unp[0], dtype=np.float32)

        avg = sum(data) / len(data)
        std_deviation = np.std(data)

        global UPPER_THRESHOLD
        UPPER_THRESHOLD = 1.25 * std_deviation + avg

        global UNDER_THRESHOLD
        UNDER_THRESHOLD = avg - 1 * std_deviation

        print(UPPER_THRESHOLD)
        print(UNDER_THRESHOLD)


def clean(file_name):
    with open(file_name, newline='', encoding='utf-8') as csvfile, open('clean_' + file_name, 'w', newline='',
                                                                        encoding='utf-8') as f_output:
        file = csv.reader(csvfile)
        data_unp = list(file)
        data = np.array(data_unp, dtype=np.float32)

        r = 0
        reached_peak = False
        while not reached_peak:
            if float(data[r][0]) > UPPER_THRESHOLD:
                reached_peak = True

            else:
                r = r + 1

        csv_output = csv.writer(f_output)
        csv_output.writerows(data[r:None])
    return 'clean_' + file_name


def peaks(file_name):
    peaks_index_list = []
    with open(file_name, newline='', encoding='utf-8') as csvfile, open('peaks_' + file_name, 'w', newline='',
                                                                        encoding='utf-8') as f_output:
        file = csv.reader(csvfile)
        data = list(file)

        i = 0
        while i < len(data) - 2:

            if float(data[i][0]) > UPPER_THRESHOLD:
                if data[i][0] > data[i + 1][0]:
                    if (float(data[i + 1][0]) < UNDER_THRESHOLD) | (float(data[i + 2][0]) < UNDER_THRESHOLD) | (float(data[i + 3][0]) < UNDER_THRESHOLD):
                        peaks_index_list.append(i)
                        data.pop(i + 1)
                        i = i - 1

            if float(data[i][0]) < UNDER_THRESHOLD:
                if data[i][0] < data[i + 1][0]:
                    data.pop(i + 1)
                    i = i - 1

            i = i + 1
        csv_output = csv.writer(f_output)
        csv_output.writerows(data)
    return peaks_index_list, 'peaks_' + file_name


def get_avg_distance_peaks(peaks_index_list):
    i = 0
    distance_t = []
    while i <= len(peaks_index_list) - 2:
        distance_t.append(peaks_index_list[i + 1] - peaks_index_list[i])
        i = i + 1

    t = sum(distance_t) / len(distance_t)
    one_dot_two_t = ceil(1.2 * t)
    return one_dot_two_t


def transpose_csv(file_name):
    pd.read_csv(file_name, header=None).T.to_csv('transposed_' + file_name, header=False, index=False)
    return 'transposed_' + file_name


def cut(file_name, one_dot_two_t, peaks_index_list):
    with open(file_name, newline='', encoding='utf-8') as csvfile, open('cut_' + file_name, 'w', newline='',
                                                                        encoding='utf-8') as f_output:
        file = csv.reader(csvfile)
        data_unp = list(file)
        data = np.array(data_unp, dtype=np.float32)
        i = 0
        while i <= len(peaks_index_list) - 2:
            j = peaks_index_list[i]
            tmp = data[0][j:j + one_dot_two_t]
            csv_output = csv.writer(f_output)
            csv_output.writerow(tmp)
            i = i + 2

    return 'cut_' + file_name


def padding(cut_file, file_name):
    with open(cut_file, newline='', encoding='utf-8') as csvfile, open('processed_' + file_name, 'w', newline='',
                                                                       encoding='utf-8') as f_output:
        file = csv.reader(csvfile)
        data = []
        for row in file:
            data.append(row)
            n = 140 - len(data[0])
            list_of_zeros = [0] * n
            wr = csv.writer(f_output)
            tmp = data[0] + list_of_zeros
            wr.writerow(tmp)
            data = []


def mark(file_name):
    with open(file_name, 'a', newline='', encoding='utf-8') as csvfile, open('processed_' + file_name, 'a', newline='',
                                                                             encoding='utf-8') as f_output:
        wr = csv.writer(f_output)
        data = [str(file_name)]
        wr.writerow(data)


def main():
    one_dot_two_list = []
    peaks_list = []

    i = 0
    while i <= 56:
        file_name = "bitalino_proc" + str(i) + ".csv"
        transposed_file = transpose_csv(file_name)
        get_max(transposed_file)
        clean_file = clean(file_name)
        peaks_index_list, peaks_file = peaks(clean_file)
        one_dot_two_t = get_avg_distance_peaks(peaks_index_list)
        transposed_file = transpose_csv(peaks_file)
        cut_file = cut(transposed_file, one_dot_two_t, peaks_index_list)
        padding(cut_file, file_name)
        # mark(file_name)
        os.remove(clean_file)
        os.remove(peaks_file)
        os.remove(transposed_file)
        os.remove(cut_file)

        peaks_list.append(len(peaks_index_list))
        one_dot_two_list.append(one_dot_two_t)
        print("======" + str(i) + "=====")
        print(peaks_list)
        print(one_dot_two_list)
        print(max(peaks_list))
        print(sum(peaks_list) / len(peaks_list))
        print(max(one_dot_two_list))

        i = i + 1


# merge all in http://merge-csv.com/

if __name__ == "__main__":
    main()
