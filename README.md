# Repository for the paper "Synthesis of realistic stress ECG using GANs"

I recommend reading the paper in order to get a better graps of the idea and scope of the project. They are under the [**docs**](https://github.com/JulianGR/ECG_GAN_Stress/tree/master/docs) folder.

# Preprocessing

1. Download database from [https://physionet.org/content/ecg-spider-clip/1.0.0/](https://physionet.org/content/ecg-spider-clip/1.0.0/)
2. since the database comes in groups, we are going to rename each ECG file from each folder according to this mapping

| Group2 -> | Renaming of g2 | Group3 -> | Renaming of g3 | Group4 -> | Renaming of g4 |
|-----------|----------------|-----------|----------------|-----------|----------------|
| VP02      | 0              | VP03      | 20             | VP61      | 38             |
| VP05      | 1              | VP06      | 21             | VP62      | 39             |
| VP08      | 2              | VP09      | 22             | VP63      | 40             |
| VP11      | 3              | VP12      | 23             | VP64      | 41             |
| VP14      | 4              | VP15      | 24             | VP65      | 42             |
| VP17      | 5              | VP18      | 25             | VP66      | 43             |
| VP20      | 6              | VP24      | 26             | VP68      | 44             |
| VP23      | 7              | VP27      | 27             | VP69      | 45             |
| VP26      | 8              | VP30      | 28             | VP70      | 46             |
| VP29      | 9              | VP33      | 29             | VP71      | 47             |
| VP32      | 10             | VP36      | 30             | VP72      | 48             |
| VP35      | 11             | VP39      | 31             | VP73      | 49             |
| VP38      | 12             | VP42      | 32             | VP74      | 50             |
| VP41      | 13             | VP45      | 33             | VP75      | 51             |
| VP44      | 14             | VP48      | 34             | VP76      | 52             |
| VP47      | 15             | VP51      | 35             | VP77      | 53             |
| VP50      | 16             | VP54      | 36             | VP78      | 54             |
| VP53      | 17             | VP57      | 37             | VP79      | 55             |
| VP56      | 18             |           |                | VP80      | 56             |
| VP59      | 19             |           |                |           |                |

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
