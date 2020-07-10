for i = 0:56
noProcPartialFilename = 'prepared_rows_BitalinoECG_';

noProcFilename = append(append(noProcPartialFilename, int2str(i)),'.txt');
matrix = readmatrix(noProcFilename);
onlyECG = matrix(:,1);

normalizedECG = mat2gray(onlyECG);

procPartialFilename= 'bitalino_proc';
procFilename = append(append(procPartialFilename, int2str(i)), '.csv');

csvwrite(procFilename,normalizedECG);
end