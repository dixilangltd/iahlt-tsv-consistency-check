# IAHLT TSV Consistency Check

A simple script to check and validate [IAHLT](https://www.iahlt.org/) (The Israeli Association of Human Language Technologies) TSV file format and find common mistakes and inconsistencies.

## Data

The access to the data is limited to IAHLT organization members. If you have membership, you can download the packages from the [official website](https://releases.iahlt.org/).

## Reports

- [release-2022-12-01/transcription-3/](reports/release-2022-12-01/transcription-3/)
- [release-2023-03-16/transcription-4/](reports/release-2023-03-16/transcription-4/)
- [release-2023-06-06/transcription-5/](reports/release-2023-06-06/transcription-5/)
- [release-2023-09-06/transcription-6/](reports/release-2023-09-06/transcription-6/)

## Usage

Using Python >=3.7, run `tsv_consistency_check.py` with argument `--path` pointing to TSV directory. For example:

```console
python tsv_consistency_check.py --path release-2022-12-01/transcription-3/corpus/
```

You can redirect the logs to report file, i.e:

```console
python tsv_consistency_check.py --path <tsvDirectory> > report.txt
```

## License

This project is licensed under [Apache License 2.0](LICENSE).
