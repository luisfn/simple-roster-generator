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
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Dependencies

This script was written in python 3.9 and not yet tested on other versions

## Other tips

Join contents of multiple csv files

```
awk 'FNR==1 && NR!=1{next;}{print}' file1.csv file2.csv > file3.csv
```

Convert Excel file to csv (-S for all tabs) - For OSX
```
brew install gnumeric

ssconvert -S file.xlsx file.csv
```

Remove Lines of a file, containing certain string - For OSX
```
brew install gsed

gsed -i '/M21_08LIN_TED_TA2/d' ./aggregated-assignments.csv
```