# AI QSR Consolidation Workflow - Project Overview

**Created:** 2025-10-22
**Status:** Planning/Research Phase
**Priority:** High
**Owner:** Chase (AI Transformation Analyst, CSI/Pyxis)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Project Context](#project-context)
3. [Document Structures](#document-structures)
4. [Workflow Architecture](#workflow-architecture)
5. [Technical Decisions](#technical-decisions)
6. [Data Mapping](#data-mapping)
7. [Critical Considerations](#critical-considerations)
8. [Implementation Plan](#implementation-plan)
9. [Next Steps](#next-steps)

---

## Executive Summary

**Goal:** Automate the consolidation of weekly AI project submissions from 10+ Business Units into a single Google Sheets database for executive reporting and trend analysis.

**Problem:** Business Units across CSI/Pyxis submit weekly Quarterly Strategic Review (QSR) reports via Excel files. Currently requires manual aggregation of data from multiple project tabs across multiple BU submissions (10 BUs × variable projects/BU × 52 weeks = 2,600+ rows/year).

**Solution:** Build an n8n workflow that:
- Monitors OneDrive folder for new BU submissions
- Dynamically discovers all project sheets (P1, P2, ..., Pn) in each submission
- Transforms vertical form data into horizontal 79-column flat table format
- Appends consolidated data to Google Sheets master database
- Maintains full historical tracking with timestamps

**Value:** Eliminates ~3-4 hours/week of manual data consolidation, enables real-time executive dashboards, provides trend analysis across BUs.

---

## Project Context

### Organizational Background

**CSI (Constellation Software Inc.)** is a holding company with 100+ acquired software businesses organized into portfolios. The **Pyxis Portfolio** is implementing an **AI Transformation Initiative** led by Arthur (CEO) and Jamie (GM).

**Measurement Framework:**
- **Value Tiers:** Projects scored 1-5 (Tier 1 = Simple Tools [10 pts] → Tier 5 = Net-New AI Products [200 pts])
- **Stage Multipliers:** Idea (0.1x) → Develop (0.4x) → Pilot (0.7x) → Live (1.0x)
- **Tracking:** Weekly submissions to measure progress across BUs

### Current Process (Manual)

1. BUs download template (`AI QSR Inputs vBeta.xlsx`)
2. Fill out project sheets (P1, P2, P3, etc.) for each active AI project
3. Upload to OneDrive `/AI QSR Submissions/2025-Q4/` folder
4. Chase manually opens each file, copies data to consolidator spreadsheet
5. Consolidator feeds into executive dashboards and QSR presentations

**Pain Points:**
- Time-consuming (3-4 hrs/week)
- Error-prone (copy-paste mistakes)
- Difficult to track trends over time
- No real-time visibility

---

## Document Structures

### Input: AI QSR Inputs vBeta.xlsx (BU Submission Template)

**Location:** `C:\Users\chase\OneDrive\Desktop\Work\BU Orbit\Execution\Builds\N8N Workflows\AI_QSR_Consolidation\AI QSR Inputs vBeta .xlsx`

**Structure:**
- **16 sheets:** Scorecard, Sample, P1-P10, Project Data, Lookups, KPI Library, Maturity Ratings
- **Key workflow concern:** P1-P10 sheets (project data), but **count is NOT fixed at 10**
- **Critical:** Number of project sheets will grow dynamically (P1, P2, ..., P15+) as BUs add projects

**Project Sheet Layout (P1-P10):**
- **Vertical form layout** (label-value pairs)
- **Labels in Column B** (index 1)
- **Values in Column F** (index 5)
- **Additional data in Columns G-H** (dates, calculations)

**Key Fields (by section):**

**Project Info (Rows 2-8):**
- Row 2: Project Name
- Row 4: Description (Use Case)
- Row 6: Category (L1-L5)
- Row 7: Strategic Value Level
- Row 8: Examples

**Project Resources (Rows 11-20):**
- Row 11: AI Tools & Services
- Row 16: Contact
- Row 17: Prod Mgr
- Row 18: Analyst
- Row 19: Tech Lead
- Row 20: Exec

**KPIs (Rows 22-34):**
- 3 KPIs tracked with:
  - Week Ending date
  - TARGET value
  - Actual value
  - Delta (calculated)

**Maturity Milestones (Rows 37+):**
- 12 milestones across 4 stages (Idea, Develop, Pilot, Live)
- Each milestone has: Target Date, Completed Date, Days to Target

---

### Output: AI QSR Consolidator.xlsx (Master Database)

**Location:** `C:\Users\chase\OneDrive\Desktop\Work\BU Orbit\Execution\Builds\N8N Workflows\AI_QSR_Consolidation\AI QSR Consolidator.xlsx`

**Structure:**
- **Single sheet** with **79 columns** (horizontal flat table)
- **Each row = 1 project × 1 week submission**
- Historical tracking: Same project creates new row each week

**Column Organization:**

**Columns 1-9 (Overview):**
1. Date
2. Business Unit
3. Project
4. Project UUID (format: `{BU}_{ProjectName}_{Date}`)
5. Description (use case)
6. Category
7. Strategic value level
8. Examples
9. Ratio impacted

**Columns 10-15 (Project Resources):**
10. AI tools and services
11. Contact
12. Prod Manager
13. Analysts
14. Tech Lead
15. Exec

**Columns 16-36 (KPIs - 3 KPIs × 7 fields each):**
For each KPI (1, 2, 3):
- KPI Category
- KPI Name
- Support explanation
- Measurement approach
- TARGET value
- Actual value
- Delta (variance)

**Columns 37-75 (Maturity Milestones - 12 milestones × 3 fields each):**
For each milestone:
- Target date
- Completed date
- Days to target

Milestones:
- **Idea:** Project Defined, Business Case Approved, Resources Allocated
- **Develop:** POC Validated, Roadmap Documented, Coding Started
- **Pilot:** Deployment to Beta, Initial Metrics/Feedback, Feedback Affecting Code
- **Live:** General Release Available, Success Metrics Tracking, Feedback Loop Continuing

**Columns 76-79 (Scorer - CALCULATED IN SPREADSHEET):**
76. Strategic value (points)
77. Stage multiplier (today)
78. Stage last quarter
79. Project Score (formula-based)

---

## Workflow Architecture

### High-Level Flow (~19 nodes)

```
[OneDrive Trigger] → [Extract Metadata] → [Download Excel File]
    ↓
[Discover All Project Sheets Dynamically]
    ↓
[Loop Through Each Sheet] → [Read Project Data] (×N sheets)
    ↓
[Merge All Projects] → [Filter Empty Projects]
    ↓
[Map to 79-Column Format] → [Generate UUID]
    ↓
[Append to Google Sheets Consolidator]
    ↓
[Send Success Notification]
```

### Phase Breakdown

**Phase 1: Trigger & Download (3 nodes)**
1. **OneDrive Trigger:** Watch `/AI QSR Submissions/2025-Q4/` folder for new `.xlsx` files
2. **Extract Metadata (Set node):** Parse BU name, submission date, quarter from filename
3. **Download File (OneDrive node):** Retrieve binary Excel file

**Phase 2: Extract Project Data (variable nodes)**
4. **Discover Sheets (Code node):** Dynamically list all sheets starting with "P" + digit(s)
5. **Split/Loop:** Iterate through discovered project sheets
6-N. **Read Each Project Sheet (Microsoft Excel node):** Extract form data from each P* sheet

**Phase 3: Transform (4 nodes)**
- **Merge All Projects:** Combine results from all sheets
- **Filter Empty Projects:** Remove rows where Project Name is empty/null
- **Map to Consolidator Format (Set node):** Transform vertical form → horizontal 79-column row
- **Calculate UUID:** Generate `{BU}_{ProjectName}_{Date}` composite key

**Phase 4: Append (2 nodes)**
- **Append to Google Sheets:** Add rows to consolidator (Google Sheets node)
- **Success Notification:** Email confirmation to Chase + Jamie

---

## Technical Decisions

### Key Agreements from October 19 Conversation

**1. Storage Location**
- **Decision:** Google Sheets for consolidator database
- **Rationale:** Better performance with large datasets, easier dashboards (Looker Studio), superior API rate limits
- **Note:** Can export to Excel weekly for Arthur's analysis if needed

**2. Score Calculations (Columns 76-79)**
- **Decision:** Calculations live in spreadsheet formulas (NOT calculated in n8n)
- **Rationale:** Traceability, easier to tweak scoring logic without workflow changes
- **Implementation:** n8n appends raw data (columns 1-75), formulas in columns 76-79 auto-calculate

**3. Unique ID (Project UUID)**
- **Decision:** Composite key format `{BU}_{ProjectName}_{Date}`
- **Example:** `ClubOS_Password_Reset_Agent_2025-10-19`
- **Rationale:** Human-readable, detects duplicate submissions, easier traceability
- **Note:** Separate Date column (Column 1) exists for filtering/analysis

**4. Historical Tracking**
- **Decision:** Append new rows each week (do NOT update existing rows)
- **Example:**
  - Week 42: ClubOS Project A (Stage: Dev) → Row 1
  - Week 43: ClubOS Project A (Stage: Pilot) → Row 2
- **Rationale:** Full historical tracking, easier than updates, enables trend analysis
- **Query Pattern:** Use pivot tables or filters to show "latest snapshot only" when needed

**5. Dynamic Project Sheets**
- **Decision:** MUST dynamically discover all project sheets (not hardcoded to P1-P10)
- **Rationale:** BUs will add more projects over time (P11, P12, P15+)
- **Implementation:** Use sheet discovery logic to find all sheets matching pattern `P\d+`

---

## Data Mapping

### Transformation Challenge

**Input:** Vertical form (label-value pairs in Columns B & F)
**Output:** Horizontal row with 79 columns

### Critical Mapping Logic

```
# Pseudo-mapping
consolidator_row = {
    "Date": today_or_filename_date,
    "Business Unit": parsed_from_filename,
    "Project": row_2_column_F,
    "Project UUID": f"{bu_name}_{project_name}_{date}",
    "Description (use case)": row_4_column_F,
    "Category": row_6_column_F,
    "Strategic value level": row_7_column_F,
    "Examples": row_8_column_F,
    "Ratio impacted": row_9_column_F,  # TBD exact row
    "AI tools and services": row_11_column_F,
    "Contact": row_16_column_F,
    "Prod Manager": row_17_column_F,
    "Analysts": row_18_column_F,
    "Tech Lead": row_19_column_F,
    "Exec": row_20_column_F,
    # KPIs: Extract from rows 22-34 (3 KPIs × 7 fields)
    # Milestones: Extract from rows 37+ (12 milestones × 3 fields)
    # Scorer columns (76-79): Leave empty, formulas will calculate
}
```

**Note:** Exact row mappings need validation during implementation by reading actual template.

---

## Critical Considerations

### 1. Dynamic Sheet Discovery
- **Challenge:** Cannot hardcode P1-P10 loop
- **Solution:** Use Code node or Excel API to list all sheets, filter by regex `^P\d+$`
- **Alternative:** Use n8n Split In Batches with dynamic input

### 2. Empty Project Handling
- **Scenario:** BU submits file with P1-P3 filled, P4-P10 empty
- **Solution:** Filter node checks for non-null Project Name (row 2, column F)
- **Result:** Only P1-P3 appended to consolidator

### 3. Concurrent Write Conflicts
- **Risk:** Multiple BU submissions uploaded simultaneously to OneDrive
- **Mitigation:** OneDrive Trigger processes sequentially, Google Sheets API handles concurrent appends
- **Note:** This is why Google Sheets > Excel Online

### 4. Error Handling
- **Scenarios:**
  - Malformed filename (cannot parse BU name)
  - Corrupted Excel file
  - Missing required fields
  - Sheet structure changes
- **Solution:** Wrap critical nodes in error workflows, send failure notifications with details

### 5. Token Management (n8n MCP)
- **Challenge:** Large workflow JSON can consume significant tokens
- **Strategy:** Use `n8n_update_partial_workflow()` for incremental changes
- **Best Practice:** Build initial workflow, then use diff operations for updates

### 6. File Format Compatibility
- **Input:** `.xlsx` (binary Excel format)
- **n8n Node:** Microsoft Excel node (or convert to CSV if needed)
- **Watch Out:** Excel node may require OAuth/Service Principal for SharePoint/OneDrive

---

## Implementation Plan

### Pre-Implementation Research (CURRENT PHASE)

**Research Topics for Sub-Agents:**
1. Microsoft Excel node vs Google Sheets node best practices
2. Dynamic sheet discovery patterns in n8n
3. Known gotchas with Excel/OneDrive triggers
4. Token management strategies for n8n MCP
5. Data extraction from vertical Excel forms
6. Error handling patterns for file processing workflows
7. Recent reported issues from n8n MCP community

### Implementation Sequence

**Phase 1: Foundation (Nodes 1-3)**
- OneDrive Trigger setup
- Metadata extraction logic
- File download validation

**Phase 2: Data Extraction (Nodes 4-N)**
- Dynamic sheet discovery
- Loop configuration
- Excel read operations
- Data validation

**Phase 3: Transformation (Nodes 4)**
- Merge logic
- Filtering rules
- 79-column mapping
- UUID generation

**Phase 4: Output & Monitoring (Nodes 2)**
- Google Sheets append
- Notification setup

**Phase 5: Testing**
- Test with sample files
- Validate all 79 columns map correctly
- Test with varying numbers of project sheets (3, 5, 10, 15)
- Error scenario testing

**Phase 6: Deployment**
- Create workflow in n8n via MCP
- Validate with `n8n_validate_workflow()`
- Activate trigger
- Monitor first real submissions

---

## Next Steps

### Immediate (Today)
1. ✅ **Complete:** Project overview documentation (this file)
2. **Pending:** Launch research sub-agents for implementation gotchas
3. **Pending:** Review research findings and update implementation plan

### Short-Term (This Week)
4. Build workflow in n8n using MCP tools
5. Test with sample files
6. Deploy to production
7. Monitor first week of submissions

### Long-Term (Next Month)
8. Build executive dashboard in Looker Studio (connected to Google Sheets)
9. Implement data quality monitoring (alerts for missing fields)
10. Add weekly summary email (aggregated stats across all BUs)

---

## Reference Files

**Project Directory:** `C:\Users\chase\OneDrive\Desktop\Work\BU Orbit\Execution\Builds\N8N Workflows\AI_QSR_Consolidation`

**Key Files:**
- `AI QSR Inputs vBeta .xlsx` - BU submission template (input)
- `AI QSR Consolidator.xlsx` - 79-column master database (output)
- `oct_19_convo_n8n.md` - Full conversation log with original agent (4,845 lines)
- `project_overview.md` - This file

**n8n MCP Documentation:**
- `C:\Users\chase\OneDrive\Desktop\Work\n8n_mcp_overview.md`

**Related Context:**
- `C:\Users\chase\OneDrive\Desktop\Work\BU Orbit\Execution\Role_Context_and_Responsibilities.md` - Full role context
- `C:\Users\chase\OneDrive\Desktop\Work\BU Orbit\Strategy\Jonas HQ\AI QSR Inputs vBeta.xlsx` - Original template (may be older version)

---

## Contact & Stakeholders

**Project Owner:** Chase (AI Transformation Analyst)
**Stakeholders:**
- Arthur (Pyxis CEO) - Executive reporting consumer
- Jamie (GM) - Workflow sponsor
- 10+ BU Leads - Data submitters

**Communication:**
- Success notifications: Chase + Jamie
- Failure alerts: Chase (immediate)
- Weekly summary: Arthur + Jamie

---

**Last Updated:** 2025-10-22
**Version:** 1.0
**Status:** Ready for Implementation Research Phase
