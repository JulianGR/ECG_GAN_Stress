for i = 1:45
        
noProcPartialFilename = 'rows_';

noProcFilename = append(append(noProcPartialFilename, int2str(i)),'.csv');
matrix = readmatrix(noProcFilename);
onlyECG = matrix(:,1);

[qrs_amp_raw,qrs_i_raw,delay] = pan_tompkin(onlyECG, 125, 0);
tras_indexes = transpose(qrs_i_raw);

normalizedECG = rescale(onlyECG);


disp("First cell from file " + int2str(i) + ": " + normalizedECG(1,1))

procPartialFilename= 'final_';
procFilename = append(append(procPartialFilename, int2str(i)), '.csv');

procPartialFilename2= 'peaks_';
procFilename2 = append(append(procPartialFilename2, int2str(i)), '.csv');


dlmwrite(procFilename, normalizedECG, 'delimiter', ',', 'precision', 6)
dlmwrite(procFilename2, tras_indexes, 'delimiter', ',', 'precision', 6)
end


