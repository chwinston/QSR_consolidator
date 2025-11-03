# Test QSR Extraction

Run the QSR extraction process in **TEST** mode. This will extract data from the provided workbook and save it to the test environment.

## Usage
`/test-qsr <file_path> <business_name>`

## What this does:
1. Extracts 91 fields from the provided workbook
2. Validates and cleans the data
3. Appends to `data/test/AI_QSR_Consolidator.xlsx`
4. Archives original file to `data/test/archive/`
5. Logs extraction to `data/test/extraction_log.csv`

## Your task:
Run the following command:

```bash
python main.py --file "{file_path}" --business {business_name} --environment test
```

Then provide a summary of:
- How many projects were extracted
- Any errors encountered
- Where the data was saved

## Example:
`/test-qsr "Project_planning/Assets/ClubOS_test.xlsx" ClubOS`
