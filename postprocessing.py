import csv
from math import ceil
import pandas as pd

THRESHOLD = 0.695


def clean(file_name):
    with open(file_name, newline='', encoding='utf-8') as csvfile, open('clean_' + file_name, 'w', newline='',
                                                                        encoding='utf-8') as f_output:
        file = csv.reader(csvfile)
        data = list(file)
        r = 0
        reached_peak = False
        while not reached_peak:
            if float(data[r][0]) > THRESHOLD:
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
            if float(data[i][0]) > THRESHOLD:
                if data[i] == data[i + 1]:
                    peaks_index_list.append(i)
                    data.pop(i + 1)
                    i = i - 1

            i = i + 1
        csv_output = csv.writer(f_output)
        csv_output.writerows(data)
    return peaks_index_list, 'peaks_' + file_name


def get_avg_distance_peaks(peaks_index_list):
    i = 0
    distance_t = []
    while i < len(peaks_index_list) - 2:
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
        data = list(file)
        i = 0
        while i <= len(peaks_index_list) - 2:
            j = peaks_index_list[i]
            tmp = data[0][j:j+one_dot_two_t]
            csv_output = csv.writer(f_output)
            csv_output.writerow(tmp)
            i = i + 2

    return 'cut_' + file_name


def padding(file_name):
    with open(file_name, newline='', encoding='utf-8') as csvfile, open('pad_' + file_name, 'w', newline='',
                                                                        encoding='utf-8') as f_output:
        file = csv.reader(csvfile)
        data = []
        for row in file:
            data.append(row)
            n = 188 - len(data[0])
            list_of_zeros = [0] * n
            wr = csv.writer(f_output)
            tmp = data[0] + list_of_zeros
            wr.writerow(tmp)
            data = []


def main():
    file_name = "bitalino_proc0 - copia.csv"
    clean_file = clean(file_name)
    peaks_index_list, file_name = peaks(clean_file)
    one_dot_two_t = get_avg_distance_peaks(peaks_index_list)
    transposed = transpose_csv(file_name)
    cut_file = cut(transposed, one_dot_two_t, peaks_index_list)
    padding(cut_file)


if __name__ == "__main__":
    main()
