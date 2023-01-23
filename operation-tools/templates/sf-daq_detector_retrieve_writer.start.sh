#!/bin/bash

if [ $# != 1 ]
then
    systemctl start sf-daq_detector_retrieve_writer@{01..{{ number_of_detector_retrieve_writers}}}
    exit
fi

source /home/dbe/miniconda3/etc/profile.d/conda.sh
conda deactivate
conda activate sf-daq

M=$1
C={{ detector_retrieve_cores }}

export OMP_NUM_THREADS=5
export NUMBA_NUM_THREADS=5

taskset -c $C python /home/dbe/git/sf_daq_broker/sf_daq_broker/writer/start.py  --writer_id $M  --writer_type 1
