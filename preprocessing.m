test = csvread('lol.csv');
med = medfilt1(test);
ntest = mat2gray(med);
csvwrite('filename.csv',ntest);