"""
Reorder Milestone Notes Columns in field_mapping.csv

This script reorders the milestone notes columns so they appear immediately after
their corresponding days_to_target columns, similar to how KPI notes were grouped
with their KPIs.

Current Order:
    idea_project_defined_target
    idea_project_defined_completed
    idea_project_defined_days_to_target
    [... other milestones ...]
    [... scoring section ...]
    idea_project_defined_notes  <-- All notes at end

Target Order:
    idea_project_defined_target
    idea_project_defined_completed
    idea_project_defined_days_to_target
    idea_project_defined_notes  <-- Notes grouped with milestone
    [... other milestones with notes ...]
    [... scoring section ...]
"""

import csv
from pathlib import Path
from datetime import datetime

# Configuration
PROJECT_ROOT = Path(__file__).parent
FIELD_MAPPING_PATH = PROJECT_ROOT / "config" / "field_mapping.csv"
BACKUP_PATH = PROJECT_ROOT / "config" / f"field_mapping_BACKUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# The 12 milestone base names (without suffixes)
MILESTONE_NAMES = [
    "idea_project_defined",
    "idea_business_case_approved",
    "idea_resources_allocated",
    "develop_technical_poc_validated",
    "develop_dev_roadmap_documented",
    "develop_coding_started",
    "pilot_deployment_to_beta",
    "pilot_initial_metrics_feedback",
    "pilot_feedback_affecting_code",
    "live_general_release_available",
    "live_success_metrics_tracking",
    "live_feedback_loop_continuing",
]

def backup_field_mapping():
    """Create a backup of the current field_mapping.csv"""
    import shutil
    shutil.copy(FIELD_MAPPING_PATH, BACKUP_PATH)
    print(f"[OK] Backup created: {BACKUP_PATH.name}")

def load_field_mapping():
    """Load field_mapping.csv into memory"""
    with open(FIELD_MAPPING_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows

def separate_milestone_notes(rows):
    """
    Separate milestone notes from other rows

    Returns:
        tuple: (notes_dict, other_rows)
        - notes_dict: {milestone_name: notes_row}
        - other_rows: all non-notes rows
    """
    notes_dict = {}
    other_rows = []

    for row in rows:
        col_name = row['output_column_name']

        # Check if this is a milestone notes field
        if col_name.endswith('_notes') and any(col_name.startswith(m) for m in MILESTONE_NAMES):
            # Extract base milestone name (remove '_notes' suffix)
            milestone_name = col_name.replace('_notes', '')
            notes_dict[milestone_name] = row
        else:
            other_rows.append(row)

    return notes_dict, other_rows

def reorder_with_grouped_notes(other_rows, notes_dict):
    """
    Rebuild rows with notes grouped after their corresponding days_to_target fields

    Args:
        other_rows: All non-notes rows
        notes_dict: Dictionary of {milestone_name: notes_row}

    Returns:
        list: Reordered rows with notes grouped
    """
    reordered_rows = []

    for row in other_rows:
        col_name = row['output_column_name']
        reordered_rows.append(row)

        # Check if this is a days_to_target field
        if col_name.endswith('_days_to_target'):
            # Extract base milestone name
            milestone_name = col_name.replace('_days_to_target', '')

            # Insert corresponding notes right after
            if milestone_name in notes_dict:
                reordered_rows.append(notes_dict[milestone_name])
                print(f"  [+] Inserted {milestone_name}_notes after {col_name}")

    return reordered_rows

def save_field_mapping(rows):
    """Save reordered rows back to field_mapping.csv"""
    fieldnames = ['output_column_name', 'input_row_number', 'input_column_letter', 'data_type', 'is_required', 'section']

    with open(FIELD_MAPPING_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] Updated field_mapping.csv with {len(rows)} fields")

def verify_reordering():
    """Verify that milestone notes are now grouped correctly"""
    rows = load_field_mapping()

    print("\n=== Verification: Milestone Field Grouping ===")

    for milestone_name in MILESTONE_NAMES:
        target_field = f"{milestone_name}_target"
        completed_field = f"{milestone_name}_completed"
        days_field = f"{milestone_name}_days_to_target"
        notes_field = f"{milestone_name}_notes"

        # Find positions
        positions = {}
        for i, row in enumerate(rows):
            col_name = row['output_column_name']
            if col_name in [target_field, completed_field, days_field, notes_field]:
                positions[col_name] = i

        # Check if they're consecutive
        if len(positions) == 4:
            indices = [positions[target_field], positions[completed_field], positions[days_field], positions[notes_field]]
            if indices == sorted(indices) and max(indices) - min(indices) == 3:
                print(f"  [+] {milestone_name}: target -> completed -> days_to_target -> notes (positions {min(indices)}-{max(indices)})")
            else:
                print(f"  [!] {milestone_name}: Fields not consecutive! Positions: {indices}")
        else:
            print(f"  [!] {milestone_name}: Missing fields! Found: {list(positions.keys())}")

def main():
    """Main execution"""
    print("=" * 80)
    print("Reordering Milestone Notes in field_mapping.csv")
    print("=" * 80)
    print()

    # Step 1: Backup
    print("Step 1: Creating backup...")
    backup_field_mapping()
    print()

    # Step 2: Load
    print("Step 2: Loading field_mapping.csv...")
    rows = load_field_mapping()
    print(f"  Loaded {len(rows)} fields")
    print()

    # Step 3: Separate notes
    print("Step 3: Separating milestone notes from other fields...")
    notes_dict, other_rows = separate_milestone_notes(rows)
    print(f"  Found {len(notes_dict)} milestone notes fields")
    print(f"  Found {len(other_rows)} other fields")
    print()

    # Step 4: Reorder
    print("Step 4: Reordering with grouped notes...")
    reordered_rows = reorder_with_grouped_notes(other_rows, notes_dict)
    print()

    # Step 5: Save
    print("Step 5: Saving reordered field_mapping.csv...")
    save_field_mapping(reordered_rows)
    print()

    # Step 6: Verify
    verify_reordering()
    print()

    print("=" * 80)
    print("[OK] COMPLETE: Milestone notes are now grouped with their milestones!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Update consolidator Excel files (test and live)")
    print("  2. Run test extraction to verify")

if __name__ == "__main__":
    main()
