"""
Categorize measurement approaches into standardized, MECE categories
"""

import pandas as pd
import re

def categorize_measurement(approach, kpi_category):
    """
    Categorize measurement approach into standardized categories.
    Returns: category name (2-5 words)
    """

    if pd.isna(approach) or str(approach).strip() == "":
        return "Not Defined"

    approach_lower = str(approach).lower()

    # 1. License/Access Rate - % of FTE with license/access
    if any(keyword in approach_lower for keyword in [
        "% of", "percentage of", "confirm all", "have access",
        "licences issues", "with access", "eligible", "% near shore",
        "% of onshore", "% of viable"
    ]) and any(keyword in approach_lower for keyword in [
        "headcount", "fte", "employees", "team", "developers", "users"
    ]) and not "actively using" in approach_lower and not "adoption" in approach_lower:
        return "License/Access Rate"

    # 2. Active Usage Rate - % actively using (frequency)
    if any(keyword in approach_lower for keyword in [
        "actively using", "weekly active", "active use", "weekly sprints",
        "adaptation across", "% of developers using"
    ]) and "%" in approach_lower:
        return "Active Usage Rate"

    # 3. Time Saved - hours/minutes saved per task
    if any(keyword in approach_lower for keyword in [
        "hours saved", "time saved", "reduction in time", "cut that time",
        "time to complete", "time required", "hours per week",
        "reduction in average time", "hours reduced", "minutes"
    ]) and not "cycle time" in approach_lower and not "response time" in approach_lower:
        return "Time Saved"

    # 4. Response Time - time to resolve/respond
    if any(keyword in approach_lower for keyword in [
        "response time", "resolution time", "call handling time",
        "average time to resolve", "time to respond", "turnaround time",
        "handling time"
    ]):
        return "Response Time"

    # 5. Cycle Time Reduction - reduction in cycle time/process duration
    if any(keyword in approach_lower for keyword in [
        "cycle time", "reduction in cycle", "process duration"
    ]):
        return "Cycle Time Reduction"

    # 6. Volume Completed - count of tasks/tickets/items
    if any(keyword in approach_lower for keyword in [
        "number of", "count of", "tasks completed", "story points",
        "weekly tasks", "# of", "total number", "prompts sent",
        "ticket count", "demos produced", "kanban", "throughput",
        "completed per", "increase in completed", "articles by"
    ]) and not any(keyword in approach_lower for keyword in [
        "customers", "clients", "users using", "adoption", "revenue",
        "calls routed", "escalation", "transferred"
    ]):
        return "Volume Completed"

    # 7. Revenue Impact - ARR/revenue in dollars
    if any(keyword in approach_lower for keyword in [
        "revenue", "arr", "arpu", "upsold", "sales", "paying customers",
        "upgrade", "additional revenue", "$", "usd"
    ]) and not "cost" in approach_lower:
        return "Revenue Impact"

    # 8. Cost Savings - cost reduction in dollars
    if any(keyword in approach_lower for keyword in [
        "cost savings", "cost of", "cost less", "saving $", "annual savings",
        "opex saving", "labor cost saved", "operational efficiencies"
    ]):
        return "Cost Savings"

    # 9. Customer Adoption Count - number of customers using
    if any(keyword in approach_lower for keyword in [
        "number of customers", "total # of clients", "# of clients",
        "customers using", "clients with", "members using",
        "total customers"
    ]) and "%" not in approach_lower:
        return "Customer Adoption Count"

    # 10. Customer Adoption Rate - % of customers using
    if any(keyword in approach_lower for keyword in [
        "% of customers", "% of clients", "% of eligible customers",
        "% of users who adopt", "adoption by", "activation rate",
        "feature activation", "% adoption"
    ]):
        return "Customer Adoption Rate"

    # 11. Conversion Rate - % conversion between stages
    if any(keyword in approach_lower for keyword in [
        "conversion rate", "convert", "demos completed to", "leads to",
        "conversion", "uplift"
    ]):
        return "Conversion Rate"

    # 12. Satisfaction Score - survey-based satisfaction
    if any(keyword in approach_lower for keyword in [
        "satisfaction survey", "staff satisfaction", "feedback",
        "csat", "rating", "perception"
    ]):
        return "Satisfaction Score"

    # 13. Automation Rate - % of workflow/process automated
    if any(keyword in approach_lower for keyword in [
        "% automation", "% of workflow", "% automated",
        "automation in", "code delivered weekly", "reviewed weekly"
    ]):
        return "Automation Rate"

    # 14. Performance Benchmark - vs standard/baseline
    if any(keyword in approach_lower for keyword in [
        "vs benchmark", "vs baseline", "faster than", "performance in ms",
        "industry average", "industry standard", "compared to",
        "baseline taken", "velocity increases"
    ]):
        return "Performance Benchmark"

    # 15. Escalation Rate - % escalated/transferred
    if any(keyword in approach_lower for keyword in [
        "transferred to", "routed to support", "escalation",
        "calls routed", "% routed"
    ]):
        return "Escalation Rate"

    # 16. Self-Service Rate - % self-resolved without human
    if any(keyword in approach_lower for keyword in [
        "self-solved", "without escalation", "handled by automation",
        "handled via automation"
    ]):
        return "Self-Service Rate"

    # 17. Accuracy Rate - % correct/error rate
    if any(keyword in approach_lower for keyword in [
        "% of correct", "error", "accuracy", "reduce errors",
        "correct answers"
    ]):
        return "Accuracy Rate"

    # 18. Feature Count - number of features/automations deployed
    if any(keyword in approach_lower for keyword in [
        "# of automated", "# of automations", "# of workflows",
        "total # of active", "automations in place"
    ]):
        return "Feature Count"

    # 19. Proactive Touchpoints - count of outreach activities
    if any(keyword in approach_lower for keyword in [
        "proactive touchpoints", "emails, calls, and meetings",
        "weekly outreach", "unique accounts"
    ]):
        return "Proactive Touchpoints"

    # 20. Deployment Speed - time to deploy new features
    if any(keyword in approach_lower for keyword in [
        "time required to expand", "time to deliver",
        "days to deliver"
    ]):
        return "Deployment Speed"

    # 21. Adoption Rate (generic) - when "adoption" is mentioned
    if "adoption" in approach_lower and "rate" in approach_lower:
        return "Adoption Rate"

    # 22. Usage Metrics (generic count) - generic usage tracking
    if "track" in approach_lower and any(keyword in approach_lower for keyword in [
        "questions handled", "inquiries handled", "avg. #", "calls /",
        "per customer per month"
    ]):
        return "Usage Metrics"

    # 23. Under review / TBD
    if any(keyword in approach_lower for keyword in [
        "under review", "tbd", "to be conducted", "goal tbd",
        "not have a baseline"
    ]):
        return "Not Defined"

    # Default: if no clear match, categorize by KPI type context
    if "cost" in kpi_category.lower():
        return "Cost Savings"
    elif "revenue" in kpi_category.lower():
        return "Revenue Impact"
    elif "adoption" in kpi_category.lower():
        return "Adoption Rate"
    elif "productivity" in kpi_category.lower():
        return "Volume Completed"
    elif "satisfaction" in kpi_category.lower():
        return "Satisfaction Score"

    # If still no match, return generic
    return "Volume Completed"


# Load data
print("Loading data...")
df = pd.read_excel('analysis/Nov_2/KPI_measurement_quality.xlsx')

print(f"Total rows: {len(df)}")
print(f"Columns: {df.columns.tolist()}")

# Apply categorization
print("\nCategorizing measurement approaches...")
df['measurement_approach_category'] = df.apply(
    lambda row: categorize_measurement(row['measurement_approach'], row['kpi_category']),
    axis=1
)

# Show distribution of categories
print("\nCategory Distribution:")
category_counts = df['measurement_approach_category'].value_counts()
print(category_counts)

# Save back to Excel FIRST (before any print statements that might fail)
print("\n\nSaving updated file...")
df.to_excel('analysis/Nov_2/KPI_measurement_quality.xlsx', index=False)
print("File saved successfully!")

print(f"\nSUCCESS: File updated with measurement_approach_category column")
print(f"Total categories created: {df['measurement_approach_category'].nunique()}")
print(f"Total rows categorized: {len(df)}")

# Show some examples (optional - might have Unicode issues)
try:
    print("\n\nSample Categorizations (top 5):")
    for category in category_counts.head(5).index:
        print(f"\n{category}: {category_counts[category]} instances")
except Exception as e:
    print(f"(Could not print examples due to encoding: {e})")
