# Real QSR Extraction

Run the QSR extraction process in **LIVE/PRODUCTION** mode. This will extract data from the provided workbook and save it to the live environment.

⚠️ **WARNING**: This writes to production data! Use carefully.

## Usage
`/real-qsr <file_path> <business_name>`

## What this does:
1. Extracts 91 fields from the provided workbook
2. Validates and cleans the data
3. Appends to `data/live/AI_QSR_Consolidator.xlsx` (PRODUCTION)
4. Archives original file to `data/live/archive/`
5. Logs extraction to `data/live/extraction_log.csv`

## Your task:
Run the following command:

```bash
python main.py --file "{file_path}" --business {business_name} --environment live
```

Then provide a summary of:
- How many projects were extracted
- Any errors encountered
- Where the data was saved
- **Confirm this was a live extraction**

## Example:
`/real-qsr "uploads/ClubOS_Week43.xlsx" ClubOS`
