---
title: "An Overview of Web Browser Technology — A JavaScript Perspective"
date: 2026-05-30T11:00:00+09:00
draft: false
slug: "web-browser-internals"
translationKey: "web-browser-internals"
categories: ["Engineering"]
tags: ["browser", "javascript", "v8", "webassembly", "bundler"]
summary: "Web browser technology from a JavaScript perspective — browser engines, V8 tiering, ECMAScript, module systems, bundlers, and Node.js in one pass."
---

## A Short History of Web Browsers

- Standards existed even in the early days of the web
    - HTML/CSS were standardized by the W3C, JavaScript by ECMA International (ECMAScript)
- The problem wasn't the absence of standards but inconsistent implementations across browsers
    - The Internet Explorer vs. Netscape Navigator era had severe compatibility issues
- Later, as Chromium-family browsers built on Blink (a separate engine Google forked from WebKit in 2013) spread and WHATWG-centered standards collaboration strengthened, conformance improved dramatically
    - Blink and WebKit now evolve independently, and Safari is about the only major browser still using WebKit directly
    - Chromium has a large influence on the evolution of the web platform and often acts as a de facto reference implementation
- With V8's JIT optimizations in Chromium plus broad architectural improvements across browser engines, overall performance improved enormously compared to the previous generation of browsers.
    - JIT advances, multi-process architecture, GPU acceleration, etc.

### Aside: W3C vs. WHATWG

- The two bodies responsible for HTML and CSS standards
    - W3C (**W**orld **W**ide **W**eb **C**onsortium)
        - The early standards body
    - WHATWG (**W**eb **H**ypertext **A**pplication **T**echnology **W**orking **G**roup)
        - Led by browser vendors, appeared in 2004

| Aspect | WHATWG | W3C |
| --- | --- | --- |
| Core philosophy | Based on real browser behavior (reality-driven) | Defining an ideal standard (spec-driven) |
| Standards model | **Living Standard** (continuously updated) | **Snapshot/versioned** (HTML5, etc.) |
| Update speed | Fast (immediate) | Slow (requires consensus) |
| Flexibility | High | Low (stability first) |
| Main participants | Browser-vendor centric (Apple, Mozilla, etc.) | Diverse companies/institutions (broad participation) |
| Influence on HTML standard | ⭐ The de facto standard today | Historically central, now secondary |
| CSS/other standards | Involved only partially | ⭐ Still a core role |
| Practical baseline | Develop against the latest browsers | Reference official docs/recommendations |

### Aside: Blink vs. WebKit (vs. Gecko)

- WebKit = rendering engine (HTML/CSS) + JS engine (JavaScriptCore)
    - WebCore (rendering) + JavaScriptCore (JS engine)
    - On iOS, Apple's policy requires every browser to use WebKit, so iOS Chrome also uses WebKit internally
        - Since the EU's DMA (Digital Markets Act) took effect in 2024, alternative engines are allowed in the EU region
- Blink = forked from WebKit's WebCore (the rendering part)
    - Uses V8 as its JS engine
- Gecko = a separate engine used by Mozilla Firefox

| Category | Blink | WebKit | Gecko |
| --- | --- | --- | --- |
| **Developer** | Google (Chromium project) | Apple | Mozilla Foundation |
| **Released/started** | 2013 (forked from WebKit's WebCore) | 2001 (forked from KHTML) | 1998 (Netscape open-sourced) |
| **Origin** | Branched from WebKit | Branched from KHTML/KJS | Netscape NGLayout |
| **License** | BSD, LGPL | LGPL (WebCore), BSD (JavaScriptCore) | MPL 2.0 |
| **JavaScript engine** | V8 | JavaScriptCore (Nitro/SquirrelFish) | SpiderMonkey |
| **Language** | C++ | C++ | C++, Rust (partially integrated, e.g. Stylo) |
| **Major browsers** | Chrome, Edge, Opera, Brave, Vivaldi, Samsung Internet, Arc | Safari, all iOS browser engines | Firefox, Tor Browser, LibreWolf |
| **Market share** | ~70%+ (estimate, dominant #1) | ~18–20% (mostly iOS-based, estimate) | ~3% (estimate) |
| **Platform support** | Windows, macOS, Linux, Android※ iOS forces WebKit (Blink not allowed) | macOS, iOS (effectively the main platforms)※ other ports exist but have little impact | Windows, macOS, Linux, Android |
| **Rendering architecture** | Multi-process, Site Isolation | Multi-process (WebKit2) | Multi-process (Electrolysis, Fission) |
| **Update speed** | Very fast, aggressive | Conservative, cautious | Moderate, standards-focused |
| **Standards conformance** | High (large implementation influence, de facto reference role) | High | Very high (standards-first) |
| **DevTools** | Chrome DevTools | Safari Web Inspector | Firefox DevTools |
| **Extensions** | Chrome Web Store (broadest) | Safari Extensions (limited) | AMO (WebExtensions) |
| **Strengths** | Fast feature adoption, huge ecosystem | Power efficiency, Apple ecosystem integration | Privacy, standards conformance |
| **Weaknesses** | Google dependence, high resource use | iOS policy constraints, slower feature adoption | Low share, some compatibility gaps |
| **Signature tech** | Site Isolation, aggressive WebGPU implementation | Intelligent Tracking Prevention (ITP) | Stylo (Rust), Total Cookie Protection |
| **Mobile influence** | Powers Android WebView | Effective iOS monopoly | Negligible |

## What a Browser Understands — HTML/CSS/JS (+ Wasm)

- The core resources a browser understands are HTML (structure), CSS (style), and JavaScript (logic)
- Modern browsers can additionally execute WebAssembly (Wasm)
    - Languages like C/C++/Rust can be compiled to Wasm and run in the browser
    - Wasm is a separate binary format that is *not* transpiled to JS
- From a logic standpoint, the only executable code formats a browser engine accepts are JS and Wasm
    - Platform-dependent native code (x86, ARM, etc.) can't be sent as-is
        - Browsers provide no mechanism to load/run arbitrary native code; it isn't allowed for security and portability reasons
            - Chrome historically had NaCl/PNaCl for native execution, but it was deprecated due to security/portability limits and the arrival of Wasm (fully removed in 2022)
        - Wasm came about for two reasons together: "platform independence + a verifiable, safe binary format"
    - So the approach of AOT-compiling to native code on the server and shipping it to the client is not possible
- Thanks to static typing and a simpler structure, Wasm often has a faster, more predictable compilation path than JS
    - Speed: it can reach optimized code faster from startup, with a shorter warm-up phase
    - Predictability: Wasm code doesn't rely on type feedback, so it doesn't suffer deoptimization and performs stably
- Comparing Wasm and JS execution paths
    - Wasm does not use an interpreter on the production execution path
        - In V8 it uses tiered compilation: Liftoff (baseline) → TurboFan (optimizing)
            - Some engines (especially certain mobile/embedded environments) do use a Wasm interpreter
        - A separate interpreter for debugging purposes does exist, though
    - JS, by contrast, starts from an interpreter.
        - Ignition (interpreter) → Sparkplug (baseline) → Maglev (mid-tier optimizing) → TurboFan (top-tier optimizing)
    - Note: once a JS hot path reaches TurboFan it can approach Wasm and, for some workloads, even be faster (though in general well-written Wasm tends to be on par or ahead)
- JS also has some optimizations such as V8's **bytecode caching** (code caching)
    - When the browser re-runs the same script, it caches bytecode locally to reduce parse + compile cost
- Current limitations of Wasm
    - It can't access the DOM/Web APIs directly; it must go through JS bindings
        - This incurs a JS↔Wasm call-boundary cost
    - WasmGC, which supports GC languages (Java, Kotlin, Dart, etc.), was only standardized and shipped in major browsers in 2023
    - So for now non-GC languages like C/C++/Rust remain the main compile targets, and the common pattern is to use Wasm partially for compute-intensive parts rather than writing the entire UI in Wasm

### Aside: How the V8 Engine Works

- V8's compiler pipeline is structured as follows
    - Ignition: the interpreter
        - Parser + BytecodeGenerator → generate bytecode
            - Strictly speaking the BytecodeGenerator produces the bytecode and Ignition is the interpreter that executes it, but V8's official docs often group them together as the "Ignition pipeline"
        - Ignition → execute bytecode (interpreter)
    - Sparkplug: a non-optimizing baseline JIT compiler (introduced 2021)
        - A very simple compiler that maps bytecode almost 1:1 to machine code
        - Its goal is to remove interpreter overhead
            - Applies only minimal optimization and inline caches
    - Maglev: a mid-tier optimizing JIT compiler (introduced 2023)
        - A mid-tier optimizing compiler introduced in Chrome M117; whether it's enabled depends on the platform/architecture
    - TurboFan: the top-tier, expensive, high-performance optimizing JIT compiler
- Execution flow
    - REF: https://community.intel.com/t5/Blogs/Tech-Innovation/Client/Profile-Guided-Tiering-in-the-V8-JavaScript-Engine/post/1679340
    - JS is first turned into bytecode via Parser + BytecodeGenerator, then executed by the Ignition interpreter
    - Based on profiling collected during execution plus profile data from previous runs, some functions are optimized by higher-tier compilers.
    - Tier transitions happen per function, driven by runtime profiling data (execution frequency, type info) and profile data gathered in previous runs
        - Function A: straight to TurboFan
        - Function B: stops at Sparkplug
        - Function C: up to Maglev
        - Function D: stays in the Ignition interpreter

## The JavaScript Spec — ECMAScript

- Historically JavaScript (Netscape, 1995) came first, and ECMAScript (1997) was its standardization
- The relationship
    - ECMAScript = the standard specification of the JavaScript language
    - JavaScript = an implementation of ECMAScript + Host Environment APIs
        - The ECMAScript spec cleanly separates the language from runtime-environment APIs via the "host environment" concept
- What are Host Environment APIs
    - Browser environment: Web APIs
        - WHATWG: core runtime APIs like DOM, HTML, Fetch, Streams, URL
        - W3C: CSS, WebRTC, WebGPU, Web Authentication, etc.
        - The standardizing body differs by area; see the W3C vs. WHATWG table above
    - Node.js environment: Node APIs (fs, process, etc.)
- Structurally, the **JS engine** (V8, SpiderMonkey, JavaScriptCore) implements the ECMAScript core, while the **browser engine** (Blink, Gecko, WebKit) handles Web APIs and rendering, connected to the JS engine via bindings
    - The JS engine handles JavaScript parsing, execution, built-in objects, etc.
    - The browser engine implements Web APIs and exposes them to the JS engine (e.g. V8) through a binding layer
- The ECMAScript spec keeps being updated, and support timelines differ by engine
    - Transpilers like Babel convert the latest syntax into older JS syntax
        - When needed, polyfills (core-js, etc.) fill in runtime features as well

## Comparing JavaScript Module Systems (CJS vs. ESM)

- At first a single JavaScript file was used, but as logic grew more complex, modularization became necessary
    - Everything was global, causing many namespace problems
- CommonJS (CJS)
    - Not an ECMAScript standard, but the module system that became a de facto standard in the Node.js environment
        - CJS was originally a spec from the CommonJS group, which predated Node.js and aimed to define a server-side JS module standard; Node.js adopted it and popularized it
    - Based on `require()` (synchronous loading)
        - Because `require()` is evaluated at runtime, static analysis is hard and the dependency graph can't be fully known at build time
        - Once `require()` loads a module it's cached, so it behaves like a singleton
    - Not natively supported in browsers; typically used via bundling
- ESM (ECMAScript Modules)
    - The standard ECMAScript module system
    - Based on `import / export`
        - Thanks to the static import/export structure, bundlers can analyze dependencies and perform tree shaking (safe only when there are no side effects)
        - Modules with side effects may not be safe to tree-shake, so it's common to declare them via the `sideEffects` field in `package.json`
    - Natively supported in browsers (`<script type="module">`)
    - Top-level await is only supported in ESM and can't be used in CJS (you'd have to wrap it in an async function)

### Aside: **The Evolution of JavaScript Module Systems**

Global → IIFE → {CJS (server) ↔ AMD (browser)} → UMD → ESM

- **Global**
    - All code lives in the global scope
    - Namespace collision problems arise
- **IIFE (Immediately Invoked Function Expression)**
    - Prevents global pollution via function scope
    - Allows module-like "encapsulation" but no dependency management
- **CJS (CommonJS)** — 2009
    - A **Node.js-centric** module system (introduced for **server-side** use)
    - `require / module.exports`
    - Synchronous loading; intuitive but needs bundling in the browser
- **AMD (Asynchronous Module Definition)** — 2010
    - CJS's synchronous loading was unsuitable for the **browser** → emerged from the need for asynchronous loading
    - Lets you declare dependencies (`define`)
    - Representative implementation: RequireJS
- **UMD (Universal Module Definition)** — 2011
    - A pattern that supports AMD + CJS + global all at once
    - Widely used for distributing libraries (Lodash, Backbone.js, Moment.js, etc.)
    - Works across many environments but has a complex structure
- **ESM (ECMAScript Modules)** — standardized in ES6 (2015)
    - The standard JavaScript module system
    - `import / export` (static structure)
    - Native browser support, tree shaking possible
    - Browser support: adopted by major browsers around 2017–2018
    - Node.js support: experimental in v12 (2019) → stabilized in v16 (2021)

## The Role of the Bundler

- Webpack, Vite, etc. are representative front-end build tools.
    - Webpack is the traditional bundler
    - Vite is a dev server + build tool, and uses Rollup-based bundling in production
- Note: recently there's a strong trend of rewriting bundlers/transpilers in Go (esbuild) or Rust (SWC, Turbopack, Rspack, Biome, etc.) to improve build performance
    - Several-fold to tens-of-fold faster builds compared to existing JS-written tools (Webpack, Babel, etc.)
    - Vite also uses esbuild internally for things like dependency pre-bundling
- A modern bundler is less a tool that merely concatenates files and more a "front-end build toolchain" that includes transform / optimize / dev server
    - Code transformation (transform)
    - Dependency graph analysis
    - Bundle creation and optimization (tree shaking, code splitting)
    - Polyfill inclusion
    - Dev server and HMR
- Looking at what a bundler does in more detail
    - transform (including transpile)
        - Convert various sources (TypeScript, JSX, latest JS, etc.) into JavaScript runnable in the target environment
    - minify
        - Name shortening, whitespace removal, expression simplification, etc.
            - Name shortening makes the result harder to read, but the purpose is not obfuscation
        - Reduces code size and lowers download/parse cost
    - polyfill
        - Polyfills handle new APIs by filling them in at runtime with libraries like core-js, while new syntax is converted to older syntax by Babel at build time
            - **API polyfills** (e.g. `Promise`, `Array.prototype.includes`) — filled in at runtime by libraries like core-js
            - **Syntax transforms** (e.g. async/await, optional chaining) — converted to older syntax at build time by Babel transforms
        - Strictly speaking, the bundler doesn't inject polyfills directly; it's decided by Babel (`@babel/preset-env` + `core-js`) or the `browserslist` config, and the bundler's role is to include the result in the bundle
    - Dependency Graph analysis
        - Analyze import/export relationships between modules into a graph structure
        - Use it as the basis for optimizations like tree shaking, code splitting, and bundle generation
    - tree shaking
        - Remove unused code to reduce bundle size
        - Works based on ES Module's static structure (import/export); only code with no side effects can be safely removed
    - Bundling
        - Combines files into bundles (not necessarily a single one)
        - Many files can increase request overhead (HTTP/2+ reduced this, but it still matters for management and optimization)
        - On the other hand, bundling everything into one huge file can lengthen initial load
            - The modern key is not a single file but code splitting / chunking / lazy loading strategies
            - Make the initial load fast and fetch additional files as they're needed
    - dev server
        - Less a feature of traditional bundlers, more a development feature provided by build toolchains like Vite
        - Without bundling, it serves modules directly to the browser over ESM for a fast development experience (Vite, etc.)
            - Only requested modules are transformed on-demand → fast startup
            - HMR (Hot Module Replacement) swaps only changed modules → fast feedback
    - Asset handling
        - Lets you import images, CSS, fonts, etc. like JavaScript modules
        - Performs file hashing, path rewriting, and optimization (compression, etc.) at build time for efficient resource management

### Aside: Why Bundling Is Needed

- The reason bundling is needed isn't simply "reducing the number of files."
    - tree shaking
    - minification efficiency
    - compression ratio
        - Bundling tends to reduce code duplication and increase patterns, improving gzip/brotli compression efficiency
    - preventing the waterfall that occurs while fetching the dependency graph
        - HTTP/2 eased the network waterfall, but delays from dependency loading and evaluation order still exist
    - and so on
- Because HTTP/2 multiplexing and mature native ESM greatly reduced the cost of "number of files" itself, the unbundled approach (Vite's dev server, etc.) became mainstream in dev environments
- There are cases of trying unbundled approaches in production too, but because of the other benefits above, bundling is still mainstream
    - For reference, Snowpack, which championed unbundled production, has effectively been unmaintained since 2022, and Vite too chose to bundle with Rollup in production

### Aside: What Is a Network Waterfall?

- A phenomenon where requests get partially serialized due to dependencies between resources, accumulating latency.

```
Before bundling:
HTML → app.js → react.js → hooks.js

After bundling:
HTML → bundle.js
```

- The browser can only learn the next request (a dependency) by parsing/executing
- HTTP/2 and HTTP/3 improve transfer efficiency but don't solve the dependency-discovery problem
- Bundling moves dependency discovery to build time and eases the waterfall (with trade-offs)
    - If the bundle grows large, initial load can slow down, so code splitting and the like become necessary

## Node.js

- A V8-based JavaScript runtime
    - V8 itself handles JS execution
    - The event loop is provided by libuv, on top of which Node.js orchestrates async work and callback queues (including microtasks)
        - The microtask queue (Promises, etc.) is managed by V8, and Node.js executes it in an integrated way on top of the libuv-based event loop
        - `JS code → V8 → (async work request) → libuv → event loop → callback → V8`
    - Unlike the browser, it provides system-level APIs such as fs and net, so the same JS code can behave differently depending on the execution environment (browser vs. Node.js)
- A representative runtime for executing JavaScript in server and CLI environments
- But Node.js is also used when developing apps meant for the browser → you need to bundle
    - Developing in pure HTML/CSS/JavaScript does run directly in the browser.
        - These days browsers support native ESM too, so you can even import modules without a build via `<script type="module">`
    - But most SPAs and large front-end applications still widely use bundling for reasons of optimization, compatibility, and performance, and a Node.js-based build toolchain is often used for this process.

## References

**Standards bodies / specifications**

- [WHATWG HTML Living Standard](https://html.spec.whatwg.org/)
- [WHATWG](https://whatwg.org/)
- [W3C](https://www.w3.org/)
- [ECMAScript Language Specification (ECMA-262)](https://tc39.es/ecma262/)
- [TC39 — the ECMAScript standards committee](https://tc39.es/)

**Browsers / rendering engines**

- [Blink: A rendering engine for the Chromium project (Chromium Blog, 2013)](https://blog.chromium.org/2013/04/blink-rendering-engine-for-chromium.html)
- [Chromium — Site Isolation](https://www.chromium.org/Home/chromium-security/site-isolation/)
- [WebKit](https://webkit.org/)
- [Gecko (MDN)](https://developer.mozilla.org/en-US/docs/Glossary/Gecko)
- [Apple — Alternative browser engines in the EU under the DMA (iOS 17.4)](https://developer.apple.com/support/alternative-browser-engines/)

**V8 / JavaScript engine**

- [V8 official blog](https://v8.dev/blog)
- [Ignition: the V8 interpreter](https://v8.dev/blog/ignition-interpreter)
- [Sparkplug — V8 baseline JIT](https://v8.dev/blog/sparkplug)
- [Maglev — V8's Fastest Optimizing JIT](https://v8.dev/blog/maglev)
- [Code caching for JavaScript developers](https://v8.dev/blog/code-caching-for-devs)
- [Profile-Guided Tiering in the V8 Engine (Intel)](https://community.intel.com/t5/Blogs/Tech-Innovation/Client/Profile-Guided-Tiering-in-the-V8-JavaScript-Engine/post/1679340)

**WebAssembly**

- [WebAssembly official site](https://webassembly.org/)
- [Liftoff — Wasm baseline compiler (V8)](https://v8.dev/blog/liftoff)
- [WasmGC: bringing garbage-collected languages to Wasm (V8)](https://v8.dev/blog/wasm-gc-porting)

**Module systems**

- [JavaScript modules (MDN)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)
- [Node.js — ECMAScript modules](https://nodejs.org/api/esm.html)
- [webpack — Tree Shaking (`sideEffects`)](https://webpack.js.org/guides/tree-shaking/)

**Bundlers / build tools**

- [Vite](https://vite.dev/) · [Dependency Pre-Bundling](https://vite.dev/guide/dep-pre-bundling.html)
- [Rollup](https://rollupjs.org/)
- [esbuild](https://esbuild.github.io/)
- [SWC](https://swc.rs/)
- [@babel/preset-env](https://babeljs.io/docs/babel-preset-env) · [core-js](https://github.com/zloirock/core-js) · [Browserslist](https://github.com/browserslist/browserslist)

**Node.js**

- [Node.js official](https://nodejs.org/)
- [libuv](https://libuv.org/)
- [The Node.js Event Loop](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick/)
