"""
Update Consolidator Excel Files with Reordered Milestone Notes

This script updates both test and live AI_QSR_Consolidator.xlsx files to match
the new field_mapping.csv column order where milestone notes are grouped with
their corresponding milestone fields.

Process:
1. Read current consolidator file
2. Load field_mapping.csv to get new column order
3. Reorder DataFrame columns to match new order
4. Preserve existing data
5. Save back to Excel with correct column order
"""

import pandas as pd
import csv
from pathlib import Path
from datetime import datetime

# Configuration
PROJECT_ROOT = Path(__file__).parent
FIELD_MAPPING_PATH = PROJECT_ROOT / "config" / "field_mapping.csv"
TEST_CONSOLIDATOR_PATH = PROJECT_ROOT / "data" / "test" / "AI_QSR_Consolidator.xlsx"
LIVE_CONSOLIDATOR_PATH = PROJECT_ROOT / "data" / "live" / "AI_QSR_Consolidator.xlsx"

# Metadata columns (not in field_mapping.csv, but in consolidator)
METADATA_COLUMNS = [
    'extraction_id',
    'submission_date',
    'submission_week',
    'business_unit_name',
    'workbook_filename',
    'sheet_name',
    'data_hash',
    'is_duplicate'
]

def load_field_mapping_order():
    """
    Load field_mapping.csv and return ordered list of output column names

    Returns:
        list: Ordered list of output_column_name values
    """
    with open(FIELD_MAPPING_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [row['output_column_name'] for row in reader]

def get_expected_column_order():
    """
    Get the expected column order for consolidator files

    Returns:
        list: Metadata columns + extracted field columns in correct order
    """
    field_columns = load_field_mapping_order()
    return METADATA_COLUMNS + field_columns

def backup_consolidator(file_path):
    """Create timestamped backup of consolidator file"""
    if not file_path.exists():
        print(f"  [!] File does not exist: {file_path}")
        return None

    backup_path = file_path.parent / f"{file_path.stem}_BACKUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_path.suffix}"

    import shutil
    shutil.copy(file_path, backup_path)
    print(f"  [OK] Backup created: {backup_path.name}")
    return backup_path

def reorder_consolidator_columns(file_path):
    """
    Reorder columns in consolidator file to match field_mapping.csv

    Args:
        file_path: Path to consolidator Excel file

    Returns:
        bool: True if successful, False otherwise
    """
    print(f"\nProcessing: {file_path}")
    print("=" * 80)

    # Check if file exists
    if not file_path.exists():
        print(f"  [!] File not found: {file_path}")
        print(f"  [!] Skipping...")
        return False

    # Create backup
    print("  Step 1: Creating backup...")
    backup_path = backup_consolidator(file_path)
    if backup_path is None:
        return False

    # Read current consolidator
    print("  Step 2: Reading current consolidator...")
    try:
        df = pd.read_excel(file_path)
        print(f"    Current shape: {df.shape[0]} rows x {df.shape[1]} columns")
    except Exception as e:
        print(f"  [!] Error reading file: {e}")
        return False

    # Get expected column order
    print("  Step 3: Loading new column order from field_mapping.csv...")
    expected_columns = get_expected_column_order()
    print(f"    Expected columns: {len(expected_columns)}")

    # Check for missing columns
    current_columns = set(df.columns)
    expected_columns_set = set(expected_columns)

    missing_in_df = expected_columns_set - current_columns
    extra_in_df = current_columns - expected_columns_set

    if missing_in_df:
        print(f"    [!] Columns in field_mapping but not in consolidator: {len(missing_in_df)}")
        for col in list(missing_in_df)[:5]:
            print(f"        - {col}")
        if len(missing_in_df) > 5:
            print(f"        ... and {len(missing_in_df) - 5} more")

    if extra_in_df:
        print(f"    [!] Columns in consolidator but not in field_mapping: {len(extra_in_df)}")
        for col in list(extra_in_df)[:5]:
            print(f"        - {col}")
        if len(extra_in_df) > 5:
            print(f"        ... and {len(extra_in_df) - 5} more")

    # Reorder columns (only include columns that exist in both)
    print("  Step 4: Reordering columns...")
    valid_columns = [col for col in expected_columns if col in current_columns]
    df_reordered = df[valid_columns]
    print(f"    Reordered shape: {df_reordered.shape[0]} rows x {df_reordered.shape[1]} columns")

    # Verify milestone notes grouping
    print("  Step 5: Verifying milestone notes grouping...")
    milestone_examples = [
        ('idea_project_defined_days_to_target', 'idea_project_defined_notes'),
        ('develop_coding_started_days_to_target', 'develop_coding_started_notes'),
        ('live_general_release_available_days_to_target', 'live_general_release_available_notes'),
    ]

    all_correct = True
    for days_col, notes_col in milestone_examples:
        if days_col in valid_columns and notes_col in valid_columns:
            days_idx = valid_columns.index(days_col)
            notes_idx = valid_columns.index(notes_col)
            if notes_idx == days_idx + 1:
                print(f"    [+] {notes_col} correctly follows {days_col}")
            else:
                print(f"    [!] {notes_col} NOT adjacent to {days_col} (gap: {notes_idx - days_idx - 1} columns)")
                all_correct = False

    if not all_correct:
        print("    [!] Column ordering verification failed!")
        return False

    # Save reordered consolidator
    print("  Step 6: Saving reordered consolidator...")
    try:
        df_reordered.to_excel(file_path, index=False, engine='openpyxl')
        print(f"    [OK] Saved: {file_path}")
    except Exception as e:
        print(f"    [!] Error saving file: {e}")
        return False

    print("=" * 80)
    print("[OK] COMPLETE")
    return True

def main():
    """Main execution"""
    print("=" * 80)
    print("Updating Consolidator Files with Reordered Milestone Notes")
    print("=" * 80)
    print()
    print("This script will reorder columns in both test and live consolidator files")
    print("to match the updated field_mapping.csv (milestone notes grouped with milestones)")
    print()

    # Track results
    results = {}

    # Process test consolidator
    print("\n" + "=" * 80)
    print("PROCESSING TEST CONSOLIDATOR")
    print("=" * 80)
    results['test'] = reorder_consolidator_columns(TEST_CONSOLIDATOR_PATH)

    # Process live consolidator
    print("\n" + "=" * 80)
    print("PROCESSING LIVE CONSOLIDATOR")
    print("=" * 80)
    results['live'] = reorder_consolidator_columns(LIVE_CONSOLIDATOR_PATH)

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Test consolidator: {'[OK] Success' if results['test'] else '[!] Failed'}")
    print(f"Live consolidator: {'[OK] Success' if results['live'] else '[!] Failed'}")
    print()

    if all(results.values()):
        print("[OK] All consolidator files updated successfully!")
        print()
        print("Next steps:")
        print("  1. Run test extraction: python main.py --file <test_file> --business <BU> --environment test")
        print("  2. Verify milestone notes columns are grouped correctly")
        print("  3. Commit changes to git")
    else:
        print("[!] Some consolidator files failed to update")
        print("Please review errors above and fix before proceeding")

if __name__ == "__main__":
    main()
