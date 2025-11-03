"""
Fix Missing Business Columns in Consolidator Files

Restores business_id and business_name columns that were accidentally dropped
during the milestone notes reordering.

Original column order:
1. extraction_id
2. business_id      <- MISSING
3. business_name    <- MISSING
4. sheet_name
5. submission_date
...

This script:
1. Reads backup files (with all 100 columns)
2. Extracts business_id and business_name columns
3. Inserts them back in positions 2 and 3
4. Preserves all milestone notes reordering
5. Results in 100 columns total
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent

# File paths
LIVE_CURRENT = PROJECT_ROOT / "data" / "live" / "AI_QSR_Consolidator.xlsx"
LIVE_BACKUP = PROJECT_ROOT / "data" / "live" / "AI_QSR_Consolidator_BACKUP_20251103_124414.xlsx"
TEST_CURRENT = PROJECT_ROOT / "data" / "test" / "AI_QSR_Consolidator.xlsx"
TEST_BACKUP = PROJECT_ROOT / "data" / "test" / "AI_QSR_Consolidator_BACKUP_20251103_124413.xlsx"

def create_backup(file_path):
    """Create a new backup before making changes"""
    if not file_path.exists():
        print(f"  [!] File does not exist: {file_path}")
        return None

    backup_path = file_path.parent / f"{file_path.stem}_BACKUP_FIX_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_path.suffix}"

    import shutil
    shutil.copy(file_path, backup_path)
    print(f"  [OK] Backup created: {backup_path.name}")
    return backup_path

def fix_consolidator(current_path, backup_path, env_name):
    """
    Restore business_id and business_name columns from backup

    Args:
        current_path: Path to current consolidator (98 columns, reordered milestones)
        backup_path: Path to backup consolidator (100 columns, old order)
        env_name: "TEST" or "LIVE"

    Returns:
        bool: Success status
    """
    print(f"\n{'='*80}")
    print(f"FIXING {env_name} CONSOLIDATOR")
    print(f"{'='*80}")

    # Check files exist
    if not current_path.exists():
        print(f"  [!] Current file not found: {current_path}")
        return False

    if not backup_path.exists():
        print(f"  [!] Backup file not found: {backup_path}")
        return False

    # Create safety backup
    print("  Step 1: Creating safety backup...")
    create_backup(current_path)

    # Read both files
    print("  Step 2: Reading files...")
    df_current = pd.read_excel(current_path)
    df_backup = pd.read_excel(backup_path)

    print(f"    Current: {df_current.shape[0]} rows x {df_current.shape[1]} columns")
    print(f"    Backup:  {df_backup.shape[0]} rows x {df_backup.shape[1]} columns")

    # Check if business columns exist in current file
    print("  Step 3: Checking for business_id and business_name...")

    has_business_id = 'business_id' in df_current.columns
    has_business_name = 'business_name' in df_current.columns

    print(f"    business_id in current: {has_business_id}")
    print(f"    business_name in current: {has_business_name}")

    if has_business_id and has_business_name:
        # Columns exist but may be in wrong position - reorder them
        print("  Step 4: Reordering existing business columns to positions 2-3...")

        # Get all columns
        all_columns = df_current.columns.tolist()

        # Remove business columns from current positions
        all_columns.remove('business_id')
        all_columns.remove('business_name')

        # Insert at positions 1 and 2 (after extraction_id at position 0)
        all_columns.insert(1, 'business_id')
        all_columns.insert(2, 'business_name')

        # Reorder dataframe
        df_current = df_current[all_columns]

        print(f"    [OK] Columns reordered")
        print(f"    Shape: {df_current.shape[0]} rows x {df_current.shape[1]} columns")

    else:
        # Columns missing - restore from backup
        print("  Step 4: Restoring business columns from backup...")

        if 'business_id' not in df_backup.columns:
            print(f"    [!] business_id not found in backup!")
            return False

        if 'business_name' not in df_backup.columns:
            print(f"    [!] business_name not found in backup!")
            return False

        business_id_col = df_backup['business_id']
        business_name_col = df_backup['business_name']
        print(f"    [OK] Extracted from backup ({len(business_id_col)} rows)")

        # Insert at positions 1 and 2
        df_current.insert(1, 'business_id', business_id_col)
        df_current.insert(2, 'business_name', business_name_col)

        print(f"    [OK] Columns inserted")
        print(f"    New shape: {df_current.shape[0]} rows x {df_current.shape[1]} columns")

    # Verify column order
    print("  Step 5: Verifying column order...")
    new_columns = df_current.columns.tolist()

    if new_columns[0] != 'extraction_id':
        print(f"    [!] Column 1 should be extraction_id, but is {new_columns[0]}")
        return False

    if new_columns[1] != 'business_id':
        print(f"    [!] Column 2 should be business_id, but is {new_columns[1]}")
        return False

    if new_columns[2] != 'business_name':
        print(f"    [!] Column 3 should be business_name, but is {new_columns[2]}")
        return False

    print(f"    [OK] First 5 columns:")
    for i, col in enumerate(new_columns[:5]):
        print(f"      {i+1}. {col}")

    # Verify milestone notes are still grouped
    print("  Step 6: Verifying milestone notes still grouped...")
    sample_milestones = [
        ('idea_project_defined_days_to_target', 'idea_project_defined_notes'),
        ('develop_coding_started_days_to_target', 'develop_coding_started_notes'),
        ('live_general_release_available_days_to_target', 'live_general_release_available_notes'),
    ]

    all_correct = True
    for days_col, notes_col in sample_milestones:
        if days_col in new_columns and notes_col in new_columns:
            days_idx = new_columns.index(days_col)
            notes_idx = new_columns.index(notes_col)
            if notes_idx == days_idx + 1:
                print(f"    [+] {notes_col} correctly follows {days_col}")
            else:
                print(f"    [!] {notes_col} NOT adjacent to {days_col}")
                all_correct = False

    if not all_correct:
        print("    [!] Milestone notes grouping verification failed!")
        return False

    # Save fixed file
    print("  Step 7: Saving fixed consolidator...")
    try:
        df_current.to_excel(current_path, index=False, engine='openpyxl')
        print(f"    [OK] Saved: {current_path}")
    except Exception as e:
        print(f"    [!] Error saving: {e}")
        return False

    print(f"{'='*80}")
    print(f"[OK] {env_name} CONSOLIDATOR FIXED - {df_current.shape[1]} columns")
    print(f"{'='*80}")

    return True

def main():
    """Main execution"""
    print("="*80)
    print("Restoring Missing Business Columns")
    print("="*80)
    print()
    print("This script restores business_id and business_name columns that were")
    print("accidentally dropped during milestone notes reordering.")
    print()

    results = {}

    # Fix test consolidator
    results['test'] = fix_consolidator(TEST_CURRENT, TEST_BACKUP, "TEST")

    # Fix live consolidator
    results['live'] = fix_consolidator(LIVE_CURRENT, LIVE_BACKUP, "LIVE")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Test consolidator: {'[OK] Fixed' if results['test'] else '[!] Failed'}")
    print(f"Live consolidator: {'[OK] Fixed' if results['live'] else '[!] Failed'}")
    print()

    if all(results.values()):
        print("[OK] All consolidator files now have 100 columns!")
        print()
        print("Column order:")
        print("  1. extraction_id")
        print("  2. business_id")
        print("  3. business_name")
        print("  4. sheet_name")
        print("  5. submission_date")
        print("  ...")
        print("  + 91 project fields (with milestone notes grouped)")
        print()
        print("Next steps:")
        print("  1. Test extraction to verify all columns work")
        print("  2. Commit changes to git")
    else:
        print("[!] Some files failed to fix")
        print("Please review errors above")

if __name__ == "__main__":
    main()
