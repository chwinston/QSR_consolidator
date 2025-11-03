"""
Add KPI Performance Section to Measurement Approaches Document - FIXED
"""

import pandas as pd

# Load both datasets
quality_df = pd.read_csv('analysis_results/kpi_measurement_quality_analysis.csv')
normalized_df = pd.read_csv('analysis_results/kpi_normalized.csv')

# Merge to get both quality scores and performance data
df = pd.merge(
    quality_df,
    normalized_df[['business_name', 'project_name', 'kpi_category', 'kpi_target', 'kpi_actual', 'kpi_delta']],
    on=['business_name', 'project_name', 'kpi_category'],
    how='left'
)

# Create new section
section = []

section.append("\n\n---\n\n")
section.append("## 3. KPI Performance Summary by Category\n\n")
section.append("This section shows how each business unit measures each KPI category, along with their targets, actuals, and deltas.\n\n")
section.append("**Legend:**\n")
section.append("- **Target**: Goal value for this KPI\n")
section.append("- **Actual**: Current/achieved value\n")
section.append("- **Delta**: Difference (Actual - Target). Positive = exceeding target, Negative = missing target\n\n")
section.append("---\n\n")

# Group by KPI category
for category in sorted(df['kpi_category'].unique()):
    cat_data = df[df['kpi_category'] == category]

    section.append(f"### 3.{list(sorted(df['kpi_category'].unique())).index(category) + 1} {category}\n\n")
    section.append(f"**Total Instances**: {len(cat_data)}\n")
    section.append(f"**Used By**: {', '.join(sorted(cat_data['business_name'].unique()))}\n")

    # Handle targets/actuals/deltas with proper null checking
    if cat_data['kpi_target'].notna().any():
        section.append(f"**Average Target**: {cat_data['kpi_target'].mean():.1f}\n")
    else:
        section.append(f"**Average Target**: N/A\n")

    if cat_data['kpi_actual'].notna().any():
        section.append(f"**Average Actual**: {cat_data['kpi_actual'].mean():.1f}\n")
    else:
        section.append(f"**Average Actual**: N/A\n")

    if cat_data['kpi_delta'].notna().any():
        section.append(f"**Average Delta**: {cat_data['kpi_delta'].mean():.1f}\n\n")
    else:
        section.append(f"**Average Delta**: N/A\n\n")

    section.append("| Business Unit | Project | Measurement Approach | Target | Actual | Delta | Quality |\n")
    section.append("|---------------|---------|---------------------|--------|--------|-------|----------||\n")

    for idx, row in cat_data.iterrows():
        bu = row['business_name']
        project = row['project_name'][:40] + "..." if len(str(row['project_name'])) > 40 else row['project_name']
        measurement = row['measurement_approach'][:50] + "..." if pd.notna(row['measurement_approach']) and len(str(row['measurement_approach'])) > 50 else (row['measurement_approach'] if pd.notna(row['measurement_approach']) else "[NOT PROVIDED]")
        target = f"{row['kpi_target']:.1f}" if pd.notna(row['kpi_target']) else "-"
        actual = f"{row['kpi_actual']:.1f}" if pd.notna(row['kpi_actual']) else "-"
        delta = f"{row['kpi_delta']:.1f}" if pd.notna(row['kpi_delta']) else "-"
        quality = f"{row['measurement_quality_category']}"

        section.append(f"| {bu} | {project} | {measurement} | {target} | {actual} | {delta} | {quality} |\n")

    section.append("\n")

    # Add summary insights for this category
    positive_deltas = cat_data[cat_data['kpi_delta'] > 0]
    negative_deltas = cat_data[cat_data['kpi_delta'] < 0]
    on_target = cat_data[cat_data['kpi_delta'] == 0]

    section.append(f"**Performance Summary:**\n")
    section.append(f"- Exceeding Target: {len(positive_deltas)} of {len(cat_data)} ({len(positive_deltas)/len(cat_data)*100:.1f}%)\n")
    section.append(f"- Missing Target: {len(negative_deltas)} of {len(cat_data)} ({len(negative_deltas)/len(cat_data)*100:.1f}%)\n")
    section.append(f"- On Target: {len(on_target)} of {len(cat_data)}\n\n")

    # Show best performer
    if len(positive_deltas) > 0:
        best = positive_deltas.nlargest(1, 'kpi_delta').iloc[0]
        section.append(f"**Best Performer**: {best['business_name']} - {best['project_name']} (Delta: +{best['kpi_delta']:.1f})\n\n")

    section.append("---\n\n")

# Read the existing document
with open('analysis/Nov_2/KPI_Measurement_Approaches_Analysis.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Find where to insert (after section 2 TOC entry but before "### Adoption Rate" detailed breakdown)
insert_point = content.find("### Adoption Rate")

if insert_point != -1:
    # Insert the new section
    new_content = content[:insert_point] + ''.join(section) + content[insert_point:]

    # Update table of contents - add section 3
    toc_addition = """3. [KPI Performance Summary by Category](#3-kpi-performance-summary-by-category)
   - 3.1 [Adoption Rate Performance](#31-adoption-rate)
   - 3.2 [Competitive Advantage Performance](#32-competitive-advantage)
   - 3.3 [Cost Savings Performance](#33-cost-savings)
   - 3.4 [Customer Adoption Performance](#34-customer-adoption)
   - 3.5 [Employee Satisfaction Performance](#35-employee-satisfaction)
   - 3.6 [Integration Depth Performance](#36-integration-depth)
   - 3.7 [Market Differentiation Performance](#37-market-differentiation)
   - 3.8 [Process Improvement Performance](#38-process-improvement)
   - 3.9 [Productivity Gains Performance](#39-productivity-gains)
   - 3.10 [Revenue Impact Performance](#310-revenue-impact)
   - 3.11 [Skills Development Performance](#311-skills-development)
   - 3.12 [Usage Metrics Performance](#312-usage-metrics)

"""

    # Find where to insert in TOC (after section 2)
    toc_insert = new_content.find("2. [Detailed Breakdown by KPI Category]")
    if toc_insert != -1:
        # Find end of section 2 in TOC (next line that starts with number or ---)
        toc_end = new_content.find("\n---", toc_insert)
        if toc_end != -1:
            new_content = new_content[:toc_end] + "\n" + toc_addition + new_content[toc_end:]

    # Renumber section 2 to section 4
    new_content = new_content.replace("## Detailed Breakdown by KPI Category", "## 4. Detailed Breakdown by KPI Category (Full Detail)")
    new_content = new_content.replace("2. [Detailed Breakdown by KPI Category]", "4. [Detailed Breakdown by KPI Category (Full Detail)]")

    # Write updated content
    with open('analysis/Nov_2/KPI_Measurement_Approaches_Analysis.md', 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("SUCCESS: Added KPI Performance Summary section")
    print(f"- Analyzed {len(df['kpi_category'].unique())} KPI categories")
    print(f"- Included target/actual/delta for all {len(df)} KPI instances")
    print("- Updated table of contents")
    print("- Renumbered detailed breakdown to section 4")
else:
    print("ERROR: Could not find insertion point")
