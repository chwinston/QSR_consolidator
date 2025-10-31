# AI QSR Consolidation - Research Findings Summary

**Date:** 2025-10-22
**Status:** Research Phase Complete - Ready for Implementation Review

---

## Executive Summary

Six research agents investigated critical implementation considerations for the AI QSR Consolidation workflow. The findings reveal **significant technical risks** with the Microsoft Excel/OneDrive approach and **strongly recommend** using alternative strategies.

**Key Findings:**
- ⚠️ **HIGH RISK:** Excel node + OneDrive trigger combination has major reliability issues
- ✅ **RECOMMENDED:** Google Sheets approach is significantly more reliable
- ⚠️ **CRITICAL:** Dynamic looping with Excel nodes fails frequently
- ✅ **SOLUTION:** Hybrid approach or community nodes for Excel processing

---

## 1. Microsoft Excel Node & OneDrive Trigger Research

### Critical Limitations Identified

**SharePoint/Business OneDrive Access:**
- Excel node **ONLY works with personal OneDrive**, not SharePoint or organizational drives
- Built-in OAuth app lacks `Sites.ReadWrite.All` scope
- Cannot use custom organizational credentials
- **Impact:** If BUs upload to SharePoint/OneDrive for Business, this is a SHOWSTOPPER

**OneDrive Trigger Reliability Issues:**
- Widespread failures to detect new files (Feb-July 2025 reports)
- "Fetch test event" consistently fails even when files exist
- OneDrive for Business creates URL format errors
- Manual testing unreliable - must test in Active workflow mode
- **Impact:** May miss BU submissions, causing data gaps

**Excel Node Loop Processing Failures:**
- Excel node does not work reliably inside Loop Over Items nodes
- Fails to write, appends to wrong files, or processes only first iteration
- Unlike Google Sheets node which handles loops correctly
- **Impact:** Cannot reliably process multiple project sheets (P1-P10+)

**Empty Sheet Bug:**
- "Append or Update" operation fails if worksheet has only headers with no data rows
- Returns "No data found in the specified range" error
- **Workaround:** Manually add/delete dummy row
- **Impact:** First BU submission to consolidator may fail

### Known Issues Timeline
- **October 2024:** SharePoint support confirmed not working
- **May 2025:** Empty sheet append/update bug identified
- **August 2025:** Breaking change - removed "by name" retrieval (now ID-only)
- **Ongoing:** OneDrive trigger reliability problems across 2024-2025

### Recommended Workarounds

**Option A - HTTP Request + Graph API (Most Reliable):**
- Bypass Excel node entirely
- Use HTTP Request nodes with Microsoft Graph API directly
- Requires custom OAuth2 credentials with proper permissions
- More complex but significantly more reliable for SharePoint access

**Option B - Community Nodes:**
- Use `n8n-nodes-xlsx-to-json` for local Excel file conversion
- Use Bitovi's `n8n-nodes-excel` (Spreadsheet File node) for local processing
- Download file first, then process locally

**Option C - Google Sheets Hybrid:**
- Use OneDrive trigger to detect uploads
- Auto-convert Excel to Google Sheets via Google Drive API
- Process with Google Sheets node (much more reliable)

---

## 2. Dynamic Sheet Discovery & Looping

### Best Approaches

**For Cloud Excel Files (OneDrive/SharePoint):**
- Microsoft Excel 365 node → Sheet resource → "Get Many" operation
- Returns list of all worksheets
- **Problem:** Unreliable inside loops (see above)

**For Local Excel Files (Recommended):**
- Download file to local storage first
- Use Bitovi Spreadsheet File node → "List Sheets" operation
- Outputs JSON array of sheet names
- Feed into Loop Over Items node

**Filtering by Pattern (P1, P2, ..., Pn):**
```javascript
// Code node after sheet discovery
const items = $input.all();
const pattern = /^P\d+$/; // Matches P1, P2, P10, etc.
return items
  .filter(item => pattern.test(item.json.sheetName))
  .map(item => ({ json: item.json }));
```

### Looping Strategy

**Loop Over Items (Split in Batches) Node:**
- Set batch size = 1 for processing sheets one at a time
- Use expression `$('Loop Over Items').context['done']` for completion detection
- Prevents rate limiting and memory issues

**Workflow Pattern:**
```
Download File → List Sheets → Filter by Pattern → Loop Over Items →
Read Each Sheet → Merge Results → Transform → Append to Output
```

### Performance Considerations

- **Many Sheets:** Use batch processing to control throughput
- **Large Files:** Excel API limits responses to 5MB and ranges to 5 million cells
- **Memory:** Large files with many sheets consume significant memory
- **Timeouts:** May need to increase n8n execution timeout (default: 120s)

---

## 3. Google Sheets Node Research

### Why Google Sheets is Superior for This Use Case

**Append Operation:**
- Dedicated "Append Row" operation with two modes:
  - Standard: More API calls but ensures alignment
  - "Use Append" option: Native endpoint, 50% faster, recommended
- **Manual Column Mapping** strongly recommended over automatic mapping

**Reliability:**
- Correctly handles dynamic file IDs within Loop Over Items nodes
- No reported loop processing failures (unlike Excel node)
- Better community support and documentation

**Performance:**
- Batch API requests support up to 100 calls in single request
- Much better for large datasets (1000+ rows)

### Rate Limits & Quotas

**Google Sheets API (2025):**
- 300 read requests per minute per project
- 60 requests per minute per user (read + write)
- 2MB maximum payload recommendation
- 180-second timeout for long requests

**Handling Rate Limits:**
1. Retry On Fail with 60+ second wait between tries
2. Loop Over Items + Wait nodes between requests
3. Exponential backoff for 429 errors

**For This Project:**
- Appending 10 BUs × 5-10 projects each = 50-100 append operations
- At 60 requests/min, this takes ~1-2 minutes per submission
- Well within limits

### Authentication

**OAuth2 (Recommended):**
- Simpler setup
- For self-hosted: Requires Client ID/Secret from Google Cloud Console
- Must use exact redirect URI (including protocol and port)

**Service Account:**
- Better for server-to-server
- No user interaction needed
- More complex setup with JSON key files

---

## 4. n8n MCP Token Management

### Key Strategies

**File-Based Workflow Management:**
- Use `create_workflow_from_file`, `update_workflow_from_file`, `export_workflow_to_file`
- Bypasses token limits entirely
- Avoids passing large JSON through API context

**Minimal Data Retrieval:**
- Use `list_workflows_minimal` and `get_workflow_summary` for metadata only
- Reduces token consumption by 80-90%
- `get_execution` supports modes: preview, summary, filtered, full

**Known Bug:**
- Official n8n MCP server has verbose tool descriptions
- Causes Claude to hit token limits after 2-3 messages
- Third-party implementations (czlonkowski) optimize this

### Partial Updates

**CRITICAL LIMITATION:**
- n8n REST API does NOT support partial/PATCH updates
- Must GET entire workflow, modify, and PUT complete workflow back
- `n8n_update_partial_workflow()` exists in MCP but has validation errors

**Recommended Approach:**
1. Build initial workflow with full creation
2. Use file-based updates for major changes
3. For minor tweaks, use GET → modify → PUT pattern

### Best Practices

1. **Use Templates:** Start from 2,646+ pre-extracted configurations
2. **Modular Design:** Break workflows into reusable parts
3. **Error Handling First:** Implement Error Trigger nodes before deploying
4. **Version Control:** Export workflows as JSON to git
5. **Environment Separation:** Use environment variables for config

---

## 5. Error Handling Patterns

### Multi-Layer Error Strategy

**Layer 1 - Node-Level Settings:**
- "Retry on Fail" with configurable attempts and wait times
- "Continue on Error" to allow workflow to proceed despite failures
- Custom timeout configurations

**Layer 2 - Stop and Error Node:**
- Programmatically throw errors based on custom conditions
- Data validation and business rule enforcement
- Custom error messages

**Layer 3 - Error Workflows with Error Trigger:**
- Centralized error handling across multiple workflows
- Automatic execution when main workflow fails
- Access to detailed error information and execution context

**Layer 4 - Try/Catch Pattern:**
- Implemented via conditional branches + Stop and Error node
- Granular item-level error handling
- Continue processing subsequent items when one fails

### For File Processing Workflows

**Pre-Processing Validation:**
- Validate file formats, sizes, required fields BEFORE processing
- Use community nodes: `n8n-nodes-data-validation`, `n8n-nodes-input-validator`
- JSON Schema validation for structured data

**Error Recovery:**
- Implement compensating workflows for rollback
- Track processed files to prevent duplicate processing
- Idempotency by design (safe to retry)

**Structured Error Logging:**
- Capture file-specific metadata (filename, size, processing stage)
- Enable targeted troubleshooting and recovery

### Retry Strategies

**Exponential Backoff (Recommended):**
- Delays increase exponentially (1s, 2s, 4s, 8s, etc.)
- Use @n8n/p-retry package
- Better for rate limits and transient API failures

**Auto-Retry Workflows:**
- Pre-built templates query n8n API for failed executions
- Automatically resubmit failures on schedule (e.g., hourly)
- Filter out previously retried tasks

**Circuit Breaker Pattern:**
- Temporarily pause calls when external APIs fail beyond threshold
- Redirect to alternate flows
- Prevents cascading failures

### Notification Patterns

**Multi-Channel:**
- Slack, Discord, Telegram, Email (Gmail), SMS (Twilio), Mattermost
- Route by severity: Critical → SMS, Routine → Slack

**Contextual Error Messages Must Include:**
- Workflow name
- Execution ID
- Error message
- Failed node name
- Timestamp
- Links to execution details

**Error Aggregation:**
- For high-volume workflows, send summary reports
- Prevents notification fatigue

---

## 6. Recent n8n Excel Issues (Community Reports)

### Widespread Problems

**Authentication Failures (Ongoing):**
- GitHub Issue #20040: "Could not obtain a WAC access token" (403 forbidden)
- SharePoint-hosted Excel files particularly problematic
- Only works with n8n's built-in OAuth app (cannot customize)

**OneDrive Trigger Testing:**
- Manual "Fetch test event" unreliable (shouldn't be used for validation)
- Must test with workflow in Active state
- Initial trigger registration takes several minutes

**Performance Degradation:**
- Acceptable: 1,000-5,000 rows
- Problematic: 6,000+ rows or complex formulas
- Timeouts and failures become common at scale

**Incomplete Data Reads:**
- Spreadsheet Read node reported to read only partial data (e.g., 50 of 300+ rows)
- No error messages - silent failures
- **CRITICAL:** Must implement row count validation

### Strategic Recommendations from Community

1. **Hybrid Approach:**
   - Use OneDrive trigger for file detection only
   - Use HTTP Request + Graph API for actual file operations
   - Bypass problematic Excel node entirely

2. **Validation Layer:**
   - Comprehensive data integrity checks (row counts, schema validation)
   - Duplicate detection
   - Silent failure monitoring

3. **Fallback Mechanisms:**
   - Manual trigger options when automatic polling fails
   - Alternative processing paths

4. **Performance Testing:**
   - Test with realistic BU file sizes early
   - 10 BUs × 10 projects × 100 rows = potential 10,000 row processing
   - May need chunking or pagination

5. **Error Visibility:**
   - Extensive logging for debugging
   - Notifications for silent failures
   - Track each BU submission separately

---

## Risk Assessment

### HIGH RISK Issues

1. **Excel Node + Loop Processing:** Documented failure mode for core workflow requirement
2. **OneDrive Trigger Reliability:** May miss BU submissions entirely
3. **SharePoint/Business OneDrive:** May not work at all with organizational accounts
4. **Silent Failures:** Incomplete data reads without errors

### MEDIUM RISK Issues

1. **Performance at Scale:** 6,000+ rows cause timeouts
2. **Rate Limiting:** Multiple rapid submissions may hit API limits
3. **Authentication Complexity:** OAuth setup more complex than expected
4. **First-Time Setup:** Empty sheet bug on initial consolidator setup

### LOW RISK Issues

1. **Error Handling Complexity:** Well-documented patterns available
2. **Token Management:** File-based approach mitigates concerns
3. **Google Sheets Alternative:** Proven reliable solution exists

---

## Recommended Implementation Strategy

### Option 1: Google Sheets Native (LOWEST RISK) ⭐ RECOMMENDED

**Approach:**
1. BUs upload Excel files to OneDrive (current process)
2. OneDrive trigger detects new files
3. **Download Excel file as binary**
4. **Use community node (Spreadsheet File) to convert Excel → JSON locally**
5. Transform data in n8n (Function/Set nodes)
6. **Append to Google Sheets consolidator**

**Advantages:**
- ✅ Avoids all Excel node issues
- ✅ Avoids OneDrive trigger issues (just detect, don't process)
- ✅ Reliable looping with Google Sheets
- ✅ Better performance at scale
- ✅ Proven community patterns

**Disadvantages:**
- BUs still submit Excel, but output is Google Sheets
- Requires Google Cloud setup (one-time)

**Risk Level:** LOW

---

### Option 2: Excel to Excel with Workarounds (MEDIUM-HIGH RISK)

**Approach:**
1. OneDrive trigger (Active mode only, no manual testing)
2. HTTP Request + Microsoft Graph API for file reading
3. Custom JSON parsing of Excel structure
4. Transform data
5. HTTP Request + Graph API to append to Excel consolidator

**Advantages:**
- ✅ Pure Excel solution (input and output)
- ✅ Bypasses problematic Excel node

**Disadvantages:**
- ❌ Complex Graph API integration
- ❌ SharePoint authentication may still fail
- ❌ Custom Excel parsing logic required
- ❌ More maintenance burden

**Risk Level:** MEDIUM-HIGH

---

### Option 3: Hybrid Excel Input → Google Sheets Output (BALANCED) ⭐ ALSO RECOMMENDED

**Approach:**
1. OneDrive trigger detects Excel uploads
2. Download Excel file
3. Google Drive API: Upload Excel → auto-convert to Google Sheets
4. Process with Google Sheets node (read sheets dynamically)
5. Transform data
6. Append to Google Sheets consolidator

**Advantages:**
- ✅ Accepts Excel from BUs (no process change)
- ✅ Uses reliable Google Sheets for processing
- ✅ Auto-conversion built into Google Drive API
- ✅ Reliable looping and appending

**Disadvantages:**
- Requires both Microsoft and Google authentication
- File format conversion step adds complexity

**Risk Level:** LOW-MEDIUM

---

## Implementation Recommendations

### Phase 1: Proof of Concept (1-2 days)

**Build minimal workflow to test:**
1. OneDrive trigger detection (test in Active mode with real file)
2. Excel file download
3. Convert to JSON (community node)
4. Append single row to Google Sheets

**Success Criteria:**
- Trigger reliably detects files
- Excel parsing extracts all fields correctly
- Google Sheets append works

### Phase 2: Dynamic Sheet Processing (2-3 days)

**Add complexity:**
1. Implement sheet discovery (list all P* sheets)
2. Loop Over Items with batch size = 1
3. Process each sheet individually
4. Merge results
5. Test with 3, 5, 10, and 15 project sheets

**Success Criteria:**
- Correctly processes variable numbers of sheets
- No loop failures
- All data extracted

### Phase 3: Transformation & Validation (2-3 days)

**Build transformation logic:**
1. Map vertical form → 79-column horizontal row
2. Generate composite UUID
3. Extract metadata from filename
4. Validate required fields
5. Calculate "Days to Target" fields

**Success Criteria:**
- All 79 columns map correctly
- Data validation catches errors
- UUID generation works

### Phase 4: Error Handling & Monitoring (1-2 days)

**Add resilience:**
1. Error Trigger workflow
2. Retry logic for transient failures
3. Notifications (Slack/Email)
4. Row count validation
5. Duplicate submission detection

**Success Criteria:**
- Failures trigger notifications
- Retries work automatically
- Silent failures detected

### Phase 5: Production Testing (1 week)

**Real-world validation:**
1. Test with all 10 BU file formats
2. Parallel submission testing
3. Monitor for 1 week with real data
4. Performance monitoring

**Success Criteria:**
- 100% submission capture rate
- No data loss
- <5 minute processing time per submission

---

## Questions for Decision

### 1. OneDrive Location Confirmation

**Question:** Where exactly will BUs upload files?
- Personal OneDrive?
- OneDrive for Business?
- SharePoint site?

**Why it matters:** Determines if Excel node can work at all vs requiring HTTP Request workaround.

### 2. Output Format Preference

**Question:** Must the consolidator be Excel, or is Google Sheets acceptable?

**Why it matters:** Google Sheets output dramatically reduces risk and complexity.

### 3. Real-time Requirements

**Question:** How quickly must submissions be processed?
- Real-time (minutes)?
- Hourly batch?
- Daily batch?

**Why it matters:** Affects trigger polling frequency and error handling urgency.

### 4. File Size Expectations

**Question:** What's the realistic size of BU submission files?
- Number of projects per BU (average and maximum)?
- Rows of data per project?

**Why it matters:** Determines if we'll hit performance limits requiring chunking.

### 5. Historical Data

**Question:** Do you have sample files from previous manual consolidations?

**Why it matters:** Need real BU file formats for testing and mapping validation.

---

## Next Steps (Pending Your Decisions)

1. **Review this research summary**
2. **Answer the 5 decision questions above**
3. **Choose implementation strategy** (Option 1, 2, or 3)
4. **Provide sample BU files** for testing
5. **Confirm OneDrive/SharePoint access details**

Once decisions are made, we can proceed to implementation with appropriate risk mitigation strategies.

---

**Status:** ✅ Research Complete - Awaiting Implementation Decisions
**Last Updated:** 2025-10-22
