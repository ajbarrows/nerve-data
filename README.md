# NERVE Lab Data Sets


Current path for UVM VACC users: `/users/a/j/ajbarrow/scratch/data`

Datasets are all [BIDS](https://bids.neuroimaging.io) compliant (at
least in structure), with one notable exception: `.parquet` files are
included in addition to `.tsv` files where appropriate.

## HBCD

### 1.0

Download date: 2025-08-22

Structure:

    HBCD/1.0/
    ├── dataset_description.json
    ├── derivatives
    │   ├── hdcc
    │   └── nerve
    ├── participants.json
    ├── participants.tsv
    ├── phenotype
    │   ├── {phenotype1}.json
    │   ├── {phenotype1}.parquet
    │   └── {phenotype1}.parquet
    ├── sub-{subject_id}
    │   ├── ses-V02
    │   │   ├── anat
    │   │   ├── dwi
    │   │   ├── fmap
    │   │   ├── func
    │   │   ├── motion
    │   │   └── mrs
    │   └── ses-V03
    │       ├── anat
    │       ├── dwi
    │       ├── eeg
    │       ├── fmap
    │       ├── func
    │       └── motion

- Derivatives include tabulated iamging data
  - HDCC pipeline is “HBCD Data Coordinating Center”
  - NERVE is NERVE Lab-derived files (see derivatives folder for more
    information)

<!-- -->

    Total Subjects: 602

    | session   |   anat |   dwi |   eeg |   fmap |   func |   motion |   mrs |
    |:----------|-------:|------:|------:|-------:|-------:|---------:|------:|
    | ses-V02   |    546 |   483 |     0 |    508 |    513 |      497 |   302 |
    | ses-V03   |     75 |    63 |    81 |     71 |     71 |       82 |    38 |
