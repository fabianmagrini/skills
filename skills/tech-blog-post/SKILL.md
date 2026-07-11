---
name: tech-blog-post
description: Write a detailed technical blog post from an existing analysis document (architecture analysis, onboarding guide, deep-dive, etc.) and save it as a self-contained HTML file with syntax highlighting, visual hierarchy, and no external dependencies. Use when you have an architecture.md, deep-dive, or research doc and want to publish it as a readable, well-designed article.
compatibility: Requires an existing analysis document (Markdown or plain text). Produces a single self-contained HTML file with no CDN or external dependencies.
allowed-tools: Read Glob Grep Write
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-07-11
---

Transform an existing technical analysis document into a polished, self-contained HTML blog post — readable, well-structured, and publishable without any build tools or CDN dependencies. This skill pairs naturally with `/reverse-engineer`, `/onboard-codebase`, `/tech-deep-dive`, and `/learn-technology`, which produce the source material.

## Determine the inputs

Required:
- `{source}` — path to the analysis document (Markdown `.md`, plain text `.txt`, or any readable format)

Optional:
- `{title}` — override the post title (default: derived from the document's first heading or filename)
- `{author}` — author name to display in the byline (default: omit byline)
- `{output}` — output filename (default: `{source-basename}.html` in the same directory)
- `--inline` — print the HTML to the conversation instead of writing a file

If the source file does not exist, stop and ask the user to provide the correct path.

## Discovery steps

### 1. Read and parse the source document

Read the full source document. Identify:
- The main title (first `#` heading, or the filename stem)
- The section structure (heading hierarchy: `##`, `###`)
- Any code blocks and their languages (for syntax highlighting)
- Tables, lists, blockquotes, and callout patterns
- Any diagrams described in Mermaid or ASCII art

Note the approximate word count — posts under 800 words get a simpler single-column layout; longer posts get a table of contents.

### 2. Identify the target audience and tone

From the document content, infer:
- Is this aimed at contributors, engineers, or a general technical audience?
- Is the tone formal (RFC, ADR) or conversational (deep-dive, onboarding)?
- Are there opinionated conclusions or is it primarily descriptive?

Match the HTML's typographic choices and intro paragraph to this tone.

### 3. Plan the post structure

Map the source document sections to blog post sections. Decide:
- Which sections should be combined, split, or reordered for narrative flow
- Whether a TL;DR or key-takeaways callout box belongs at the top
- Whether a "Why this matters" opening paragraph should be synthesized (it should, if the source doc jumps straight into detail)

Do not invent technical facts. If you add framing, label it clearly or make it indistinguishable from the document's own voice.

## Output requirements

The output must be a **single, self-contained HTML file**:

- **No external dependencies**: no CDN links, no Google Fonts, no external scripts or stylesheets
- **Syntax highlighting**: implement via a minimal inline `<style>` block with token classes, or use `<pre><code>` with CSS-only highlighting for the languages present
- **Visual hierarchy**: use typographic scale, spacing, and color to distinguish headings, body, code, and callouts — do not produce a wall of unstyled text
- **Readable at 600–800px column width**: use `max-width` and `margin: auto` so it looks good on desktop and mobile without a framework
- **Dark/light**: default to a light theme unless the source document's subject matter strongly implies otherwise
- **Tables**: render as proper `<table>` elements, not ASCII
- **Code blocks**: wrap in `<pre><code class="language-{lang}">` with background, border-radius, and horizontal scroll
- **Callouts / blockquotes**: style distinctively (left border or tinted background)
- **Metadata line**: include generated date and, if `{author}` is provided, author name below the title

### Inline CSS approach

All styles go in a single `<style>` block in `<head>`. Use CSS custom properties for colors so the file is easy to retheme:

```css
:root {
  --bg: #ffffff;
  --fg: #1a1a1a;
  --accent: #2563eb;
  --code-bg: #f4f4f5;
  --border: #e4e4e7;
  --muted: #71717a;
}
```

### Syntax highlighting without a library

For code blocks, use a CSS-only approach: wrap token types in `<span class="kw">`, `<span class="str">`, `<span class="cm">` etc. and style them. Only highlight code if you can do so accurately for the languages present — otherwise leave code unstyled in `<pre><code>` blocks rather than producing incorrect highlighting.

## Output format

Write the HTML file to `{output}`. After writing, print:

```
Blog post written: {path}
Title: {title}
Sections: {N}
Word count (approx): {N}
Code blocks highlighted: {languages}
```

If `--inline` is passed, print the full HTML to the conversation instead of writing a file.

## Examples

```
/tech-blog-post architecture.md
```
Converts `architecture.md` to `architecture.html` in the same directory.

```
/tech-blog-post redis-deep-dive.md --author "Fabian Magrini"
```
Adds a byline to the generated post.

```
/tech-blog-post onboarding.md --output docs/blog/onboarding-guide.html
```
Writes the post to the specified output path.

```
/tech-blog-post reverse-engineer-output.md --inline
```
Prints the HTML to the conversation for review before saving.

## Gotchas

- **Do not hallucinate content.** The blog post must be a faithful rendering of the source document. You may add a short opening paragraph to frame the post, but all technical claims must come from the source.
- **Mermaid diagrams cannot be rendered without JavaScript.** If the source contains Mermaid blocks, render them as styled `<pre>` code blocks and note that a Mermaid renderer is required to view them as diagrams.
- **ASCII art diagrams** should be preserved in `<pre>` blocks with a monospace font — they often convey architecture clearly as-is.
- **Long documents produce large HTML files.** For documents over 5 000 words, generate a floating table of contents using `<nav>` with anchor links to each section heading.
- **Markdown tables** should be converted to semantic `<table>` HTML — do not leave them as pipe-delimited text.
- **Check the output path exists** before writing. If the parent directory does not exist, ask the user whether to create it or choose a different path.
- This skill pairs naturally with `/reverse-engineer` (generates architecture analysis), `/onboard-codebase` (generates onboarding guide), `/tech-deep-dive` (generates deep-dive), and `/learn-technology` (generates learning materials) — all of which produce suitable source documents.
