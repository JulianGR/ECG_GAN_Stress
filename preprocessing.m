for i = 0:56
noProcPartialFilename = 'BitalinoECG_';


noProcFilename = append(append(noProcPartialFilename, int2str(i)),'.txt');
matrix = readmatrix(noProcFilename);
onlyECG = matrix(:,1);


filteredECG = medfilt1(onlyECG);
normalizedECG = mat2gray(filteredECG);

procPartialFilename= 'bitalino_proc';
procFilename = append(append(procPartialFilename, int2str(i)), '.csv');

csvwrite(procFilename,normalizedECG);
end