---
name: post
description: Publish a bilingual (Korean + English) blog post from a Korean markdown draft. Reads a Korean markdown file (body only, no front matter) provided by the user, polishes the Korean prose with the humanize-korean skill, derives front matter (title, slug, summary, tags, categories, date, translationKey), writes the Korean post to content/posts/<slug>.md, translates the body to English with a native-copywriter persona prompt, polishes that English with the humanizer skill, and writes the English post to content/posts/<slug>.en.md. Use this skill when the user invokes /post with a path to a Korean draft, or asks to turn a Korean markdown file into a paired ko/en blog post for this Hugo + PaperMod blog.
---

# Korean draft → bilingual blog post

This skill turns a Korean markdown draft (body only) into a paired set of bilingual posts for this Hugo + PaperMod blog. The user runs `/post <path-to-korean-draft>`; you produce `content/posts/<slug>.md` (Korean) and `content/posts/<slug>.en.md` (English).

Non-prose is masked once, at the start, and stays masked. Prose and diagram
strings then travel on separate tracks and meet again at the end:

```
draft.md
 └─ mask ─┬─ prose ──→ humanize-korean ──→ unmask ──→ content/posts/<slug>.md
          │              └─ translate (persona) ─→ humanizer ─┐
          │                                                   ├─ unmask ─→ <slug>.en.md
          └─ blocks ─→ extract strings ─→ translate ─→ apply ─┘
```

A diagram block is 90% hand-placed coordinates and 10% words. Only the words
move; the markup is never regenerated, so coordinates cannot drift.

## Input

The user provides a path to a Korean markdown file. Treat the file contents as **body only** — there is no front matter to parse. You generate all front matter yourself.

If the user invokes the skill without a path, ask them which file to use before doing anything else.

Options the user may add in plain language:
- **"윤문 생략" / `--no-humanize`** — skip both polish passes (steps 5 and 10) and go straight from the draft to the posts. Say so in the report.
- **"한글 윤문만" / "영문 윤문만"** — run only that side's polish pass.
- **강도 (보수 | 기본 | 적극)** — passed through to `humanize-korean`. Default: let the skill pick.

## Working directory

Intermediates go in `_workspace/post-<slug>/` at the repo root. `humanize-korean` writes its own `_workspace/<YYYY-MM-DD-NNN>/` there too. `/_workspace/` is gitignored — never add it to a commit, and never write intermediates into `content/`.

## Steps

### 1. Read the draft
Read the file at the given path. Do not modify it — it's the user's source.

### 2. Derive a slug
A short kebab-case English slug summarizing the topic (3–6 words). Examples from existing posts: `blog-start`, `hugo-papermod-pitfalls`.

- If the input filename (without `.md`) already looks like a slug (English, kebab-case, no spaces), reuse it as-is.
- Otherwise infer one from the content's main topic.

### 3. Check for collisions
If `content/posts/<slug>.md` or `content/posts/<slug>.en.md` already exists, **stop and ask** the user whether to overwrite or pick a different slug. Never silently overwrite.

### 4. Split the title, then mask the non-prose blocks
1. If the body's first non-empty line is an H1 (`# ...`), take that text as the Korean title and strip the line from the body. PaperMod renders the title separately — don't repeat it. The title is the author's; it does **not** go through the polish pass.
2. `mkdir -p _workspace/post-<slug>` and write the remaining body to `_workspace/post-<slug>/01_ko.md`.
3. Mask everything that isn't prose:

   ```bash
   python3 .claude/skills/post/scripts/mask_blocks.py mask \
     _workspace/post-<slug>/01_ko.md \
     _workspace/post-<slug>/02_ko_masked.md \
     _workspace/post-<slug>/blocks_ko.json
   ```

   The script replaces each fenced code block and each top-level raw HTML block (`<style>`, `<figure class="dgm">`, `<svg>`, `<table>`, …) with a single `⟦KEEP-nn⟧` line. Posts on this blog are mostly hand-laid-out inline SVG diagrams; a rewrite pass that touches an SVG label breaks the layout, and one that drops a `<figure>` silently deletes a diagram. Masking makes both impossible.

If the draft has no code or HTML blocks, masking is a no-op — run it anyway, so the rest of the pipeline is uniform.

### 5. Polish the Korean (`humanize-korean`)
Invoke the `humanize-korean:humanize-korean` skill on the **masked** file:

- Input: the absolute path to `_workspace/post-<slug>/02_ko_masked.md`
- Genre: `블로그`
- Extra instruction to pass along: *"⟦KEEP-nn⟧ 줄은 자리표시자다. 한 줄 그대로, 원래 순서대로 남긴다. 마크다운 헤딩 레벨·목록·링크·인라인 코드는 구조를 그대로 유지한다. 고유명사·명령어·수치는 원형 보존."*

(`humanize-korean:humanize` — the `/humanize` command — is user-invocable only; call the `humanize-korean:humanize-korean` orchestrator skill instead.)

It writes `_workspace/<run_id>/final.md`. Then:

1. **Strip the summary block.** `final.md` ends with an `<!-- HUMANIZE-SUMMARY ... -->` HTML comment holding its metrics. It must not reach the post:

   ```bash
   awk '/<!-- HUMANIZE-SUMMARY/{exit} {print}' _workspace/<run_id>/final.md \
     > _workspace/post-<slug>/03_ko_polished_masked.md
   ```

   Read the summary block first, though — its change rate and grade go in the report (step 12).

2. **Unmask:**

   ```bash
   python3 .claude/skills/post/scripts/mask_blocks.py unmask \
     _workspace/post-<slug>/03_ko_polished_masked.md \
     _workspace/post-<slug>/blocks_ko.json \
     _workspace/post-<slug>/04_ko_body.md
   ```

   Exit code 3 means a placeholder was dropped, duplicated or reordered — the polish pass mangled the structure. Do not publish that output: re-run step 5, or fall back to `01_ko.md` and tell the user the Korean polish was skipped.

3. **Sanity-check the result** against `01_ko.md`: same heading count and heading levels, same number of markdown links, and every number, command name, proper noun and quoted term still present. The polish pass may change wording and rhythm only. If a fact, figure or claim moved, restore that sentence from the draft.

4. **Drop the em dashes** in `03_ko_polished_masked.md` and in the Korean strings inside `blocks_ko.json` — see [House style: no em dashes](#house-style-no-em-dashes). Do this before step 8, so the English is translated from already-dashless Korean and the two versions stay parallel. Then re-run the unmask above so `04_ko_body.md` picks up the change.

`04_ko_body.md` is the Korean body from here on.

### 6. Derive Korean front matter
Derive these from the **polished** body:

- `title`: the H1 text taken in step 4, verbatim. If there was no H1, infer a concise Korean title.
- `summary`: one Korean sentence that would appear on the post listing card.
- `tags`: 2–5 short Korean tags (e.g. `["블로그", "시작"]`). Tech/tool keywords (framework names like `hugo`, `papermod`, `react`) stay lowercase English and can repeat across both files.
- `categories`: 1–2 Korean categories. Mirror existing conventions where they apply (`메타`, `개발`, `블로그` — see existing posts).
- `date`: the actual current time in KST, formatted `YYYY-MM-DDTHH:MM:SS+09:00`. Get it by running `TZ=Asia/Seoul date '+%Y-%m-%dT%H:%M:%S+09:00'` — do **not** hardcode a time. Using the real run time keeps multiple posts published on the same day sorted in publication order (Hugo sorts by `date`, and identical timestamps make the order ambiguous).
- `translationKey`: same value as `slug`.
- `draft`: `false`.

### 7. Write the Korean file
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

<contents of 04_ko_body.md>
```

Double-quote string values. Match the format used by `content/posts/blog-start.md` and `content/posts/hugo-papermod-pitfalls.md`.

### 8. Translate the prose to English
Translate `03_ko_polished_masked.md` — the polished, still-masked prose — following this persona prompt:

> You are a professional native English translator and copywriter. Translate the following Korean text into natural, fluent English.
>
> [Translation Rules]
> 1. Do not translate literally (word-for-word). Adapt the phrasing so it sounds completely natural to a native English speaker.
> 2. Match the tone and style of the original text (e.g., formal for business, casual for conversation).
> 3. Accurately convey subtle nuances and idioms rather than just the literal meaning.
> 4. Keep specialized terminology, proper nouns, or technical words accurate to standard English usage.
> 5. Output ONLY the translated English text without any additional explanations or notes.

Rule 5 means the translation carries no commentary or translator's notes — markdown structure still comes through unchanged. On top of the persona rules, this blog's constraints:

- Preserve heading levels exactly, along with list bullets, blockquotes, tables, inline code spans, and every `⟦KEEP-nn⟧` line.
- Code identifiers, config keys, file paths, command names and URLs stay as they are.
- **Internal links get an `/en` prefix.** `[제목](/posts/some-slug/)` becomes `[English Title](/en/posts/some-slug/)`, and the link text becomes that post's actual English `title` — read it out of `content/posts/<that-slug>.en.md` rather than translating the Korean title fresh.

Write the result to `_workspace/post-<slug>/05_en_masked.md`.

### 9. Translate the diagram and code strings
The masked blocks still hold Korean: SVG labels, figure captions, `aria-label` descriptions, comments in code blocks. Pull just those strings out:

```bash
python3 .claude/skills/post/scripts/block_labels.py extract \
  _workspace/post-<slug>/blocks_ko.json \
  _workspace/post-<slug>/labels_ko.json
```

Fill in the `en` field of every entry in `labels_ko.json` and save it as `labels_en.json`. Translation rules for these:

- **Keep them short.** SVG coordinates are hand-placed; a label that grows much wider than the Korean overflows its box. Korean glyphs are two columns wide, so a Korean label usually has room for roughly twice its character count in English.
- **`aria-label` is the diagram's whole description for a screen reader.** Translate it as a full sentence. Leaving it in Korean ships an English page whose alt text isn't English.
- Leave record types, flags, commands, domain names, IPs and numbers alone.
- No em dashes, same as the prose. `humanizer` never sees these strings — they're masked — so nothing else will catch one.
- A caption split across `<strong>` tags arrives as several fragments in span order. Translate them so the reassembled sentence reads correctly, keeping the emphasis on the same idea.

Then splice them back and prove nothing else moved:

```bash
python3 .claude/skills/post/scripts/block_labels.py apply \
  _workspace/post-<slug>/blocks_ko.json \
  _workspace/post-<slug>/labels_en.json \
  _workspace/post-<slug>/blocks_en.json

python3 .claude/skills/post/scripts/block_labels.py verify \
  _workspace/post-<slug>/blocks_ko.json \
  _workspace/post-<slug>/blocks_en.json \
  _workspace/post-<slug>/labels_en.json
```

`apply` re-pads trailing `#` and `←` comments so they land in the same display column as the Korean. `verify` compares the markup skeleton on both sides and fails if a single attribute or coordinate differs. If it fails, fix the labels — never hand-edit `blocks_en.json`.

### 10. Polish the English (`humanizer`)
Invoke the `humanizer:humanizer` skill on `05_en_masked.md` in embedded mode — it returns the final text only, no commentary.

- The voice to hold: direct, technical, peer-to-peer. No padding phrases ("In this post, we will explore…"). Active voice. Korean polite endings (`~합니다`, `~입니다`) read as natural English, not stiff formality. Past tense for what the author did, present for what the code does.
- Leave `⟦KEEP-nn⟧` lines exactly as they are.
- Keep every claim. This pass rewrites how a sentence reads, never what it asserts, and never invents a fact the Korean post doesn't have.
- **Don't restructure.** Both language versions render from the same diagram set and the same outline, so the English keeps the Korean's heading levels, list items and paragraph breaks even when a humanizer rule would prefer to merge or flatten them.
- Its §14 bans em dashes, which matches the house rule. The Korean was already swept in step 5, so this pass should have little to remove; whatever it does catch, it catches for free.

Save the result to `_workspace/post-<slug>/06_en_polished_masked.md`, then unmask it with the **translated** blocks:

```bash
python3 .claude/skills/post/scripts/mask_blocks.py unmask \
  _workspace/post-<slug>/06_en_polished_masked.md \
  _workspace/post-<slug>/blocks_en.json \
  _workspace/post-<slug>/07_en_body.md
```

Exit code 3: same rule as step 5 — don't publish it.

### 11. Check parity, derive English front matter, write the file
Compare `07_en_body.md` against `04_ko_body.md`. These must match exactly: heading count, link count, `<figure>`, `<svg>`, `<text>` and `aria-label` counts. And the English body must contain **zero Hangul** — any remaining is a string the translation missed. Check the opening and closing tags balance while you're there.

Both finished files must also contain **zero em or en dashes**, front matter included:

```bash
grep -c '—\|–' content/posts/<slug>.md content/posts/<slug>.en.md   # both must print 0
```

Front matter:

- `title`: translation of the Korean title, run through the same persona rules.
- `summary`: translation of the Korean summary.
- `tags`: English equivalents. Tech-keyword tags (`hugo`, `papermod`, `i18n`, etc.) stay the same across both files. Korean-only concept tags get translated (e.g. `시작` → `intro`).
- `categories`: English equivalents. Mirror existing conventions: `메타` ↔ `Meta`, `개발` ↔ `Engineering`, `블로그` ↔ `Blog`.
- `date`, `slug`, `translationKey`, `draft`: same as the Korean file.

Write `content/posts/<slug>.en.md` with this front matter and the contents of `07_en_body.md`.

### 12. Report
Print:
- The two file paths created
- The slug
- The Korean and English titles
- One line per polish pass: which one ran, its change rate and grade (Korean, from the `HUMANIZE-SUMMARY` block) and a one-line note on what it changed (English). Say explicitly if either pass was skipped or fell back.
- The parity check from step 11, and the count of diagram strings translated.
- The suggested commit command, for the user to run if they want:
  ```bash
  git add content/posts/<slug>.md content/posts/<slug>.en.md
  git commit -m "post: <short description>"
  ```

**Do not** run `git add`, `git commit`, or `git push` yourself. The user reviews the diff and commits.

## If a polish skill isn't installed

Check the available skills before invoking. If `humanize-korean:humanize-korean` or `humanizer:humanizer` isn't there, don't fake the pass and don't stop: run the rest of the pipeline, and say in the report which pass was skipped and why.

## House style: no em dashes

Neither language uses `—` or `–`. This covers prose, headings, diagram labels, figure captions, `aria-label` text and the front matter `summary`.

Replacing one takes judgment, so no script does it. What generally works:

| Where | Korean | English |
|---|---|---|
| Heading appositive (`## 존 — 네임서버가 책임지는 구역`) | `:` | `:` |
| Inline gloss after a term | `,` | `,` |
| Introducing an example or restatement | `.` or `:` | `.` or `:` |
| Parenthetical with a particle attached (`상태 — … — 를`) | rewrite (`상태, 그러니까 …를`) | `,` … `,` or parentheses |
| Trailing punchline (`뺄셈이 곧 나이다 — **…사본**이다.`) | `.` | `.` or `:` |

Two things make this its own step rather than something a polish pass handles:

- **`humanize-korean` protects them.** Its monolith agent treats an explanatory dash as a sign of live human writing and preserves it on purpose, so asking it to strip dashes fights its own rules. Sweep the Korean yourself, after that pass.
- **`humanizer` §14 covers English prose but not the diagram strings**, which are masked while it runs. Handle those in step 9.

For the Korean strings inside `blocks_ko.json`, use `block_labels.py` — its `en` field is just "the replacement string," so fill it with the dashless Korean and write the result back over `blocks_ko.json`:

```bash
python3 .claude/skills/post/scripts/block_labels.py extract \
  _workspace/post-<slug>/blocks_ko.json _workspace/post-<slug>/labels_ko.json
# fill `en` with the dashless Korean for the affected entries, then:
python3 .claude/skills/post/scripts/block_labels.py apply \
  _workspace/post-<slug>/blocks_ko.json _workspace/post-<slug>/labels_ko.json \
  _workspace/post-<slug>/blocks_ko.json
```

Re-run `extract` afterwards so `labels_ko.json` matches the updated blocks before step 9.

## Front matter reference (from existing posts)

- All string values use double quotes.
- `date` is local +09:00 (KST); use the actual current run time (see step 6), not a fixed time.
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
- Never auto-commit or push, and never commit `_workspace/`.
- Do not invent the date/time. Get the real current KST timestamp at run time via `TZ=Asia/Seoul date '+%Y-%m-%dT%H:%M:%S+09:00'`.
- A polish pass may change wording, rhythm and sentence structure. It may not change a fact, a number, a command, a heading level, a link target, or anything inside a code or SVG block. When in doubt, keep the draft's version.
- Never publish output from a failed unmask (exit 3), or from a failed `block_labels.py verify`.
- Never hand-edit `blocks_*.json`. Fix the labels and re-run `apply`.
- Never retype SVG markup to translate a label. The markup is copied, not regenerated.
- No em or en dashes in either finished file. See House style.
