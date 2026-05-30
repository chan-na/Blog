---
name: post
description: Publish a bilingual (Korean + English) blog post from a Korean markdown draft. Reads a Korean markdown file (body only, no front matter) provided by the user, derives front matter (title, slug, summary, tags, categories, date, translationKey), writes the Korean post to content/posts/<slug>.md, translates the body to English, and writes the English post to content/posts/<slug>.en.md. Use this skill when the user invokes /post with a path to a Korean draft, or asks to turn a Korean markdown file into a paired ko/en blog post for this Hugo + PaperMod blog.
---

# Korean draft → bilingual blog post

This skill turns a Korean markdown draft (body only) into a paired set of bilingual posts for this Hugo + PaperMod blog. The user runs `/post <path-to-korean-draft>`; you produce `content/posts/<slug>.md` (Korean) and `content/posts/<slug>.en.md` (English).

## Input

The user provides a path to a Korean markdown file. Treat the file contents as **body only** — there is no front matter to parse. You generate all front matter yourself.

If the user invokes the skill without a path, ask them which file to use before doing anything else.

## Steps

### 1. Read the draft
Read the file at the given path. Do not modify it — it's the user's source.

### 2. Derive a slug
A short kebab-case English slug summarizing the topic (3–6 words). Examples from existing posts: `blog-start`, `hugo-papermod-pitfalls`.

- If the input filename (without `.md`) already looks like a slug (English, kebab-case, no spaces), reuse it as-is.
- Otherwise infer one from the content's main topic.

### 3. Check for collisions
If `content/posts/<slug>.md` or `content/posts/<slug>.en.md` already exists, **stop and ask** the user whether to overwrite or pick a different slug. Never silently overwrite.

### 4. Derive Korean front matter
- `title`: If the body's first non-empty line is an H1 (`# ...`), use that text as the title and strip the H1 line from the body (PaperMod renders the title separately — don't repeat it). Otherwise infer a concise Korean title from the content.
- `summary`: one Korean sentence that would appear on the post listing card.
- `tags`: 2–5 short Korean tags (e.g. `["블로그", "시작"]`). Tech/tool keywords (framework names like `hugo`, `papermod`, `react`) stay lowercase English and can repeat across both files.
- `categories`: 1–2 Korean categories. Mirror existing conventions where they apply (`메타`, `개발`, `블로그` — see existing posts).
- `date`: the actual current time in KST, formatted `YYYY-MM-DDT HH:MM:SS+09:00` (no space — `YYYY-MM-DDTHH:MM:SS+09:00`). Get it by running `TZ=Asia/Seoul date '+%Y-%m-%dT%H:%M:%S+09:00'` — do **not** hardcode a time. Using the real run time keeps multiple posts published on the same day sorted in publication order (Hugo sorts by `date`, and identical timestamps make the order ambiguous).
- `translationKey`: same value as `slug`.
- `draft`: `false`.

### 5. Write the Korean file
Write `content/posts/<slug>.md`:

```yaml
---
title: "..."
date: 2026-05-28T10:00:00+09:00
draft: false
slug: "..."
translationKey: "..."
categories: [...]
tags: [...]
summary: "..."
---

<body, with the first H1 stripped if you used it as the title>
```

Double-quote string values. Match the format used by `content/posts/blog-start.md` and `content/posts/hugo-papermod-pitfalls.md`.

### 6. Translate the body to English
Translate the body following the style of this blog's existing English posts (`content/posts/blog-start.en.md`, `content/posts/hugo-papermod-pitfalls.en.md`):

- Direct, technical, peer-to-peer tone. No padding phrases ("In this post, we will explore..."). Active voice.
- Korean polite endings (`~합니다`, `~입니다`) become natural English, not stiff formal phrasing.
- Past tense for what the author did; present for what the code does.

**Translate:**
- Headings (preserve heading levels exactly)
- Body prose
- Captions and human-readable comments inside code blocks
- Quoted strings only when they are clearly UI copy or user-facing text

**Preserve as-is:**
- Code identifiers, config keys, file paths, command names, URLs
- Code block fence languages
- Markdown structure: list bullets, links, tables, blockquotes
- Inline code spans

### 7. Derive English front matter
- `title`: translation of the Korean title.
- `summary`: translation of the Korean summary.
- `tags`: English equivalents. Tech-keyword tags (`hugo`, `papermod`, `i18n`, etc.) stay the same across both files. Korean-only concept tags get translated (e.g. `시작` → `intro`).
- `categories`: English equivalents. Mirror existing conventions: `메타` ↔ `Meta`, `개발` ↔ `Engineering`, `블로그` ↔ `Blog`.
- `date`, `slug`, `translationKey`, `draft`: same as the Korean file.

### 8. Write the English file
Write `content/posts/<slug>.en.md` with the English front matter and the translated body.

### 9. Report
Print:
- The two file paths created
- The slug
- The Korean and English titles
- The suggested commit command, for the user to run if they want:
  ```bash
  git add content/posts/<slug>.md content/posts/<slug>.en.md
  git commit -m "post: <short description>"
  ```

**Do not** run `git add`, `git commit`, or `git push` yourself. The user reviews the diff and commits.

## Front matter reference (from existing posts)

- All string values use double quotes.
- `date` is local +09:00 (KST); use the actual current run time (see step 4), not a fixed time.
- `translationKey` and `slug` are identical between the `.md` and `.en.md` files.
- Hugo + PaperMod treats `<slug>.en.md` as the English translation of `<slug>.md` automatically — no other wiring needed.

## Category / tag mapping (extend as needed)

Korean | English
--- | ---
메타 | Meta
개발 | Engineering
블로그 | Blog
시작 (tag) | intro

Tech-keyword tags (lowercase, identical in both files): `hugo`, `papermod`, `github-pages`, `i18n`, `giscus`, etc.

## Constraints

- Never overwrite an existing file in `content/posts/`. Ask first.
- Never modify the input draft file. Read-only.
- Never auto-commit or push.
- Do not invent the date/time. Get the real current KST timestamp at run time via `TZ=Asia/Seoul date '+%Y-%m-%dT%H:%M:%S+09:00'`.
