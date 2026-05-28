---
title: "Starting the Blog"
date: 2026-05-28T10:00:00+09:00
draft: false
slug: "blog-start"
translationKey: "blog-start"
categories: ["Meta"]
tags: ["blog", "intro"]
summary: "Rebuilt the blog from Jekyll to Hugo. Every post ships in both Korean and English."
---

## First post

The blog is up. Built with **Hugo** and the **PaperMod** theme, deployed to GitHub Pages.
Every post is published in **both Korean and English** as a paired set.

## How posts are written

Create two files with the same name under `content/posts/` and `content/en/posts/`:

```text
content/posts/<slug>.md          # Korean → /posts/<slug>/
content/en/posts/<slug>.md       # English → /en/posts/<slug>/
```

Posts that share a `translationKey` are auto-paired by PaperMod, which renders a link to the
counterpart language at the top of each post.

Front matter for each:

```yaml
---
title: "Post title"
date: 2026-05-28T10:00:00+09:00
draft: false
slug: "my-post"
translationKey: "my-post"   # same in both files
categories: ["Misc"]
tags: ["tag1", "tag2"]
summary: "One-liner shown on the listing page"
---
```

### Markdown sample

- bullet list
- **bold**, *italic*
- [link](https://github.com/chan-na)

```python
def hello():
    print("Hello, blog!")
```

```typescript
function hello(name: string): string {
  return `Hello, ${name}!`;
}
```

> Blockquotes render like this. PaperMod ships a clean default style.

## What's next

Mostly notes on what I'm learning and building. Sometimes everyday thoughts.
