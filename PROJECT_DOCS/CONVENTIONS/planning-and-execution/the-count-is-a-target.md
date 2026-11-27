# The count is a target

The periodic review interval's count is the output of `just plan-count`: the commits since the base
`.devpro-temp/plan-count-base` names, then the commit subjects claiming a plan's landing, then that
claim count and the commit count.

- The base is a file, not a literal in the recipe: the landing commit of the last periodic review
  writes its own full hash there, the receipt claiming the landing. Its subject claims no landing,
  so the review's own commit is outside the count, and a receipt that did not land is outside none
  of it.
- A plan's landing commit says in its subject that it lands a plan; a periodic review's says it
  lands a periodic review. The target matches a subject holding "land"/"lands" then "plan", or
  "plan" then "lands" — so "lands a plan", "lands the plan", "the plan lands" and "Land plan P3" all
  count. `just plan-count lands` shows every claiming subject for a reader to judge the pattern
  against; the target emits candidates, never verdicts, as the sweep and spelling recipes do.
- The target reads git and one file, and writes nothing.

*Purpose:* the count is a machine's answer, not a number kept in prose or in a plan's drafting; the
machine's half is the number, the author's half is the subject that makes a landing one.
