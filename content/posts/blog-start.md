---
title: "블로그를 시작하며"
date: 2026-05-28T10:00:00+09:00
draft: false
slug: "blog-start"
translationKey: "blog-start"
categories: ["메타"]
tags: ["블로그", "시작"]
summary: "Jekyll에서 Hugo로 갈아엎고 다시 시작한 블로그. 모든 글은 한국어/영어 한 쌍으로 발행됩니다."
---

## 첫 글

드디어 블로그를 만들었습니다. **Hugo**와 **PaperMod** 테마를 사용해 GitHub Pages 위에 구축했습니다.
모든 글은 **한국어와 영어 두 버전**으로 발행됩니다.

## 글 작성 방법

`content/posts/` 와 `content/en/posts/` 에 같은 파일명으로 두 파일을 만듭니다.

```text
content/posts/<slug>.md          # 한국어 → /posts/<slug>/
content/en/posts/<slug>.md       # 영어  → /en/posts/<slug>/
```

같은 `translationKey`를 가진 두 글은 PaperMod가 자동으로 페어링해서, 페이지 상단에 다른 언어 버전 링크를 표시합니다.

각 파일의 front matter:

```yaml
---
title: "글 제목"
date: 2026-05-28T10:00:00+09:00
draft: false
slug: "my-post"
translationKey: "my-post"   # 한/영 파일에 동일하게
categories: ["카테고리"]
tags: ["태그1", "태그2"]
summary: "글 목록에 표시될 한 줄 요약"
---
```

### Markdown 예시

- 글머리 기호
- **굵게**, *기울임*
- [링크](https://github.com/chan-na)

```python
def hello():
    print("Hello, blog!")
```

```typescript
function hello(name: string): string {
  return `Hello, ${name}!`;
}
```

> 인용문은 이렇게 표시됩니다. Hugo PaperMod는 깔끔한 blockquote 스타일을 제공합니다.

## 앞으로의 계획

기술 학습 기록을 중심으로, 가끔 일상적인 생각도 담아보려 합니다.
