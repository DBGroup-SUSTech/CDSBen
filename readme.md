# CDSBen: Benchmarking the Performance of Storage Services in Cloud-native Database System at ByteDance

This repository contains the implementation of *CDSBen* published in VLDB'2023.

## Structure Overview

```
./
|-YCSB-master                     # YCSB implementation, which can be adapted to generate and execute I/O workloads on the storage tier. For up-to-date YCSB, please refer to https://github.com/brianfrankcooper/YCSB.
|-benchbase-main                  # Benchbase implementation we used to generate TPC-C transaction workloads on the compute tier. For up-to-date benchbase, please refer to https://github.com/cmu-db/benchbase.
|-models.py                       # Implementation of the models in CDSBen.
|-ycsb_adaptation_instruction.md  # General instructions on how to adapt YCSB for CDSBen.
```

## Reference

If you use our code, please cite our paper:

```
@article{10.14778/3611540.3611549,
author = {Zhang, Jiashu and Jiang, Wen and Tang, Bo and Ma, Haoxiang and Cao, Lixun and Jiang, Zhongbin and Nie, Yuanyuan and Wang, Fan and Zhang, Lei and Liang, Yuming},
title = {CDSBen: Benchmarking the Performance of Storage Services in Cloud-native Database System at ByteDance},
year = {2023},
issue_date = {August 2023},
publisher = {VLDB Endowment},
volume = {16},
number = {12},
issn = {2150-8097},
journal = {PVLDB},
pages = {3584 - 3596},
numpages = {13}
}
```
