# PROJECT CONTEXT - LOGGING PROTOCOL

**⚠️ IMPORTANT**: All agents working on this project MUST follow this logging protocol.

## Overview

This project uses a structured execution logging system to maintain context across multiple agent sessions and prevent context window bloat. When you (an agent) complete work, you MUST update the execution logs.

## Your Responsibilities as an Agent

### 1. Before Starting Work (REQUIRED)

**Read `execution_log.md`** to understand:
- What work has been completed by previous agents
- What phase the project is currently in
- What challenges previous agents encountered
- What specific work YOU should focus on
- What decisions have already been made

**This prevents duplicate work and ensures continuity.**

### 2. During Work (TRACK EVERYTHING)

Track the following as you work:
- ✅ All commands you run (with full output)
- ✅ All files you create or modify
- ✅ Design decisions you make and the rationale
- ✅ Challenges you encounter and how you resolve them
- ✅ Any research you conduct (APIs, libraries, patterns)
- ✅ Test results and validation outcomes

### 3. After Completing Work (REQUIRED - DO NOT SKIP)

You MUST update two files:

**A. Create Detailed Summary** (`execution_logs/[phase]_summary_[n].md`)

**B. Update Execution Log** (`execution_log.md`)

## How to Create Your Detailed Summary

### Determine Your Filename

**Format**: `execution_logs/[phase]_summary_[n].md`

**Phase** - Which PRP phase are you working on?
- `research` - External API research, domain analysis, integration planning
- `architecture` - System design, component structure, data flow
- `implementation` - Code writing, feature development
- `testing` - Test creation, validation gates
- `validation` - Final checks, deployment prep
- `bugfix` - Fixing issues found during testing
- `refactor` - Code improvements, optimization

**Number** - Chronological order within this phase:
1. List files in `execution_logs/` directory
2. Count files matching your phase (e.g., count files starting with `research_summary_`)
3. Your number is: count + 1

**Examples**:
- First agent doing research → `research_summary_1.md`
- Second agent doing research → `research_summary_2.md`
- First agent doing implementation → `implementation_summary_1.md`
- Second agent doing implementation → `implementation_summary_2.md`

### Use the Summary Template

Copy `.templates/agent_summary_template.md` and fill in ALL sections:

```bash
cp .templates/agent_summary_template.md execution_logs/[phase]_summary_[n].md
```

**Required Sections**:
1. **Task Assignment** - What were you asked to do?
2. **Context Received** - What did you learn from execution_log.md?
3. **Work Performed** - Files created/modified, research conducted, design decisions
4. **Commands Executed** - Every command with full output
5. **Challenges Encountered** - Problems and how you solved them
6. **Validation Results** - Test results, coverage reports
7. **Handoff Notes** - Critical info for next agent
8. **Artifacts Produced** - Links to all deliverables

**BE THOROUGH** - Future agents will read this to understand your work.

## How to Update execution_log.md

### Step 1: Add TOC Entry

At the **bottom of the Table of Contents section**, add:

```markdown
- [{Your Agent Name} - {Phase}](#your-agent-name-phase-timestamp)
```

**Example**:
```markdown
- [data-engineer - Research](#data-engineer-research-2025-01-26-143022)
```

### Step 2: Add Compact Entry

At the **bottom of Agent Execution Entries section**, add:

```markdown
### {Agent Name} - {Phase} - {YYYY-MM-DD HH:MM:SS}

**Role**: {One sentence describing what you do}
**Task**: {One sentence describing what you were asked to do}
**Detailed Summary**: [`{phase}_summary_{n}.md`](execution_logs/{phase}_summary_{n}.md)

**Work Completed**:
- {Key accomplishment 1 - max 1 line}
- {Key accomplishment 2 - max 1 line}
- {Key accomplishment 3 - max 1 line}
- {Key accomplishment 4 - max 1 line}
- {Key accomplishment 5 - max 1 line}

**Commands Run**:
```bash
{command 1}  # Result: {brief result}
{command 2}  # Result: {brief result}
{command 3}  # Result: {brief result}
```

**Status**: ✅ Completed | ⚠️ Partial | ❌ Blocked
**Next Agent**: {Next agent name if known, or "TBD"}

---
```

**IMPORTANT**: Keep this compact (max 10 lines excluding code blocks)

## Logging Best Practices

### Keep Execution Log COMPACT
- ❌ Don't paste full command output in execution_log.md
- ✅ Do provide brief result summary
- ❌ Don't explain HOW you did something
- ✅ Do explain WHAT you accomplished
- ❌ Don't duplicate content from detailed summary
- ✅ Do link to detailed summary for full context

### Make Detailed Summaries COMPREHENSIVE
- ✅ Include all commands with FULL output
- ✅ Document every design decision with rationale
- ✅ Explain challenges and how you solved them
- ✅ Provide context for next agent
- ✅ Link to all artifacts you created

### Update Files in Correct Order
1. First: Create detailed summary (`execution_logs/[phase]_summary_[n].md`)
2. Second: Update execution log (`execution_log.md`)

This ensures you have the summary link ready when updating the execution log.

### Handle Parallel Agents Correctly
- If you finish before a parallel agent, add your entry first
- Your TOC entry appears before theirs
- Your execution entry appears before theirs
- **Chronology = order of completion, not order of launch**

## Example: Good vs Bad Logging

### ❌ BAD - Too Verbose in execution_log.md

```markdown
### data-engineer - Research - 2025-01-26 14:30:22

**Role**: Research best practices for pandas DataFrame operations and openpyxl cell reading patterns
**Task**: I was asked to research how to efficiently extract 76 fields from Excel workbooks using pandas and openpyxl, with particular attention to handling formulas, merged cells, and data type validation. I also needed to investigate deduplication strategies using hash-based approaches.

**Work Completed**:
- Researched pandas read_excel() method and found that using openpyxl engine is best for .xlsx files
- Discovered that formulas in cells can be evaluated using the data_only=True parameter
- Found that merged cells should be detected using worksheet.merged_cells property
- Investigated xxhash and hashlib for fast hashing
- Created detailed research document with 15 pages of findings

[... continues for 50 more lines]
```

**Problems**:
- Too detailed in main log (should be in summary)
- No link to detailed summary
- Will bloat context window quickly

### ✅ GOOD - Compact Main Log, Detailed Summary

**execution_log.md**:
```markdown
### data-engineer - Research - 2025-01-26 14:30:22

**Role**: ETL pipeline expert researching pandas/openpyxl patterns
**Task**: Research 76-field Excel extraction strategies
**Detailed Summary**: [`research_summary_1.md`](execution_logs/research_summary_1.md)

**Work Completed**:
- Researched pandas read_excel() with openpyxl engine patterns
- Investigated formula evaluation and merged cell handling
- Designed hash-based deduplication strategy (xxhash vs hashlib)
- Documented 15 Excel gotchas and workarounds
- Created field extraction pattern recommendations

**Commands Run**:
```bash
python -m pip list | grep pandas  # Result: pandas 2.1.4
python -m pip list | grep openpyxl  # Result: openpyxl 3.1.2
```

**Status**: ✅ Completed
**Next Agent**: backend-architect (for architecture design)

---
```

**execution_logs/research_summary_1.md**: [Contains full 15 pages of research with all details]

**Benefits**:
- Main log stays compact
- All details preserved in summary
- Easy to scan chronologically
- Future agents know where to look for deep context

## Special Cases

### If You Encounter Blockers

Mark status as ❌ Blocked and explain:

```markdown
**Status**: ❌ Blocked
**Blocker**: Missing API key for Pinecone - need user to provide in .env file
**Next Agent**: Awaiting user input before continuing
```

### If Work is Partial

Mark status as ⚠️ Partial and explain:

```markdown
**Status**: ⚠️ Partial (3 of 5 validation gates passed)
**Remaining Work**:
- Integration tests failing (2 test cases)
- E2E tests not yet run
**Next Agent**: Same agent will retry after fixes, or new agent to complete
```

### If You're Updating Someone Else's Work

Still create your own summary with a new number:

```markdown
# bugfix_summary_1.md
# Even if you're fixing implementation_summary_1.md issues

This maintains chronological order and clear accountability.
```

## Questions?

If you're unsure how to log your work, follow this rule:

**"What would the next agent need to know to continue my work without reading my mind?"**

Log that information in your detailed summary, and link to it from the execution log.

---

## Quick Checklist Before Finishing Your Work

- [ ] Read execution_log.md before starting
- [ ] Tracked all commands run
- [ ] Tracked all files created/modified
- [ ] Tracked all design decisions
- [ ] Created detailed summary: `execution_logs/[phase]_summary_[n].md`
- [ ] Updated execution_log.md with compact entry
- [ ] Added TOC link at bottom of TOC section
- [ ] Added execution entry at bottom of entries section
- [ ] Verified links work
- [ ] Status accurately reflects work state (✅/⚠️/❌)

If all boxes checked: ✅ You're done! Next agent can take over.
