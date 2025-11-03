"""
Setup script to create master consolidator files for test and live environments.
Run this after closing all Excel files.
"""

import pandas as pd
import csv
from pathlib import Path

def create_master_consolidator(output_file: Path):
    """Create empty master consolidator file with proper column order."""

    # Load field mapping to get column order
    field_mapping_file = Path('config/field_mapping.csv')
    with open(field_mapping_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        field_names = [row['output_column_name'] for row in reader]

    # Metadata columns (always come first)
    metadata_columns = [
        'extraction_id',
        'business_id',
        'business_name',
        'sheet_name',
        'submission_date',
        'submission_week',
        'workbook_filename',
        'data_hash'
    ]

    # Full column order: metadata + extracted fields
    all_columns = metadata_columns + field_names

    print(f"Creating master consolidator with {len(all_columns)} columns")
    print(f"  Metadata: {len(metadata_columns)} columns")
    print(f"  Extracted fields: {len(field_names)} columns")

    # Create empty DataFrame with proper column order
    df = pd.DataFrame(columns=all_columns)

    # Save to Excel
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_file, index=False, engine='openpyxl')

    print(f"[OK] Created: {output_file}")

    # Show KPI column positions
    kpi_cols = [i for i, col in enumerate(all_columns, 1)
                if 'kpi' in col and any(x in col for x in ['target', 'actual', 'delta', 'notes'])]
    print(f"  KPI columns at positions: {kpi_cols}")

    return all_columns

if __name__ == '__main__':
    base_dir = Path(__file__).parent

    print("="*60)
    print("Setting up Master Consolidator Files")
    print("="*60)

    # Create test environment file
    print("\n1. Creating TEST environment file...")
    test_file = base_dir / 'data' / 'test' / 'AI_QSR_Consolidator.xlsx'
    test_cols = create_master_consolidator(test_file)

    # Create live environment file
    print("\n2. Creating LIVE environment file...")
    live_file = base_dir / 'data' / 'live' / 'AI_QSR_Consolidator.xlsx'
    live_cols = create_master_consolidator(live_file)

    print("\n" + "="*60)
    print("[OK] Setup Complete!")
    print("="*60)
    print(f"\nTest file: {test_file}")
    print(f"Live file: {live_file}")
    print(f"\nTotal columns: {len(test_cols)}")
    print("\nKPI grouping:")
    for i, col in enumerate(test_cols, 1):
        if 'kpi1' in col and any(x in col for x in ['target', 'actual', 'delta', 'notes']):
            print(f"  Column {i}: {col}")

    print("\nReady to run extractions!")
    print("  Test: /test-qsr <file> <business>")
    print("  Live: /real-qsr <file> <business>")
