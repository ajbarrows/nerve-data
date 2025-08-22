# NERVE Lab Data Sets


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

    Total Subjects: 93

    | session   |   anat |   dwi |   fmap |   func |   motion |   mrs |
    |:----------|-------:|------:|-------:|-------:|---------:|------:|
    | ses-V02   |     70 |    61 |     65 |     70 |       75 |    41 |
    | ses-V03   |      8 |     8 |      9 |      9 |        8 |     2 |
