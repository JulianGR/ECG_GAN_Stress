# Preprocessing for the original paper

The original paper is (https://arxiv.org/abs/1909.09150), whose processing is detailed in (https://arxiv.org/abs/1805.00794). 
Since the authors of the second paper were the ones doing the preprocessing, I contacted them politely asking for the code of the preprocessing. They decided that it won't be released, so I coded my version.
It might not give the same results as their code, but its the best approximation I came with.


# Preprocessing

1. Download database from (https://physionet.org/content/mitdb/1.0.0/)
2. Run ```firt-run.sh```
3. Run ```resample.sh```
4. Run ```prepare.sh```
5. Run ```preprocessing.m```
6. Run ```main.py```

7. shuffle each file with

	```
	for f in *.csv;  do shuf -o shuffled_${f} < ${f}; done;
	```
	
8.- merge the files of each group into 3 csv files  with  http://merge-csv.com/

9.- shuffle again the merged file for more data decorrelation

# Usage

Download and import into Google Colab [**gcolab.ipynb**](https://github.com/JulianGR/ECG_GAN_Stress/blob/master/gcolab.ipynb)
