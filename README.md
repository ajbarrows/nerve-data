# NERVE Lab Data Sets


Current path for UVM VACC users: `/users/a/j/ajbarrow/scratch/data`

Datasets are all [BIDS](https://bids.neuroimaging.io) compliant (at
least in structure), with one notable exception: `.parquet` files are
included in addition to `.tsv` files where appropriate.

All data come from the [NBCD Data Hub](https://www.nbdc-datahub.org).

## [HBCD](https://heal.nih.gov/research/infants-and-children/healthy-brain)

- [Release Docs](https://docs.hbcdstudy.org/latest/)
- [Data Dictionary (DEAP)](https://hbcd.deapscience.com/#/home)
- [Volkow et al. (2024)](https://pubmed.ncbi.nlm.nih.gov/39098249/)
- [Developmental Cognitive Neuroscience Special
  Issue](https://www.sciencedirect.com/special-issue/10VNSS1BBLV)

### 1.0

Citation:

    @misc{https://doi.org/10.82525/qv5x-qx11,
      doi = {10.82525/QV5X-QX11},
      url = {https://nbdc-datahub.org/hbcd-release-1-0},
      author = {Chambers,  C and Nelson,  C and Dale,  A and Fair,  D and Smyser,  C and Acheson,  A and Bakhireva,  L and Bandoli,  G and Bell,  MA and Berry,  U and Bogdan,  R and Bosquet Enlow,  M and Coles,  C and Croff,  J and Cutting,  L and Dean,  D and DeMauro,  S and Engel,  S and Fox,  N and Gahagan,  S and Gao,  W and Garavan,  H and Georgieff,  M and Graham,  A and Grant,  E and Gregory,  K and Gurka,  K and Gurka,  M and Hays Grudo,  J and Hosig,  K and Howell,  B and Huang,  H and Johnson,  S and Jones Harden,  B and Kable,  J and Kaufman,  J and Levitt,  P and Lin,  W and McKelvey,  L and Merhar,  S and Morris,  A and Nagel,  B and Newman,  S and Newsom,  C and Norton,  E and Osmundson,  S and Ou,  X and Pekar,  J and Peralta-Carcelen,  M and Perez-Edgar,  K and Poehlmann-Tynan,  J and Potter,  A and Riggins,  T and Rogers,  C and Satin,  A and Scott,  L and Shenberger,  J and Shuffrey,  L and Smith,  B and Smith,  L and Stamilio,  D and Sullivan,  E and Thomason,  M and Vannest,  J and Volk,  H and Wakschlag,  L and Wilson,  S and Wisnowski,  J and Yerby,  L and Zgierska,  A and Zilverstand,  A},
      title = {HBCD Study Data Release 1.0},
      publisher = {Lasso Informatics US Inc},
      year = {2025}
    }

Structure:

    HBCD/1.0/
    |__ rawdata/ 
    |   |__ phenotype/     # Tabulated Data (demographics, visit info, behavior, etc.)
    |   |   |__ par_visit_data.*
    |   |   |__ sed_basic_demographics.*
    |   |   |__ <instrument_name>.*
    |   |
    |   |__ sub-<label>/   # Raw File-Based Data (MRI, EEG, etc.)
    |   |   |__ sub-<label>_sessions.tsv
    |   |   |__ sub-<label>_sessions.json
    |   |   |__ ses-<label>/
    |   |       |__ anat/
    |   |       |__ dwi/
    |   |       |__ eeg/
    |   |       |__ fmap/
    |   |       |__ func/
    |   |       |__ motion/
    |   |       |__ mrs/
    |   |       |__ sub-<label>_ses-<label>_scans.tsv
    |   |       |__ sub-<label>_ses-<label>_scans.json
    |   |
    |   |__ dataset_description.json
    |   |__ participants.tsv
    |   |__ participants.json 
    |
    |__ derivatives/        # Processed File-Based Data (MRI, EEG, etc.)
        |__ bibsnet/
        |__ hbcd_motion/
        |__ made/
        |__ mriqc/
        |__ nibabies/
        |__ osprey/
        |__ qmri_postproc/
        |__ qsiprep/
        |__ qsirecon/
        |__ symri/
        |__ xcp_d/

    Total Subjects: 602

    | session   |   anat |   dwi |   eeg |   fmap |   func |   motion |   mrs |
    |:----------|-------:|------:|------:|-------:|-------:|---------:|------:|
    | ses-V02   |    546 |   483 |     0 |    508 |    513 |      497 |   302 |
    | ses-V03   |     75 |    63 |    81 |     71 |     71 |       82 |    38 |

## [ABCD](https://abcdstudy.org)

- [ABCD Wiki](https://docs.abcdstudy.org/latest/)
- [Data
  Structure](https://docs.abcdstudy.org/latest/documentation/curation/structure.html)
- [Data Dictionary
  (DEAP)](https://abcd.deapscience.com/#/my-datasets/create-dataset)

### 6.0

Citation

    @misc{https://doi.org/10.82525/jy7n-g441,
      doi = {10.82525/JY7N-G441},
      url = {https://nbdc-datahub.org/abcd-release-6-0},
      author = {Jernigan,  Terry L. and Brown,  Sandra A. and Dale,  Anders M. and Tapert,  Susan F. and Sowell,  Elizabeth R. and Herting,  Megan and Laird,  Angela and Gonzalez,  Raul and Squeglia,  Lindsay and Gray,  Kevin and Paulus,  Martin P. and Aupperle,  Robin and Feldstein Ewing,  Sarah W. and Nagel,  Bonnie J. and Fair,  Damien A. and Baker,  Fiona and M\"{u}ller Oehring,  Eva and Bookheimer,  Susan Y. and Dapretto,  Mirella and Jacobus,  Joanna and Wilson,  Sylia and Banich,  Marie T. and Cottler,  Linda B. and Nixon,  Sara Jo and Ernst,  Thomas M. and Chang,  Linda and Heitzeg,  Mary M. and Sripada,  Chandra and Luciana,  Monica M. and Friedman,  Naomi and Clark,  Duncan B. and Luna,  Beatriz and Foxe,  John and Freedman,  Edward and Yurgelun-Todd,  Deborah A. and Renshaw,  Perry F. and Potter,  Alexandra and Garavan,  Hugh P. and Lisdahl,  Krista and Larson,  Christine and Bjork,  James M. and Neale,  Michael C. and Heath,  Andrew C. and Barch,  Deanna M. and Madden,  Pamela A. and Casey,  Betty J. and Baskin-Sommers,  Arielle and Gee,  Dylan},
      title = {ABCD Study(R) Data Release 6.0},
      publisher = {Lasso Informatics US Inc},
      year = {2025}
    }

Note: We only maintain a subset of available ABCD data due to storage
constraints. Please get in touch if there is information you’re missing.

    ABCD/6.0/
        dairc
        └── rawdata
            ├── phenotype
            │   ├── <table_name>.json
            │   ├── <table_name>.parquet
            │   ├── <table_name>.tsv
            │   └── ...
            ├── sub-<participant>
            │   ├── ses-<event>
            │   └── ...
            ├── ...
            ├── dataset_description.json
            ├── participants.json
            ├── participants.tsv
            ├── scans.json
            ├── sessions.json
            ├── task-<experiment>_beh.json
            └── ...
        └── concat
            └── substance_use
                └── tlfb

    Total Subjects: 11868

    | session   |   beh |
    |:----------|------:|
    | ses-00A   | 11852 |
    | ses-01A   |  9009 |
    | ses-02A   | 10855 |
    | ses-03A   |  8482 |
    | ses-04A   |  9644 |
    | ses-05A   |  8615 |
    | ses-06A   |  5014 |
