import csv
from math import ceil
import pandas as pd
import numpy as np
import os


# get average distance between the indexes using the peaks file
def get_avg_distance_peaks(peaks):
    i = 0
    distance_t = []
    while i <= len(peaks) - 2:
        distance_t.append(peaks[i + 1] - peaks[i])
        i = i + 1

    t = sum(distance_t) / len(distance_t)
    one_dot_two_t = ceil(1.2 * t)

    return one_dot_two_t


def transpose_csv(file_name):
    pd.read_csv(file_name, header=None).T.to_csv('transposed_' + file_name, header=False, index=False)
    return 'transposed_' + file_name


# cut the series using the peaks list and the average distance
def cut(file_name, one_dot_two_t, peaks):
    with open(file_name, newline='', encoding='utf-8') as csvfile, open('cut_' + file_name, 'w', newline='',
                                                                        encoding='utf-8') as f_output:
        file = csv.reader(csvfile)
        data_unp = list(file)
        data = np.array(data_unp, dtype=np.float32)
        i = 0

        while i <= len(peaks) - 2:
            j = peaks[i]
            tmp = data[0][j:j + one_dot_two_t]
            csv_output = csv.writer(f_output)
            csv_output.writerow(tmp)
            i = i + 2

    return 'cut_' + file_name


# pad with zeroes until 191 columns (arbitrary* value)
def padding(cut_file, file_name):
    with open(cut_file, newline='', encoding='utf-8') as csvfile, open('processed_' + file_name, 'w', newline='',
                                                                       encoding='utf-8') as f_output:
        file = csv.reader(csvfile)
        data = []
        for row in file:
            data.append(row)
            n = 191 - len(data[0])
            list_of_zeros = [0.0000] * n
            wr = csv.writer(f_output)
            tmp = data[0] + list_of_zeros
            wr.writerow(tmp)
            data = []


#debugging function
def mark(file_name):
    with open(file_name, 'a', newline='', encoding='utf-8') as csvfile, open('processed_' + file_name, 'a', newline='',
                                                                             encoding='utf-8') as f_output:
        wr = csv.writer(f_output)
        data = [str(file_name)]
        wr.writerow(data)


def main():
    i = 1
    while i <= 45:
        file_name = "final_" + str(i) + ".csv"
        peaks_name = "peaks_" + str(i) + ".csv"

        transposed_peaks = transpose_csv(peaks_name)
        transposed_file = transpose_csv(file_name)

        with open(transposed_peaks, newline='', encoding='utf-8') as csvfile:
            file = csv.reader(csvfile)
            data_unp = list(file)
            peaks = np.array(data_unp[0], dtype=np.int32)

            one_dot_two_t = get_avg_distance_peaks(peaks)
            cut_file = cut(transposed_file, one_dot_two_t, peaks)
            padding(cut_file, file_name)
            mark(file_name)

            os.remove(transposed_file)
            os.remove(transposed_peaks)
            os.remove(cut_file)

            print("=== Processing file " + str(i) + " ===")
            i = i + 1


if __name__ == "__main__":
    main()
