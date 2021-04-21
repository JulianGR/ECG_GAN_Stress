#!/usr/bin/bash

FILES="100 102 103 104 105 106 107 108 109 111 112 113 114 115 116 117 118 119 121 122 123 124 200 201 202 203 205 207 208 209 210 212 214 215 217 219 220 221 222 223 230 231 232 233 234 "

counter=1

for f in $FILES
do
    echo "=== Processing file ${f} ===";
    rdsamp -r ${f}_alt -c > ${counter}.csv;
    cut -d, -f1 --complement ${counter}.csv > rows_${counter}.csv
    rm ${counter}.csv
    counter=$((counter+1));
done