# Simple Roster Scripts

Unfortunately, metadata files given by the customer not always make sense. 
This tool aims to simplify the generation of Simple Roster files based on customer metadata.

## Usage

Before running any command, please check/adjust `config/customers.json`

Generate line-items files.

```
/usr/local/bin/python3 ./main.py users:line-items:generate nsa
```

Generate user files.

```
/usr/local/bin/python3 ./main.py users:generate nsa
```

Checks if all users generated/given have existing slugs.

```
/usr/local/bin/python3 ./main.py users:check_line_items nsa
```

Search for real users an aggregate them in a single file.

```
/usr/local/bin/python3 ./main.py users:aggregate_real_users nsa
```

## Dependencies

the only external module been used is `dateutil`. To install it, execute:

```
pip3 install dateutil
```

## Configuration

- `config/customers.json` - Defines options like input/output parameter per customer.
- `config/headers.json` - Defines the header for each type of file, based on Simple Roster Version.
- `config/mapping.json` - Tries to map names used on metadata files from customer to names used on the Simple Roster files.

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