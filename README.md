# chan-na's Blog

[Hugo](https://gohugo.io/) + [PaperMod](https://github.com/adityatelange/hugo-PaperMod) 테마로 만든 GitHub Pages 블로그.
**모든 글은 한국어와 영어 두 버전으로 한 쌍으로 발행한다.**

- **사이트**: https://chan-na.github.io/Blog/ (한국어) / https://chan-na.github.io/Blog/en/ (English)
- **글쓰기**: `content/posts/` 와 `content/en/posts/` 에 같은 파일명으로 두 파일 추가 → `main` push → GitHub Actions가 자동 빌드/배포

---

## 글쓰기 (한/영 쌍)

### 1. 새 글 한 쌍 만들기

같은 슬러그/파일명을 가진 두 파일을 만든다.

```text
content/posts/<slug>.md          # 한국어 → /posts/<slug>/
content/en/posts/<slug>.md       # English → /en/posts/<slug>/
```

#### 한국어 파일

```markdown
---
title: "글 제목"
date: 2026-05-28T10:00:00+09:00
draft: false
slug: "my-post"
translationKey: "my-post"        # 한/영 파일에 같은 값
categories: ["메타"]
tags: ["블로그"]
summary: "글 목록 카드에 표시될 한 줄 요약"
---

본문...
```

#### 영어 파일

```markdown
---
title: "Post Title"
date: 2026-05-28T10:00:00+09:00
draft: false
slug: "my-post"
translationKey: "my-post"        # same value as the Korean file
categories: ["Meta"]
tags: ["blog"]
summary: "One-liner shown on the listing page"
---

Body...
```

### 2. 자동으로 일어나는 일

- `translationKey`가 같은 두 글은 PaperMod가 자동으로 페어링 → 각 글 상단에 다른 언어 버전 링크 표시
- `/` 한국어 홈, `/en/` 영어 홈에 각 언어 글만 시간순 자동 나열
- 카테고리/태그/아카이브 페이지가 **언어별로 자동 분리** (Hugo i18n 내장 효과)
- 페이지네이션(10개씩) 자동
- RSS 피드 자동 생성 (`/index.xml`, `/en/index.xml`)
- 코드 블록 복사 버튼, 다크/라이트 모드 자동 토글

### 3. 푸시

```bash
git add content/posts/my-post.md content/en/posts/my-post.md
git commit -m "post: my post"
git push
```

`main` 브랜치에 push 되면 [Actions](.github/workflows/hugo-deploy.yml)가 빌드해서 GitHub Pages에 배포한다.

---

## 한 쪽 언어만 먼저 발행하고 싶을 때

그냥 한쪽 파일만 만들고 push 하면 된다. 짝이 없으면 다른 언어 링크가 표시되지 않을 뿐, 빌드는 정상.

---

## 로컬에서 미리보기

Hugo extended 필요.

```bash
# 1회: 설치
brew install hugo

# 글 작성 중 라이브 프리뷰 (드래프트 포함)
hugo server -D

# → http://localhost:1313/Blog/
```

⚠️ 처음 클론할 땐 PaperMod 서브모듈도 같이 가져와야 한다.

```bash
git clone --recurse-submodules git@github.com:chan-na/Blog.git
# 또는 이미 클론한 상태라면:
git submodule update --init --recursive
```

---

## 배포 환경 설정 (1회 작업)

### GitHub Pages 활성화

1. https://github.com/chan-na/Blog/settings/pages 이동
2. **Source** 를 `GitHub Actions` 로 설정
3. `main` 브랜치에 push 하면 자동 배포

### Giscus 댓글 활성화

1. https://github.com/chan-na/Blog/settings 에서 **Discussions** 기능 켜기
2. [giscus.app](https://giscus.app) 에서 repo: `chan-na/Blog` 선택, 카테고리 선택
3. 생성된 `data-repo-id`, `data-category-id` 값을 `hugo.toml` 의 `[params.giscus]` 섹션에 채워넣기

   ```toml
   [params.giscus]
     repo = "chan-na/Blog"
     repoID = "R_kgDO..."          # giscus.app에서 받은 값
     category = "General"
     categoryID = "DIC_kwDO..."    # giscus.app에서 받은 값
   ```

> 한/영 쌍의 두 글은 URL이 다르므로 댓글 스레드도 각각 별도로 생성된다.

---

## 디렉터리 구조

```
.
├── hugo.toml                     # 사이트 설정 (i18n, 메뉴, 테마 옵션)
├── content/
│   ├── posts/                    # 한국어 글
│   │   └── blog-start.md
│   └── en/posts/                 # 영어 글 (같은 파일명)
│       └── blog-start.md
├── layouts/
│   └── partials/
│       └── comments.html         # Giscus 통합
├── archetypes/
│   └── default.md                # `hugo new posts/foo.md` 템플릿
├── themes/PaperMod/              # 테마 (git submodule)
├── .github/workflows/hugo-deploy.yml
└── .gitignore
```

---

## 유용한 Hugo 명령어

```bash
# 새 글 한국어 버전 (한 쌍이니까 영어 버전도 만들어야 함)
hugo new posts/my-new-post.md

# 영어 버전
hugo new --kind default posts/my-new-post.md --content-dir content/en

# 로컬 빌드 (public/ 에 결과)
hugo --gc --minify

# 드래프트 포함 서버
hugo server -D
```
