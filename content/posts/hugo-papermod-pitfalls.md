---
title: "Hugo + PaperMod로 다국어 블로그 만들기: 만난 함정들"
date: 2026-05-28T17:00:00+09:00
draft: false
slug: "hugo-papermod-pitfalls"
translationKey: "hugo-papermod-pitfalls"
categories: ["개발", "블로그"]
tags: ["hugo", "papermod", "github-pages", "i18n", "giscus"]
summary: "Jekyll에서 Hugo + PaperMod로 갈아엎으며 다국어 블로그를 세팅하는 동안 부딪힌 6가지 함정과 해결법."
---

이 블로그는 처음에 Jekyll + Chirpy로 시작했다가 **다국어(한/영) 운용**이 자꾸 손이 가서 Hugo + PaperMod로 갈아엎었다.
Hugo는 i18n이 1급 기능이라 훨씬 깔끔할 줄 알았지만, 막상 세팅하면서 *대놓고 적혀있지 않은 함정*들에 여러 번 막혔다. 같은 길을 가는 사람이 두 번 막히지 않도록 정리한다.

> 환경: Hugo 0.150.0 (extended) + PaperMod (서브모듈, 2026-05 기준 최신) + GitHub Pages

---

## 1. PaperMod의 최소 Hugo 버전을 놓치고 빌드 실패

GitHub Actions에 Hugo 0.142.0을 박고 첫 푸시를 했더니 곧바로:

```text
ERROR => hugo v0.146.0 or greater is required for hugo-PaperMod to build
WARN  found no layout file for "html" for kind "section"
ERROR render of "/" failed: ... partial "head.html" not found
```

수많은 WARN/ERROR가 함께 쏟아져서 일단 모양은 처참했지만, 진짜 원인은 **딱 첫 줄**이다. PaperMod는 이미 Hugo 0.146 이상을 요구하는데 (`layouts/_partials/` 구조가 그 버전부터다) 워크플로의 `HUGO_VERSION`이 너무 낮으면 layout lookup이 모두 깨진다.

```yaml
# .github/workflows/hugo-deploy.yml
env:
  HUGO_VERSION: 0.150.0   # 0.146 미만이면 PaperMod 빌드 자체가 실패
```

**교훈**: 테마의 `theme.toml` 또는 README의 "Minimum Hugo Version"을 가장 먼저 확인할 것.

---

## 2. 다국어 콘텐츠 폴더 구조 — 가장 큰 함정

처음엔 직관적으로 이렇게 잡았다:

```text
content/
  posts/blog-start.md        # 한국어
  en/posts/blog-start.md     # 영어
```

`hugo.toml`도 그에 맞춰서:

```toml
[languages.en]
  contentDir = "content/en"
```

결과: 한국어 홈(`/`)에 영어 글이 카드로 떠 있고, 클릭하면 영어 페이지로 이동. 한국어 글 목록 페이지(`/posts/`)는 또 정상이라 더 헷갈렸다.

원인: **`content/en/` 가 `content/` 의 하위 폴더**라, 한국어 빌드 시 Hugo가 `content/` 를 재귀 스캔하며 영어 글까지 한국어 글로 잡아버렸다.

해결책은 두 가지인데, Hugo가 1급으로 지원하는 **파일명 접미사 방식**이 가장 깔끔하다.

```text
content/
  posts/
    blog-start.md       # 한국어 (기본 언어, 접미사 없음)
    blog-start.en.md    # 영어 (.en.md 자동 인식)
```

`hugo.toml`에서 `contentDir = "content/en"`은 제거. Hugo가 `<base>.<lang>.md` 패턴을 알아서 분리한다. 페어링도 같은 베이스 이름이면 자동.

> 폴더로 나누고 싶다면 `content/ko/` + `content/en/` 처럼 **둘 다 명시적**으로 분리해야 한다. `content/` 와 `content/en/` 처럼 한쪽이 다른 쪽의 부모가 되면 충돌한다.

---

## 3. `homeInfoParams` 가 두 언어 모두에서 동일하게 표시

PaperMod 홈 상단의 인사말. 처음엔 전역 `[params]` 아래에 넣었다.

```toml
[params]
  [params.homeInfoParams]
    Title = "👋 안녕하세요"
    Content = "chan-na의 개발 블로그입니다."
```

당연히 영어 페이지에서도 "👋 안녕하세요"가 떴다. 다국어 사이트에서는 **각 언어의 `params` 아래로 내려야 한다.**

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

같은 원리로 `keywords`, `description` 등도 언어별로 분리하는 게 자연스럽다.

---

## 4. Giscus 다크모드 동기화 — 세 번 고쳤다

PaperMod의 라이트/다크 토글에 맞춰 Giscus 댓글 위젯의 테마도 함께 바뀌도록 하려고 `layouts/_partials/comments.html`에 동기화 JS를 넣었다. 그런데 한 번에 안 됐다. **세 번 연속으로 고쳐야 다 잡혔다.**

### 4-1. 잘못된 셀렉터: `body.dark` 가 아니라 `<html data-theme>`

처음엔 흔히 보는 패턴대로 작성했다.

```js
document.body.classList.contains('dark')  // ❌ PaperMod는 이렇게 안 함
```

PaperMod의 footer.html을 까보니 토글이 이렇게 동작한다.

```js
document.querySelector("html").dataset.theme = 'dark';
```

따라서 감시 대상은 `<html>` 의 `data-theme` 속성이다.

```js
const root = document.documentElement;
new MutationObserver(sync).observe(root, {
  attributes: true,
  attributeFilter: ['data-theme'],
});
```

### 4-2. `data-theme="auto"` 케이스를 빼먹음

PaperMod의 `defaultTheme = "auto"` 모드에서는 사용자가 토글을 안 누른 상태일 때 `<html data-theme="auto">` 가 그대로 유지된다. 즉 `=== 'dark'` 만 체크하면 OS 다크모드인 방문자에게 댓글만 라이트로 남는다.

`prefers-color-scheme` 미디어쿼리를 fallback으로 묶어줘야 한다.

```js
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
const isDark = () => {
  const t = root.dataset.theme;
  if (t === 'dark') return true;
  if (t === 'light') return false;
  return prefersDark.matches;  // 'auto' 일 때 OS 따라감
};
prefersDark.addEventListener('change', sync);  // OS 설정 변화에도 반응
```

### 4-3. `jsonify` 때문에 테마 이름에 따옴표가 두 겹

이게 가장 디버깅하기 어려웠다. 브라우저 콘솔에 이런 에러가 떴다.

```text
Refused to apply style from 'https://giscus.app/en/%22noborder_dark%22'
because its MIME type ('text/html') is not a supported stylesheet MIME type
```

`%22`는 `"`. 즉 Giscus가 받은 테마 값이 `noborder_dark` 가 아니라 **`"noborder_dark"`** (양 끝에 따옴표 포함된 문자열). Giscus는 그걸 그대로 URL pathname으로 써서 404를 받고 스타일을 못 입혔다.

원인: Hugo 템플릿에서 `| jsonify` 를 썼다.

```html
<!-- ❌ jsonify는 이미 따옴표를 포함한 JSON 문자열을 출력 -->
const LIGHT = {{ default "light" .lightTheme | jsonify }};
```

`jsonify`는 `noborder_light` 를 `"noborder_light"` (따옴표 포함)로 출력. 그게 JS 변수에 그대로 들어가서 값에 따옴표가 박혀버린 것. 단순 보간으로 충분하다.

```html
<!-- ✅ 명시적 단일 따옴표 안에서 보간 -->
const LIGHT = '{{ default "light" .lightTheme }}';
```

**교훈**: 템플릿 결과가 `Refused to apply style` 처럼 의외의 곳에서 나오면 *항상 직접 렌더된 HTML/JS의 raw 문자열*을 보자. 변수에 뭐가 들어갔는지 추측하지 말고.

---

## 5. 헤더 언어 토글이 항상 "다른 언어 홈"으로 이동

한국어 글 페이지에서 우상단 `En` 버튼을 누르면, 기대는 같은 글의 영어 버전이지만 실제로는 영어 **홈**으로만 갔다.

PaperMod의 `_partials/header.html` 을 보면 이유가 명확하다.

```go-template
{{- with site.Home.Translations }}
  ...
  <a href="{{- .Permalink -}}">{{- .Lang | title -}}</a>
{{- end }}
```

`site.Home.Translations` — 늘 홈의 번역 목록을 쓰니까 현재 페이지가 뭐든 다른 언어의 홈으로만 간다. 본문 위쪽에 PaperMod가 자동으로 띄워주는 `translation_list.html` 은 글 단위로 정상 작동하지만, 헤더는 별도 로직이다.

`layouts/_partials/header.html` 로 override해서 한 줄 바꿔주면 된다.

```go-template
{{- /* 현재 페이지의 번역을 우선 사용, 없으면 홈 번역으로 fallback */}}
{{- $alts := .Translations }}
{{- if not $alts }}{{ $alts = site.Home.Translations }}{{ end }}
{{- with $alts }}
  ...
```

이제 한국어 글에서 `En`을 누르면 같은 글의 영어 버전으로, 영어 글에서 `Ko`를 누르면 한국어 버전으로 이동한다. 홈 같은 비-글 페이지에선 fallback이 발동해서 다른 언어 홈으로 간다.

---

## 6. 존재하지 않는 페이지를 메뉴에 박아두면 404

`hugo.toml`에서 의욕적으로 메뉴를 4개 추가했다 — Posts, Categories, Tags, Archives.

```toml
[[languages.ko.menu.main]]
  identifier = "archives"
  name = "아카이브"
  url = "/archives/"
```

그런데 Archives는 PaperMod가 layout만 제공할 뿐 **콘텐츠 페이지(`content/archives.md`)는 직접 만들어야** 한다. 안 만들면 메뉴 클릭 시 404.

선택지는 둘이다:
1. `content/archives.md`(+ `.en.md`)에 `layout: "archives"` front matter로 페이지 만들기
2. 메뉴에서 항목 제거

글이 몇 개 안 되는 초기 단계라면 2번이 깔끔하다. 글이 쌓이면 1번으로 살리면 된다.

---

## 마치며

큰 흐름은 "**Hugo는 i18n 잘 되어 있다**" 가 맞다. 단지 다음 셋만 조심하면 된다.

- 폴더 구조에서 한 언어가 다른 언어의 *부모*가 되면 안 된다 (2번)
- 다국어 사이트의 모든 사용자 노출 파라미터는 `[languages.<lang>.params]` 아래로 (3번)
- 테마가 제공하는 partial이 알아서 처리하지 못하는 부분이 있다 (헤더 토글: 5번)

그리고 외부 통합(Giscus처럼)은 **세 가지 모드**를 다 시험해보자: 사이트 토글로 라이트, 토글로 다크, 그리고 토글 안 누른 상태에서 OS 다크. 4-2가 그 셋째에서만 터졌다.

같은 함정에 빠진 사람의 시간이 5분이라도 줄어들었으면 좋겠다.
