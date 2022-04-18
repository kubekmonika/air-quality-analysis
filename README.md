# PM2.5 concentrations in Poland

The aim of this project is an analysis of air quality data in Poland for year 2021.

This repository presents a script which was used to curate the data which was then visualised in Tableau.

## Data

Data was downloaded from the [GIOŚ website](https://powietrze.gios.gov.pl/pjp/archives).

### PM2.5 data

PM2.5, particulate matter consisting of fine aerosol particles measuring 2.5 microns or smaller in diameter, is one of six routinely measured criteria air pollutants and is commonly accepted as the most harmful to human health due to its prevalence in the environment and broad range of health effects.

The PM2.5 dataset contains information about measured PM2.5 concentrations in micrograms per cubic meter (µg/m³). Data comes from 77 measurement stations located across Poland.

### Measuring stations metadata

The other dataset contains metadata about stations: their names, identifiers, locations, coordinates.

## Project - curating data

The script `clean_data.py` does the following operations:
1. Reads the PM2.5 data.
  - Interpolates missing values if the gap is up to 5 hours.
  - Drops stations which have more then 6% data missing.
  - For each of the remaining stations, calculates the mean value and fills the missing values with it.
  - Keeps both information: actual measurement data and curated data with filled values.
  - Transforms the dataset from horizontal to vertical format.
2. Reads the metadata.
3. Joins the PM2.5 data with metadata.
4. Final dataset consinsts of the following columns:
  - 'Czas' - time, granularity 1 hour,
  - 'Kod stacji' - station ID,
  - 'Pomiar' - measured PM2.5 concentrations in micrograms per cubic meter (µg/m³),
  - 'Pomiar (uzupełniony)' - measured PM2.5 concentrations with missing values filled by the mean value.
  - 'Nazwa stacji' - station name
  - 'φ N' - latitude
  - 'λ E' - longitute

### Files structure

```
- analyses  # code from previous iterations, I kept it for the future reference

- data
|- 2021_DANE_1H_24H.xlsx  # both PM2.5 data and metadada, they are in separate sheets

- .gitignore
- clean_data.py  # script that curates data and produces the final dataset
- environment.yaml
- README.md
- requirements.txt
```

### How to run it

To run this project the conda package and environment manager is being used.

Libraries and their versions required for replication of this analysis are listed in the `requirements.txt` file.

Python version: 3.8.12

Run `conda create --name <env> --file requirements.txt` to create a conda environment, and then `conda activate <env>` to activate it.

To produce the final dataset run the following command:
```
python clean_data.py -D <path to spreadsheet with data> -O pm25-data-clean-2021.csv
```

## Inspiration

[2021 World Air Quality Report](https://www.iqair.com/us/world-air-quality-report)
