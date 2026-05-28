---
title: "Setting Up a Bilingual Blog with Hugo + PaperMod: Pitfalls I Hit"
date: 2026-05-28T17:00:00+09:00
draft: false
slug: "hugo-papermod-pitfalls"
translationKey: "hugo-papermod-pitfalls"
categories: ["Engineering", "Blog"]
tags: ["hugo", "papermod", "github-pages", "i18n", "giscus"]
summary: "Six gotchas I hit while migrating from Jekyll to Hugo + PaperMod for a bilingual (ko/en) blog, and how I fixed each one."
---

This blog started on Jekyll + Chirpy. Maintaining the Korean/English split kept eating my time, so I rewrote it on Hugo + PaperMod where i18n is a first-class feature.

Hugo *is* cleaner — once you learn which footguns aren't documented loudly enough. This post walks through six issues I actually hit and what fixed each one, so the next person doesn't have to find them all from scratch.

> Stack: Hugo 0.150.0 (extended) + PaperMod (latest as of May 2026, vendored as a git submodule) + GitHub Pages

---

## 1. Missed PaperMod's minimum Hugo version → build broke

My first GitHub Actions workflow pinned Hugo 0.142.0. The very first push spat out a wall of errors:

```text
ERROR => hugo v0.146.0 or greater is required for hugo-PaperMod to build
WARN  found no layout file for "html" for kind "section"
ERROR render of "/" failed: ... partial "head.html" not found
```

The first line is the only one that matters. PaperMod now requires Hugo 0.146+ (its `layouts/_partials/` structure dates from that release). With an older Hugo, the layout lookup itself collapses and every downstream warning follows.

```yaml
# .github/workflows/hugo-deploy.yml
env:
  HUGO_VERSION: 0.150.0   # anything below 0.146 will not build PaperMod
```

**Takeaway**: read the theme's `theme.toml` or README for "Minimum Hugo Version" *before* writing the workflow.

---

## 2. Multilingual content directory layout — the biggest trap

My instinctive structure was:

```text
content/
  posts/blog-start.md        # Korean
  en/posts/blog-start.md     # English
```

With matching config:

```toml
[languages.en]
  contentDir = "content/en"
```

Result: the Korean home (`/`) showed the English post card and linked to the English URL. Meanwhile `/posts/` (the Korean listing page) looked fine, which made the bug harder to spot.

Root cause: **`content/en/` is a child of `content/`**, so when Hugo scans `content/` for the Korean build it also picks up the English files.

The cleanest fix is the **filename-suffix convention** Hugo supports natively:

```text
content/
  posts/
    blog-start.md       # Korean (default language, no suffix)
    blog-start.en.md    # English (.en.md auto-detected)
```

Drop `contentDir = "content/en"` from `hugo.toml`. Hugo recognizes `<base>.<lang>.md` and splits the languages on its own. Pairing happens automatically when the base name matches.

> If you prefer folders, separate **both** languages explicitly: `content/ko/` + `content/en/`. The conflict only happens when one language's directory is a parent of the other.

---

## 3. `homeInfoParams` showing the same value in both languages

The greeting at the top of PaperMod's home page. I put it under the global `[params]` block first:

```toml
[params]
  [params.homeInfoParams]
    Title = "👋 Hello"
    Content = "chan-na's tech blog."
```

Both languages picked up the same English greeting. On a multilingual site, anything user-facing has to live under the per-language `params`:

```toml
[languages.ko.params]
  [languages.ko.params.homeInfoParams]
    Title = "👋 안녕하세요"
    Content = "chan-na의 개발 블로그입니다."

[languages.en.params]
  [languages.en.params.homeInfoParams]
    Title = "👋 Hello"
    Content = "chan-na's tech blog."
```

Same applies to `keywords`, `description`, and so on.

---

## 4. Syncing Giscus with dark mode — I fixed this three times

I wanted the Giscus comments widget to follow PaperMod's light/dark toggle, so I added a small sync script in `layouts/_partials/comments.html`. It needed three separate fixes before it actually worked.

### 4-1. Wrong selector: not `body.dark`, but `<html data-theme>`

My first attempt used the common pattern:

```js
document.body.classList.contains('dark')  // ❌ PaperMod does not do this
```

Reading PaperMod's `footer.html` shows what the toggle actually does:

```js
document.querySelector("html").dataset.theme = 'dark';
```

So I should be watching the `data-theme` attribute on `<html>`:

```js
const root = document.documentElement;
new MutationObserver(sync).observe(root, {
  attributes: true,
  attributeFilter: ['data-theme'],
});
```

### 4-2. Missed the `data-theme="auto"` case

With PaperMod's `defaultTheme = "auto"`, a visitor who hasn't pressed the toggle keeps `<html data-theme="auto">`. Checking only `=== 'dark'` leaves the comments in the light theme for OS-dark visitors.

The fix is to fall back to the `prefers-color-scheme` media query:

```js
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
const isDark = () => {
  const t = root.dataset.theme;
  if (t === 'dark') return true;
  if (t === 'light') return false;
  return prefersDark.matches;  // 'auto' follows OS
};
prefersDark.addEventListener('change', sync);  // and react to OS changes
```

### 4-3. `jsonify` wrapped the theme name in literal quotes

This one was the hardest to diagnose. The browser console kept saying:

```text
Refused to apply style from 'https://giscus.app/en/%22noborder_dark%22'
because its MIME type ('text/html') is not a supported stylesheet MIME type
```

`%22` is `"`. The value Giscus received wasn't `noborder_dark` but **`"noborder_dark"`** — quotes baked into the string. Giscus put that into a CSS URL, got a 404, and silently kept the light theme.

The culprit was `| jsonify` in the Hugo template:

```html
<!-- ❌ jsonify already wraps strings in JSON quotes -->
const LIGHT = {{ default "light" .lightTheme | jsonify }};
```

`jsonify` rendered `noborder_light` as `"noborder_light"` (with quotes). That landed inside the JS variable so the *value* contained the quotes. Plain interpolation works fine:

```html
<!-- ✅ explicit single-quoted JS literal, no jsonify -->
const LIGHT = '{{ default "light" .lightTheme }}';
```

**Takeaway**: when a template-driven bug surfaces somewhere unexpected ("Refused to apply style..."), inspect the *raw rendered HTML/JS string* directly. Don't guess what the variable holds.

---

## 5. Header language switch always jumped to the other language's home

On a Korean post page, clicking the top-right `En` button should go to the English version of the same post. Instead it always went to the English **home**.

The reason is plain in `_partials/header.html`:

```go-template
{{- with site.Home.Translations }}
  ...
  <a href="{{- .Permalink -}}">{{- .Lang | title -}}</a>
{{- end }}
```

`site.Home.Translations` — always the home's translations, regardless of the current page. (PaperMod's `translation_list.html` partial that shows up above the post body uses per-page translations and works correctly; the header is separate logic.)

Override `layouts/_partials/header.html` and change one block:

```go-template
{{- /* Prefer this page's translations; fall back to home translations. */}}
{{- $alts := .Translations }}
{{- if not $alts }}{{ $alts = site.Home.Translations }}{{ end }}
{{- with $alts }}
  ...
```

Now `En` on a Korean post goes to the English post, `Ko` on an English post goes to the Korean post, and the home pages still fall back to each other's home.

---

## 6. Adding a menu entry for a page that doesn't exist → 404

I enthusiastically added four menu items in `hugo.toml`: Posts, Categories, Tags, Archives.

```toml
[[languages.ko.menu.main]]
  identifier = "archives"
  name = "Archives"
  url = "/archives/"
```

But PaperMod only ships the **layout** for Archives — you still need a content page (`content/archives.md`) to make the route exist. Without it, the menu link 404s.

Two ways out:
1. Create `content/archives.md` (and `.en.md`) with `layout: "archives"` in the front matter.
2. Remove the menu entry until you actually need it.

Early on with only a handful of posts, option 2 is the saner default. Bring it back when post volume warrants archive navigation.

---

## Wrap-up

The headline is still true: **Hugo's i18n is solid**. Just watch for three things:

- Don't let one language's content directory be a parent of another's (#2).
- Move every user-facing parameter under `[languages.<lang>.params]` on a multilingual site (#3).
- Some theme partials don't do what you'd hope (e.g., the header language switch in #5) and need overriding.

For external integrations (like Giscus), test **all three modes**: site-toggled light, site-toggled dark, and untouched (OS-driven). Issue 4-2 only surfaced in the third case.

Hope this saves the next person five minutes of head-scratching.
