# Segment fidelity — what does not survive a translation cleanly

Check every changed segment against this before proposing the plan, not after writing the
variant. Each item below is something to **say out loud in Phase 3**, because the user can
decide what to do about it and the skill cannot.

The rule underneath all of it: **flag, never silently restructure.** A variant that quietly
reflowed a table to make the text fit is worse than one that reports the table will not fit,
because nobody will notice the first one until a client does.

## Text expansion

German and French commonly run 15–30% longer than English; Finnish and Hungarian longer
still. CJK is usually shorter but taller once it wraps. That matters wherever width is
fixed:

- **Table cells** — the usual casualty. A three-column comparison table that fits in
  English will wrap to two lines per cell in German and push the table onto a second page.
- **Headings** that fit one line in the source and wrap in the target, breaking the visual
  rhythm of a document that was laid out by hand.
- **Buttons, labels, captions, figure titles** — anything with a box around it.
- **Fixed-width layouts**: slide text boxes, form fields, anything with a hard boundary.

Say which segment, which locale, and what will happen — "the feature comparison table in
section 4 will run to two lines per cell in DE and FR" — not "some formatting issues".

## Structure that carries meaning

- **Cross-references** — "see section 3.2 above" survives only if the target has the same
  numbering. If sections were added or reordered, the reference is now wrong in a way no
  spell-check finds.
- **Alphabetical ordering.** A list sorted A–Z in English is not sorted in any other
  language. Decide per family whether to re-sort or preserve order; do not do either
  silently.
- **Defined terms**, where a contract says *"the Services (as defined in clause 2)"*. The
  defined term and every use of it must move together or the definition breaks.
- **Numbered or lettered sub-clauses** referenced elsewhere in the document.

## Things that should not be translated

- **Product and feature names**, unless the family glossary says otherwise.
- **Legal entity names**, registration numbers, addresses.
- **Code, commands, file paths, API field names, config keys.**
- **Quoted third-party text** — a quotation from a regulation must use that regulation's
  own published translation, not a fresh one.
- **UI strings that must match the actual interface** the reader is looking at. If the
  product ships in English only, translating a menu name in the manual makes it unfindable.

When in doubt, leave it and flag it. An untranslated term is a visible question; a
wrongly-translated one is an invisible error.

## Format-specific traps

| Format | What breaks |
|---|---|
| `.docx` | Assigning to a paragraph's `.text` collapses every run into one and loses all inline styling. Replace run text instead. Tracked changes and comments do not carry across |
| `.pdf` | Not editable in place. A translated PDF has to be regenerated from its source, and if the source is gone the family cannot be synced — say so rather than producing a lossy rebuild |
| Slides | Text boxes are fixed size and do not reflow. Expansion overflows the shape rather than wrapping |
| Spreadsheets | Formulas referencing sheet names or column headers break when those are translated. Translate cell *values*, not structural names, unless the family rule says to |
| Markdown / docs-as-code | Link anchors are generated from heading text, so translating a heading breaks every link to it |

## Numbers, dates, units

These look like formatting and behave like meaning:

- **Decimal separators** — `1,234.56` in English is `1.234,56` in German. Getting this wrong
  changes a price by three orders of magnitude.
- **Date order** — 03/04/2026 is two different days depending on the locale. Prefer an
  unambiguous form.
- **Currency** — convert the *symbol placement*, never the amount. An amount is a fact from
  the source document and is not this employee's to change.
- **Units** — do not convert metric to imperial unless the family rule says to. A
  specification that says 2 m means 2 m in every locale.

## What to write in the plan

For each flagged segment, one line: the locale, where it is, what the problem is, and what
you propose. For example:

> **DE, section 4 table** — the three-column feature table will wrap to two lines per cell
> and push onto page 3. Propose translating it as-is and flagging the layout for the owner,
> rather than abbreviating the German to fit.

That gives the user the decision. Abbreviating the German to preserve the layout is a
legitimate choice — but it is theirs, not yours.
