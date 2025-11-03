"""
Create Enhanced KPI Quality Excel with Project Sheet Names and AI Tools/Services
"""

import pandas as pd

# Read consolidator data
print("Reading consolidator...")
consolidator = pd.read_excel('data/live/AI_QSR_Consolidator.xlsx')

# Get unique projects with sheet names and AI tools
project_info = consolidator[['business_name', 'project_name', 'sheet_name', 'ai_tools_services']].drop_duplicates()
print(f"Found {len(project_info)} unique projects")

# Read KPI quality analysis
print("Reading KPI quality analysis...")
kpi_quality = pd.read_csv('analysis/analysis_results/kpi_measurement_quality_analysis.csv')
print(f"Found {len(kpi_quality)} KPI instances")

# Merge to add sheet_name and ai_tools_services
print("Merging data...")
enhanced = pd.merge(
    kpi_quality,
    project_info,
    on=['business_name', 'project_name'],
    how='left'
)

# Reorder columns to put new fields near the front
columns_order = [
    'business_name',
    'project_name',
    'sheet_name',  # NEW
    'ai_tools_services',  # NEW
    'project_category',
    'kpi_category',
    'measurement_approach',
    'measurement_quality_score',
    'measurement_quality_category',
    'measurement_has_metric',
    'measurement_has_timeframe',
    'measurement_word_count',
    'support_description',
    'support_quality_score',
    'support_quality_category',
    'support_has_metric',
    'support_has_timeframe',
    'support_word_count'
]

enhanced = enhanced[columns_order]

# Sort by business, then sheet name
enhanced = enhanced.sort_values(['business_name', 'sheet_name', 'kpi_category'])

# Write to Excel with formatting
print("Writing to Excel...")
output_path = 'analysis/Nov_2/KPI_measurement_quality.xlsx'

with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    enhanced.to_excel(writer, sheet_name='KPI Quality Analysis', index=False)

    # Get the worksheet to apply formatting
    worksheet = writer.sheets['KPI Quality Analysis']

    # Set column widths
    worksheet.column_dimensions['A'].width = 20  # business_name
    worksheet.column_dimensions['B'].width = 50  # project_name
    worksheet.column_dimensions['C'].width = 12  # sheet_name
    worksheet.column_dimensions['D'].width = 40  # ai_tools_services
    worksheet.column_dimensions['E'].width = 25  # project_category
    worksheet.column_dimensions['F'].width = 25  # kpi_category
    worksheet.column_dimensions['G'].width = 60  # measurement_approach
    worksheet.column_dimensions['H'].width = 18  # measurement_quality_score
    worksheet.column_dimensions['I'].width = 22  # measurement_quality_category

    # Freeze header row and first 3 columns
    worksheet.freeze_panes = 'D2'

print(f"✅ Created enhanced KPI quality file: {output_path}")
print(f"   - {len(enhanced)} KPI instances")
print(f"   - {len(enhanced['business_name'].unique())} business units")
print(f"   - {len(enhanced['project_name'].unique())} projects")
print(f"   - Columns added: sheet_name, ai_tools_services")
