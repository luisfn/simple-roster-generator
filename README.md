# Simple Roster Scripts

Unfortunately, metadata files given by the customer not always make sense. 
This tool aims to simplify the generation of Simple Roster files based on customer metadata.

## Usage

Before running any command, please check/adjust 

- [config/customers.json](config/customers.json)
- [config/headers.json](config/headers.json)
- [config/mappings.json](config/mappings.json)

To run the tool, just execute:

```
python3 main.py
```

## Dependencies

This script was written in python 3.9 and not yet tested on other versions

To install the needed packages, execute

```
pip3 install dateutil pyinquirer
```

## Other tips

Join contents of multiple csv files

```
awk 'FNR==1 && NR!=1{next;}{print}' file1.csv file2.csv > file3.csv
```

Convert Excel file to csv (-S for all tabs)
```
brew install gnumeric

ssconvert -S file.xlsx file.csv
```