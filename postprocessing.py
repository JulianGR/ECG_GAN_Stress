import csv
from math import ceil
import pandas as pd
import numpy as np
import os

UPPER_THRESHOLD = 0.55
UNDER_THRESHOLD = 0.35

#set thresholds
def get_max(file_name):
    with open(file_name, newline='', encoding='utf-8') as csvfile:
        file = csv.reader(csvfile)
        data_unp = list(file)
        data = np.array(data_unp[0], dtype=np.float32)

        avg = sum(data) / len(data)
        std_deviation = np.std(data)

        global UPPER_THRESHOLD
        global UNDER_THRESHOLD

        #difference between peaks and average too high for other methods to handle
        if std_deviation > 0.075:
            UPPER_THRESHOLD = 1 * std_deviation + avg
            UNDER_THRESHOLD = avg - 0.2 * std_deviation

        else:
            UPPER_THRESHOLD = 1.2 * std_deviation + avg
            UNDER_THRESHOLD = avg - 0.6 * std_deviation

#remove data from the beginning until the first peak of each file
def clean(file_name):
    with open(file_name, newline='', encoding='utf-8') as csvfile, open('clean_' + file_name, 'w', newline='',
                                                                        encoding='utf-8') as f_output:
        file = csv.reader(csvfile)
        data_unp = list(file)
        data = np.array(data_unp, dtype=np.float32)

        i = 0
        reached_peak = False

        while not reached_peak:
            over_th = float(data[i][0]) > UPPER_THRESHOLD
            next_smaller = data[i][0] > data[i - 1][0]
            next_under_th = (float(data[i + 1][0]) < UNDER_THRESHOLD) | (float(data[i + 2][0]) < UNDER_THRESHOLD)

            if over_th & next_smaller & next_under_th:
                reached_peak = True

            i = i + 1

        csv_output = csv.writer(f_output)
        csv_output.writerows(data[i:None])
    return 'clean_' + file_name

#get a list with the indexed of all peaks
def peaks(file_name):
    peaks_index_list = []
    with open(file_name, newline='', encoding='utf-8') as csvfile, open('peaks_' + file_name, 'w', newline='',
                                                                        encoding='utf-8') as f_output:
        file = csv.reader(csvfile)
        data_unp = list(file)
        data = np.array(data_unp, dtype=np.float32)

        i = 0
        while i < len(data) - 2:

            over_th = float(data[i][0]) > UPPER_THRESHOLD
            next_smaller = data[i][0] > data[i - 1][0]
            next_under_th = (float(data[i + 1][0]) < UNDER_THRESHOLD) | (float(data[i + 2][0]) < UNDER_THRESHOLD)

            if over_th & next_smaller & next_under_th:
                peaks_index_list.append(i)

            i = i + 1
        csv_output = csv.writer(f_output)
        csv_output.writerows(data)
    return peaks_index_list, 'peaks_' + file_name

# get average distance between the indexes using the peaks list
def get_avg_distance_peaks(peaks_index_list):
    i = 0
    skip_file = False
    distance_t = []
    while i <= len(peaks_index_list) - 2:
        distance_t.append(peaks_index_list[i + 1] - peaks_index_list[i])
        i = i + 1

    t = sum(distance_t) / len(distance_t)
    one_dot_two_t = ceil(1.2 * t)
#there are some files that exceed 150 columns by a lot - they are removed (only happens with a couple of them)
    if one_dot_two_t > 150:
        skip_file = True
    return one_dot_two_t, skip_file


def transpose_csv(file_name):
    pd.read_csv(file_name, header=None).T.to_csv('transposed_' + file_name, header=False, index=False)
    return 'transposed_' + file_name

#cut the series using the peaks list and the average distance
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

#pad with zeroes until 150 columns (arbitrary* value)
def padding(cut_file, file_name):
    with open(cut_file, newline='', encoding='utf-8') as csvfile, open('processed_' + file_name, 'w', newline='',
                                                                       encoding='utf-8') as f_output:
        file = csv.reader(csvfile)
        data = []
        for row in file:
            data.append(row)
            n = 150 - len(data[0])
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
    one_dot_two_list = []
    peaks_list = []
    skipped_file = []

    i = 0
    while i <= 56:
        file_name = "bitalino_proc" + str(i) + ".csv"
        transposed_file = transpose_csv(file_name)
        get_max(transposed_file)
        os.remove(transposed_file)
        clean_file = clean(file_name)
        peaks_index_list, peaks_file = peaks(clean_file)
        one_dot_two_t, skip_file = get_avg_distance_peaks(peaks_index_list)

        if skip_file:
            skipped_file.append(file_name)
            os.remove(clean_file)
            os.remove(peaks_file)
            i = i + 1
            continue

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
        print("=========" + str(i) + "========")
        print("UPPER_THRESHOLD: " + str(UPPER_THRESHOLD))
        print("UNDER_THRESHOLD: " + str(UNDER_THRESHOLD))
        print("peaks_list: " + str(peaks_list))
        print("one_dot_two_list: " + str(one_dot_two_list))
        print("max(peaks_list): " + str(max(peaks_list)))
        print("sum(peaks_list) / len(peaks_list): " + str(sum(peaks_list) / len(peaks_list)))
        print("max(one_dot_two_list): " + str(max(one_dot_two_list)))
        print("Skipped files: " + str(skipped_file))

        i = i + 1


if __name__ == "__main__":
    main()
