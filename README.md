# Repository for the paper "Synthesis of realistic stress ECG using GANs"

I recommend reading the paper in order to get a better graps of the idea and scope of the project. They are under the[**docs**](https://github.com/JulianGR/ECG_GAN_Stress/tree/master/docs) folder.

# Preprocessing

1. Download database from [https://physionet.org/content/ecg-spider-clip/1.0.0/](https://physionet.org/content/ecg-spider-clip/1.0.0/)
2. since the database comes in groups, we are going to rename each ECG file from each folder according to this mapping

| **Group2** | **Group3** | **Group4** |
|--------|--------|--------|
| VP02   | VP03   | VP61   |
| VP05   | VP06   | VP62   |
| VP08   | VP09   | VP63   |
| VP11   | VP12   | VP64   |
| VP14   | VP15   | VP65   |
| VP17   | VP18   | VP66   |
| VP20   | VP24   | VP68   |
| VP23   | VP27   | VP69   |
| VP26   | VP30   | VP70   |
| VP29   | VP33   | VP71   |
| VP32   | VP36   | VP72   |
| VP35   | VP39   | VP73   |
| VP38   | VP42   | VP74   |
| VP41   | VP45   | VP75   |
| VP44   | VP48   | VP76   |
| VP47   | VP51   | VP77   |
| VP50   | VP54   | VP78   |
| VP53   | VP57   | VP79   |
| VP56   |        | VP80   |
| VP59   |        |        |

each file is renamed to

| **Group2** | **Group3**| **Group4** |
|--------|--------|--------|
| 0      | 20     | 38     |
| 1      | 21     | 39     |
| 2      | 22     | 40     |
| 3      | 23     | 41     |
| 4      | 24     | 42     |
| 5      | 25     | 43     |
| 6      | 26     | 44     |
| 7      | 27     | 45     |
| 8      | 28     | 46     |
| 9      | 29     | 47     |
| 10     | 30     | 48     |
| 11     | 31     | 49     |
| 12     | 32     | 50     |
| 13     | 33     | 51     |
| 14     | 34     | 52     |
| 15     | 35     | 53     |
| 16     | 36     | 54     |
| 17     | 37     | 55     |
| 18     |        | 56     |
| 19     |        |        |


3. we are going to calculate how many rows are 5 min, and they are approx. 30000 rows. at the end of each recording there were a period od 5 minutres of resting, which we dont want because the GAN will be confused.
	Thus, we store this value for the step 4
	
	
4. we remove the second and the third column (timestamps and RAW annotations) with a linux utility. We also remove the last 5 min wiht the last 30000 rows.
	
	```
	for f in *.txt;  do cut -f2-3 --complement ${f} > rows_${f} ; done;
	for f in rows_*.txt;  do head -n -30000 ${f} > prepared_${f} ; done;	
	```

5. we pass each file to [matlab script](https://github.com/JulianGR/ECG_GAN_Stress/blob/master/preprocessing.m)
6. we pass each file to [pyhton script](https://github.com/JulianGR/ECG_GAN_Stress/blob/master/postprocessing.py)
7. shuffle each file with

	```
	for f in *.csv;  do shuf -o shuffled_${f} < ${f}; done;
	```
	
8.- merge the files of each group into 3 csv files  with  http://merge-csv.com/

9.- shuffle again the merged file for more data decorrelation

# Usage

Download and import into Google Colab [**gcolab.ipynb**](https://github.com/JulianGR/ECG_GAN_Stress/blob/master/gcolab.ipynb)
