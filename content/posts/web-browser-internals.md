---
title: "Web Browser 기술에 대한 개괄 - JavaScript 관점"
date: 2026-05-30T11:00:00+09:00
draft: false
slug: "web-browser-internals"
translationKey: "web-browser-internals"
categories: ["개발"]
tags: ["browser", "javascript", "v8", "webassembly", "bundler"]
summary: "브라우저 엔진부터 V8 티어링, ECMAScript, 모듈 시스템, 번들러, Node.js까지 — JavaScript 관점에서 웹 브라우저 기술을 한 번에 정리."
---

## Web Browser의 역사

- 웹 초창기에도 표준은 존재했음
    - HTML/CSS는 W3C, JavaScript는 ECMA International (ECMAScript)에서 표준화
- 문제는 표준 부재가 아니라 브라우저 간 구현 불일치였음
    - Internet Explorer vs Netscape Navigator 시절은 호환성 문제가 심각했음
- 이후 Blink(2013년 Google이 WebKit에서 fork한 별도 엔진) 기반의 Chromium 계열 브라우저가 확산되고 WHATWG 중심의 표준 협업이 강화되면서 표준 준수 수준이 크게 향상됨
    - Blink와 WebKit은 현재 독립적으로 발전하고 있으며, WebKit을 그대로 쓰는 주요 브라우저는 Safari 정도임
    - Chromium은 웹 플랫폼 발전에 큰 영향을 주며 사실상 구현 레퍼런스처럼 작용하는 경우가 많음
- Chromium에서 사용하는 V8의 JIT 최적화와 함께 브라우저 엔진 전반의 아키텍처 개선이 이루어지면서 이전 세대 브라우저 대비 전반적인 성능이 크게 향상되었다.
    - JIT 발전, 멀티프로세스 아키텍처, GPU 가속 등

### 참고: W3C vs WHATWG

- HTML과 CSS의 표준을 담당하는 두 단체
    - W3C (**W**orld **W**ide **W**eb **C**onsortium)
        - 초창기 표준화 단체
    - WHATWG (**W**eb **H**ypertext **A**pplication **T**echnology **W**orking **G**roup)
        - 브라우저 개발사 주도, 2004년 등장

| 항목 | WHATWG | W3C |
| --- | --- | --- |
| 기본 철학 | 실제 브라우저 동작 기준 (현실 중심) | 이상적인 표준 정의 (명세 중심) |
| 표준 방식 | **Living Standard** (계속 업데이트) | **Snapshot/버전 방식** (HTML5 등) |
| 업데이트 속도 | 빠름 (즉시 반영) | 느림 (합의 과정 필요) |
| 유연성 | 높음 | 낮음 (안정성 우선) |
| 주요 참여자 | 브라우저 벤더 중심 (Apple, Mozilla 등) | 다양한 기업/기관 (폭넓은 참여) |
| HTML 표준 영향력 | ⭐ 현재 사실상 표준 | 과거 중심, 현재는 보조적 |
| CSS/기타 표준 | 일부만 관여 | ⭐ 여전히 핵심 역할 |
| 실무 기준 | 최신 브라우저 기준 개발 | 공식 문서/권고안 참고 |

### 참고: Blink vs WebKit (vs Gecko)

- WebKit = 렌더링 엔진 (HTML/CSS) + JS 엔진(JavaScriptCore)
    - WebCore(렌더링) + JavaScriptCore(JS 엔진)
    - iOS는 Apple 정책상 모든 브라우저가 WebKit 사용하도록 되어있으므로, iOS Chrome도 내부적으로 WebKit 사용함
        - 2024년 이후 EU의 DMA(Digital Markets Act) 시행으로 EU 지역에서는 대체 엔진 허용
- Blink = WebKit의 WebCore(렌더링 부분)에서 fork
    - JS엔진은 V8 사용
- Gecko = Mozilla Firefox에서 사용하는 별도 엔진

| 구분 | Blink | WebKit | Gecko |
| --- | --- | --- | --- |
| **개발 주체** | Google (Chromium 프로젝트) | Apple | Mozilla Foundation |
| **출시/시작** | 2013년 (WebKit의 WebCore에서 fork) | 2001년 (KHTML에서 포크) | 1998년 (Netscape 오픈소스화) |
| **기원** | WebKit에서 분기 | KHTML/KJS에서 분기 | Netscape NGLayout |
| **라이선스** | BSD, LGPL | LGPL (WebCore), BSD (JavaScriptCore) | MPL 2.0 |
| **JavaScript 엔진** | V8 | JavaScriptCore (Nitro/SquirrelFish) | SpiderMonkey |
| **개발 언어** | C++ | C++ | C++, Rust (Stylo 등 일부 통합) |
| **주요 사용 브라우저** | Chrome, Edge, Opera, Brave, Vivaldi, Samsung Internet, Arc | Safari, iOS의 모든 브라우저 엔진 | Firefox, Tor Browser, LibreWolf |
| **시장 점유율** | 약 70% 이상 (추정치, 압도적 1위) | 약 18~20% (대부분 iOS 기반, 추정치) | 약 3% (추정치) |
| **플랫폼 지원** | Windows, macOS, Linux, Android※ iOS는 WebKit 강제 (Blink 사용 불가) | macOS, iOS (사실상 주요 플랫폼)※ 기타 포팅 존재하나 영향력 미미 | Windows, macOS, Linux, Android |
| **렌더링 아키텍처** | 멀티프로세스, Site Isolation | 멀티프로세스 (WebKit2) | 멀티프로세스 (Electrolysis, Fission) |
| **업데이트 속도** | 매우 빠름, 공격적 | 보수적, 신중함 | 중간, 표준 중심 |
| **표준 준수도** | 높음 (구현 영향력 큼, de facto reference 역할) | 높음 | 매우 높음 (표준 우선주의) |
| **개발자 도구** | Chrome DevTools | Safari Web Inspector | Firefox DevTools |
| **확장 프로그램** | Chrome Web Store (가장 광범위) | Safari Extensions (제한적) | AMO (WebExtensions) |
| **강점** | 빠른 신기능 도입, 거대한 생태계 | 전력 효율, Apple 생태계 통합 | 프라이버시, 표준 준수 |
| **약점** | Google 의존도, 높은 리소스 사용 | iOS 정책 제약, 느린 기능 도입 | 낮은 점유율, 일부 호환성 |
| **특징적 기술** | Site Isolation, WebGPU 적극 구현 | Intelligent Tracking Prevention (ITP) | Stylo (Rust), Total Cookie Protection |
| **모바일 영향력** | Android WebView 기반 | iOS 사실상 독점 | 미미 |

## Web Browser가 이해하는 파일 - HTML/CSS/JS (+ Wasm)

- 브라우저가 이해하는 핵심 리소스는 HTML(구조), CSS(스타일), JavaScript(로직)
- 현대 브라우저는 추가로 WebAssembly(Wasm)도 실행할 수 있음
    - C/C++/Rust 등의 언어를 Wasm으로 컴파일해 브라우저에서 실행 가능
    - Wasm은 JS로 변환되지 않는 별도의 바이너리 포맷임
- 브라우저 엔진이 로직 관점에서 실행 가능한 코드 형식은 JS와 Wasm으로 한정됨
    - 플랫폼 종속적인 네이티브 코드(x86, ARM 등)는 그대로 보낼 수 없음
        - 브라우저는 임의의 네이티브 코드를 로드/실행하는 메커니즘을 제공하지 않으며, 보안 및 포터빌리티 이유로 허용되지 않는다
            - 과거 Chrome에는 네이티브 코드 실행을 위한 NaCl/PNaCl이 있었으나, 보안·이식성 한계와 Wasm의 등장으로 폐기됨(2022년 제거 완료)
        - Wasm이 등장한 배경에는 "플랫폼 독립성 + 검증 가능한 안전한 바이너리 포맷" 두 축이 모두 있음
    - 따라서 서버에서 미리 네이티브 코드로 AOT 컴파일해놓고 클라이언트로 보내는 방식은 불가능
- Wasm은 정적 타입과 단순한 구조 덕분에 JS에 비해 더 빠르고 예측 가능한 컴파일 경로를 가지는 경우가 많다
    - 속도 관점: 시작 시점부터 더 빠르게 최적화된 코드를 얻을 수 있고, 워밍업 단계가 짧다
    - 예측 가능성 관점: Wasm 코드는 type feedback에 의존하지 않으므로 deoptimization이 발생하지 않고 성능이 안정적
- Wasm과 JS 실행 경로 비교
    - Wasm은 production 실행 경로에서는 인터프리터를 사용하지 않는다
        - V8 기준 Liftoff(baseline) → TurboFan(optimizing)의 tiered compilation을 사용
            - 다른 엔진(특히 일부 모바일/임베디드 환경)에서는 Wasm 인터프리터를 사용하는 경우도 존재
        - 단, 디버깅 목적의 인터프리터는 별도로 존재
    - 반면 JS는 인터프리터부터 시작한다.
        - Ignition (interpreter) → Sparkplug (baseline) → Maglev (mid-tier optimizing) → TurboFan (top-tier optimizing)
    - 참고: JS의 hot path가 TurboFan까지 도달하면 Wasm에 근접하거나 일부 워크로드에서는 빠를 수도 있다 (다만 일반적으로는 잘 작성된 Wasm이 동등하거나 우위인 경우가 많음)
- JS의 경우에도 V8의 **바이트코드 캐싱**(code caching) 등 일부 최적화는 존재함
    - 브라우저가 같은 스크립트를 다시 실행할 때 파싱+컴파일 비용을 줄이기 위해 바이트코드를 로컬에 캐시한다
- Wasm의 현재 한계
    - DOM/Web API에 직접 접근할 수 없으며, JS 바인딩을 거쳐야 함
        - JS↔Wasm 호출 경계 비용 발생
    - GC 언어(Java, Kotlin, Dart 등) 지원을 위한 WasmGC는 2023년에야 표준화되어 주요 브라우저에 도입됨
    - 따라서 현재까지는 C/C++/Rust 같은 비-GC 언어가 주된 컴파일 타겟이며, UI 전체를 Wasm으로 작성하는 것보다 연산 집약적인 부분에 부분적으로 사용하는 패턴이 일반적

### 참고: V8 엔진 동작 방식

- V8의 컴파일러 파이프라인은 다음과 같이 구성됨
    - Ignition: 인터프리터
        - Parser + BytecodeGenerator → 바이트코드 생성
            - 바이트코드 생성은 엄밀히는 BytecodeGenerator가 담당하고, Ignition은 그 바이트코드를 실행하는 인터프리터지만, V8 공식 문서에서도 Ignition 파이프라인으로 묶어 설명하는 경우가 많음
        - Ignition → 바이트코드 실행 (인터프리터)
    - Sparkplug: non-optimizing baseline JIT 컴파일러 (2021년 도입)
        - 바이트코드를 거의 1:1로 머신코드에 매핑하는 매우 단순한 컴파일러
        - 인터프리터 오버헤드를 제거하는 데 목적이 있음
            - 최소한의 최적화와 inline cache만 적용
    - Maglev: mid-tier 최적화 JIT 컴파일러 (2023년 도입)
        - Chrome M117에 도입된 mid-tier optimizing 컴파일러로, 플랫폼/아키텍처에 따라 활성화 여부가 다름
    - TurboFan: top-tier 고비용 고성능 최적화 JIT 컴파일러
- 실행 흐름
    - REF: https://community.intel.com/t5/Blogs/Tech-Innovation/Client/Profile-Guided-Tiering-in-the-V8-JavaScript-Engine/post/1679340
    - JS는 일단 Parser + BytecodeGenerator를 통해 바이트코드로 변환된 후 Ignition 인터프리터에 의해 실행된다
    - 실행 중 수집된 profiling 정보 및 이전 실행에서의 profile 데이터를 기반으로 일부 함수는 상위 tier 컴파일러로 최적화된다.
    - tier 전환은 각 함수 별로 runtime profiling 데이터(실행 빈도, 타입 정보)와 이전 실행에서 수집된 profile 데이터를 기반으로 이루어진다
        - A 함수: 바로 TurboFan
        - B 함수: Sparkplug에서 멈춤
        - C 함수: Maglev까지
        - D 함수: Ignition 인터프리터 상태 유지

## JavaScript의 스펙 - ECMAScript

- 역사적으로는 JavaScript(Netscape, 1995)가 먼저 나오고, 이를 표준화한 것이 ECMAScript(1997)
- 관계
    - ECMAScript = JavaScript 언어의 표준 명세
    - JavaScript = ECMAScript의 구현 + Host Environment API
        - ECMAScript 스펙은 "host environment" 개념을 통해 언어와 실행 환경 API를 명확히 분리
- Host Environment API 란
    - 브라우저 환경: Web API
        - WHATWG: DOM, HTML, Fetch, Streams, URL 등 핵심 런타임 API
        - W3C: CSS, WebRTC, WebGPU, Web Authentication 등
        - 영역별로 표준화 주체가 다르며, 위의 W3C vs WHATWG 표 참고
    - Node.js 환경: Node API (fs, process 등)
- 구조적으로 **JS 엔진**(V8, SpiderMonkey, JavaScriptCore)이 ECMAScript 코어를 구현하고, **브라우저 엔진**(Blink, Gecko, WebKit)이 Web API와 렌더링을 담당하며 바인딩으로 JS 엔진에 연결됨
    - JS 엔진은 JavaScript 파싱, 실행, 빌트인 객체 등을 담당
    - 브라우저 엔진이 Web API를 구현하고, 바인딩 레이어를 통해 JS 엔진(V8 등)에 노출
- ECMAScript 스펙은 계속 업데이트되고 있는데 엔진별로 지원 시점이 다름
    - Babel 등의 트랜스파일러를 사용해 최신 문법을 구버전 JS 문법으로 변환
        - 필요 시 polyfill(core-js 등)을 통해 런타임 기능도 보완

## JavaScript 모듈 시스템 비교 (CJS vs ESM)

- 최초에는 하나의 JavaScript 파일을 사용했지만, 점점 로직이 복잡해지면서 모듈화가 필요했음
    - 모두 전역이라 네임스페이스 문제 많았음
- CommonJS (CJS)
    - ECMAScript 표준은 아니며, Node.js 환경에서 사실상 표준처럼 사용된 모듈 시스템
        - CJS는 원래 Node.js 이전에 서버사이드 JS 모듈 표준을 만들려던 CommonJS 그룹의 명세였고, Node.js가 이를 채택해 대중화
    - `require()` 기반 (동기 로딩)
        - `require()`는 런타임에 평가되므로 정적 분석이 어렵고, 의존성 그래프를 빌드 타임에 완전히 알기 힘듦
        - require()는 모듈을 한 번 로드하면 캐싱되며, 이로 인해 싱글톤처럼 동작
    - 브라우저에서 native로 지원되지 않으며, 일반적으로 번들링을 통해 사용함
- ESM (ECMAScript Modules)
    - ECMAScript 표준 모듈 시스템
    - `import / export` 기반
        - 정적 import/export 구조 덕분에 bundler가 의존성을 분석해 tree shaking을 수행할 수 있음 (side-effect가 없는 경우에 한해 안전)
        - side-effect가 있는 모듈은 tree shaking이 안전하지 않을 수 있어 `package.json`의 `sideEffects` 필드로 명시하는 것이 일반적
    - 브라우저 native 지원 (`<script type="module">`)
    - top-level await는 ESM에서만 지원되며, CJS에서는 사용할 수 없음 (async 함수로 감싸야 함)

### 참고: **JavaScript 모듈 시스템 진화 흐름**

전역 → IIFE → {CJS(서버) ↔ AMD(브라우저)} → UMD → ESM

- **전역 (Global)**
    - 모든 코드가 전역 스코프에 존재
    - 네임스페이스 충돌 문제 발생
- **IIFE (Immediately Invoked Function Expression)**
    - 함수 스코프로 전역 오염 방지
    - 모듈처럼 "캡슐화"는 가능하지만, 의존성 관리 불가
- **CJS (CommonJS)** — 2009
    - **Node.js 중심** 모듈 시스템 (**서버 사이드용**으로 등장)
    - `require / module.exports`
    - 동기 로딩, 직관적이지만 브라우저에서는 번들 필요
- **AMD (Asynchronous Module Definition)** — 2010
    - CJS의 동기 로딩이 **브라우저 환경**에 부적합 → 비동기 로딩 필요성에서 등장
    - 의존성 명시 가능 (`define`)
    - 대표 구현체: RequireJS
- **UMD (Universal Module Definition)** — 2011
    - AMD + CJS + 전역 모두 지원하는 패턴
    - 라이브러리 배포용으로 널리 쓰임 (Lodash, Backbone.js, Moment.js 등)
    - 다양한 환경에서 동작하지만 구조가 복잡
- **ESM (ECMAScript Modules)** — ES6 (2015) 표준화
    - JavaScript 표준 모듈 시스템
    - `import / export` (정적 구조)
    - 브라우저 native 지원, tree shaking 가능
    - 브라우저 지원: 2017~2018년경 주요 브라우저 도입
    - Node.js 지원: v12(2019)에서 실험적 → v16(2021)에서 안정화

## Bundler의 역할

- Webpack, Vite 등은 대표적인 프론트엔드 빌드 도구이다.
    - Webpack은 전통적인 번들러
    - Vite는 dev server + 빌드 도구이며, production에서는 Rollup 기반 번들링 수행
- 참고: 최근에는 빌드 성능 개선을 위해 번들러/트랜스파일러를 Go(esbuild)나 Rust(SWC, Turbopack, Rspack, Biome 등)로 재작성하는 흐름이 두드러짐
    - JS로 작성된 기존 도구(Webpack, Babel 등) 대비 수 배~수십 배의 빌드 속도 향상
    - Vite도 내부적으로 esbuild를 의존성 사전 번들링 등에 활용
- 현대의 Bundler는 단순히 파일을 묶는 도구를 넘어 transform / optimize / dev server까지 포함하는 "프론트엔드 빌드 도구 체인"에 가깝다
    - 코드 변환 (transform)
    - 의존성 그래프 분석
    - 번들 생성 및 최적화 (tree shaking, code splitting)
    - polyfill 포함
    - dev server 및 HMR 제공
- Bundler가 하는 일은 좀더 자세히 살펴보면
    - transform (transpile 포함)
        - 다양한 소스(TypeScript, JSX, 최신 JS 등)를 타겟 환경에서 실행 가능한 JavaScript로 변환
    - minify
        - 이름 축약, 공백 제거, 표현식 단순화 등
            - 이름 축약 등으로 결과적으로 읽기 어려워지긴 하지만, 목적은 난독화가 아님
        - 코드 크기를 줄이고 다운로드/파싱 비용을 낮춤
    - polyfill
        - polyfill은 신규 API의 경우 core-js 같은 라이브러리로 런타임에 채워 넣고, 신규 문법은 Babel이 빌드 시점에 구버전 문법으로 변환하는 식으로 처리됨
            - **API polyfill** (예: `Promise`, `Array.prototype.includes`) — core-js 같은 라이브러리로 런타임에 채워 넣음
            - **문법 변환** (예: async/await, 옵셔널 체이닝) — Babel transform이 빌드 시점에 구버전 문법으로 변환
        - 엄밀히는 bundler가 직접 polyfill을 주입하는 것이 아니라, Babel(`@babel/preset-env` + `core-js`)이나 `browserslist` 설정에 따라 결정되고 bundler는 그 결과를 번들에 포함시키는 역할
    - 의존성 그래프 (Dependency Graph) 분석
        - 모듈 간 import/export 관계를 분석하여 그래프 구조로 구성
        - 이를 기반으로 tree shaking, code splitting, 번들 생성 등의 최적화 수행
    - tree shaking
        - 사용되지 않는 코드를 제거하여 번들 크기 감소
        - ES Module의 static 구조(import/export)를 기반으로 동작하며 side-effect가 없는 코드만 안전하게 제거 가능
    - Bundling
        - 여러 파일로 구성된 것을 번들로 만들어줌 (꼭 1개일 필요는 없음)
        - 파일 수가 많으면 요청 오버헤드가 증가할 수 있음 (HTTP/2 이상에서는 영향이 줄었지만 여전히 관리 및 최적화 관점에서 중요)
        - 반면 너무 큰 파일 하나로 번들링하면 초기 로딩 시간이 길어질 수 있음
            - 현대에는 단일 파일이 아닌 code splitting / chunking / lazy loading 전략이 핵심
            - 초기 로딩을 빠르게 하고 추가로 사용될 때마다 파일을 가져오는 식
    - dev server
        - 전통적인 번들러의 기능이라기보다는, Vite 같은 빌드 도구 체인이 제공하는 개발용 기능
        - 번들링 없이, ESM 기반으로 브라우저에 모듈을 직접 제공하여 빠른 개발 경험을 제공 (Vite 등)
            - 요청된 모듈만 on-demand로 transform → 초기 시작이 빠름
            - 변경된 모듈만 교체하는 HMR(Hot Module Replacement) → 수정 반영이 빠름
    - Asset 처리
        - 이미지, CSS, 폰트 등을 JavaScript 모듈처럼 import 가능하게 처리
        - 빌드 시 파일 해싱, 경로 변환, 최적화(압축 등)을 수행하여 효율적인 리소스 관리 지원

### 참고: 번들링이 필요한 이유

- 번들링이 필요한 이유는 단순히 "파일 수 줄이기"가 아니다.
    - tree shaking
    - minification 효율
    - 압축률
        - 번들링을 통해 코드 중복이 줄고 패턴이 증가하여 gzip/brotli 압축 효율이 좋아지는 경향이 있음
    - 의존성 graph fetch 시 발생하는 waterfall 방지
        - HTTP/2로 네트워크 waterfall은 완화되었지만, 의존성 로딩 및 평가 순서로 인한 지연은 여전히 존재
    - 등
- HTTP/2 멀티플렉싱과 native ESM의 성숙으로 "파일 수" 자체의 비용은 크게 줄었기 때문에, dev 환경에서는 unbundled 방식(Vite의 dev server 등)이 주류가 됨
- production에서도 unbundled 방식을 시도하는 사례가 존재하지만, 위의 다른 이점들 때문에 주류는 여전히 번들링
    - 참고로 unbundled production을 표방했던 Snowpack은 2022년 이후 사실상 개발이 중단되었고, Vite도 production에서는 Rollup으로 번들링하는 쪽을 택함

### 참고: 네트워크 waterfall 이란?

- 리소스 간 의존성 때문에 요청이 부분적으로 직렬화되며 지연이 누적되는 현상.

```
번들링 전:
HTML → app.js → react.js → hooks.js

번들링 후:
HTML → bundle.js
```

- 브라우저는 파싱/실행을 통해서만 다음 요청(의존성)을 알 수 있음
- HTTP/2, HTTP/3는 전송 효율은 개선하지만 dependency discovery 문제는 해결 못함
- 번들링은 의존성 탐색을 빌드 타임으로 옮겨 waterfall을 완화 (trade-off 존재)
    - 번들 크기가 커지면 초기 로딩이 느려질 수 있어 code splitting 등이 필요

## NodeJS

- V8 기반의 JavaScript 런타임
    - JS 실행 자체는 V8이 담당
    - 이벤트 루프는 libuv가 제공하며, Node.js는 그 위에서 비동기 작업과 콜백 큐(마이크로태스크 포함)를 조율
        - 마이크로태스크 큐(Promise 등)는 V8이 관리하고, Node.js는 libuv 기반 이벤트 루프 위에서 이를 통합적으로 실행
        - `JS 코드 → V8 → (비동기 작업 요청) → libuv → 이벤트 루프 → callback → V8`
    - 브라우저와 달리 fs, net 등 시스템 레벨 API를 제공하므로, 동일한 JS 코드라도 실행 환경(브라우저 vs Node.js)에 따라 동작이 달라질 수 있음
- 서버 및 CLI 환경에서 JavaScript를 실행하기 위한 대표적인 런타임
- 하지만 브라우저에서 사용될 앱을 개발할 때도 NodeJS가 쓰임 → 번들링 해야함
    - Pure HTML/CSS/JavaScript로 개발하면 바로 브라우저에서 실행이 되긴한다.
        - 요즘은 브라우저도 native ESM을 지원해서 `<script type="module">`로 빌드 없이 모듈 import도 가능
    - 하지만 대부분의 SPA 및 대규모 프론트엔드 애플리케이션에서는 최적화, 호환성, 성능 등의 이유로 여전히 번들링이 널리 사용되며, 이 과정을 위해 Node.js 기반 빌드 툴체인을 사용하는 경우가 많다.

## 참고 자료 (References)

**표준 단체 / 명세**

- [WHATWG HTML Living Standard](https://html.spec.whatwg.org/)
- [WHATWG](https://whatwg.org/)
- [W3C](https://www.w3.org/)
- [ECMAScript Language Specification (ECMA-262)](https://tc39.es/ecma262/)
- [TC39 — ECMAScript 표준화 위원회](https://tc39.es/)

**브라우저 / 렌더링 엔진**

- [Blink: A rendering engine for the Chromium project (Chromium Blog, 2013)](https://blog.chromium.org/2013/04/blink-rendering-engine-for-chromium.html)
- [Chromium — Site Isolation](https://www.chromium.org/Home/chromium-security/site-isolation/)
- [WebKit](https://webkit.org/)
- [Gecko (MDN)](https://developer.mozilla.org/en-US/docs/Glossary/Gecko)
- [Apple — DMA 대응으로 EU에서 대체 브라우저 엔진 허용 (iOS 17.4)](https://developer.apple.com/support/alternative-browser-engines/)

**V8 / JavaScript 엔진**

- [V8 공식 블로그](https://v8.dev/blog)
- [Ignition: V8 인터프리터](https://v8.dev/blog/ignition-interpreter)
- [Sparkplug — V8 baseline JIT](https://v8.dev/blog/sparkplug)
- [Maglev — V8's Fastest Optimizing JIT](https://v8.dev/blog/maglev)
- [Code caching for JavaScript developers](https://v8.dev/blog/code-caching-for-devs)
- [Profile-Guided Tiering in the V8 Engine (Intel)](https://community.intel.com/t5/Blogs/Tech-Innovation/Client/Profile-Guided-Tiering-in-the-V8-JavaScript-Engine/post/1679340)

**WebAssembly**

- [WebAssembly 공식 사이트](https://webassembly.org/)
- [Liftoff — Wasm baseline 컴파일러 (V8)](https://v8.dev/blog/liftoff)
- [WasmGC: garbage collected 언어를 Wasm으로 (V8)](https://v8.dev/blog/wasm-gc-porting)

**모듈 시스템**

- [JavaScript modules (MDN)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)
- [Node.js — ECMAScript modules](https://nodejs.org/api/esm.html)
- [webpack — Tree Shaking (`sideEffects`)](https://webpack.js.org/guides/tree-shaking/)

**번들러 / 빌드 도구**

- [Vite](https://vite.dev/) · [Dependency Pre-Bundling](https://vite.dev/guide/dep-pre-bundling.html)
- [Rollup](https://rollupjs.org/)
- [esbuild](https://esbuild.github.io/)
- [SWC](https://swc.rs/)
- [@babel/preset-env](https://babeljs.io/docs/babel-preset-env) · [core-js](https://github.com/zloirock/core-js) · [Browserslist](https://github.com/browserslist/browserslist)

**Node.js**

- [Node.js 공식](https://nodejs.org/)
- [libuv](https://libuv.org/)
- [The Node.js Event Loop](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick/)
