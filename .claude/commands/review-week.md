# Review Weekly Journal

Review the fitness journal for the past week and update the weekly routine based on observations.

## Input

Date to review from (format: YYYY-MM-DD): $ARGUMENTS

If no date is provided, use today's date.

## Instructions

1. **Read the journal** (`journal.md`) and find all entries from the 7 days prior to and including the specified date.

2. **Analyze the week's training:**
   - Which exercises felt good (low RPE relative to load/reps)?
   - Which exercises were challenging or approached failure?
   - Any recurring themes in "What was challenging" or "Next session focus" notes?
   - Energy levels and sleep patterns across the week
   - Were all planned workout days completed?

3. **Compare against the weekly routine** (`weekly_routine.md`):
   - Is the prescribed volume being completed?
   - Are the weight targets (% of bodyweight) being met?
   - Are rep ranges being achieved or exceeded?
   - Any exercises consistently underperforming?

4. **Propose routine updates** based on patterns observed:
   - **Progressions**: If RPE is consistently low (5-6) and reps are at top of range, suggest increasing weight or adding reps
   - **Regressions**: If RPE is consistently high (8-9) or failing reps, suggest reducing weight or using easier variations
   - **Volume adjustments**: If recovery seems poor (low energy, high RPE), consider reducing sets; if recovery is great, consider adding
   - **Exercise swaps**: If an exercise is consistently problematic, suggest alternatives from the regression options

5. **Present findings** in this format:

   ### Week in Review: [date range]

   **Sessions Completed:** X/3

   **Highlights:**
   - [What went well]

   **Areas of Concern:**
   - [What needs attention]

   **Recommended Routine Updates:**
   - [ ] [Specific change with rationale]

6. **After user approval**, edit `weekly_routine.md` with the agreed-upon changes. Add a comment at the top noting the update date and summary of changes.
