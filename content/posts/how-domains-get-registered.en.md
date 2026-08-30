---
title: "How a Domain Gets Registered, in Pictures"
date: 2026-08-30T16:13:10+09:00
draft: false
slug: "how-domains-get-registered"
translationKey: "how-domains-get-registered"
categories: ["Engineering"]
tags: ["dns", "domain", "networking", "intro"]
summary: "How a domain becomes yours, and how the name you type in the address bar finds a server — in nine pictures."
---

<style>
.dgm { --dgm-accent: #14468C; --dgm-go: #1B7A54; --dgm-stop: #A8402A; margin: 0 0 var(--content-gap); }
:root[data-theme="dark"] .dgm { --dgm-accent: #2E6BC4; --dgm-go: #4FBE90; --dgm-stop: #E5876A; }
.dgm .dgm-scroll { overflow-x: auto; }
.dgm svg { display: block; width: 100%; height: auto; color: var(--content); }
.dgm svg text { font-family: inherit; }
.dgm svg .m { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
</style>

A domain is a street sign you hang on the internet. To put a site into the world you first have to rent an address, and that process is split across more layers than most people expect. Here is what happens behind the register button, and how a name someone types in the address bar eventually reaches your server.

## Computers use numbers, people use names

Computers find each other by number. People can't memorize numbers. So we bolted names on top.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 210" role="img" aria-label="DNS translates the domain name people use into the IP address computers use">
    <defs>
      <marker id="d1a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
    </defs>
    <text x="10" y="42" font-size="13" font-weight="700" fill="var(--secondary)">What people remember</text>
    <rect x="10" y="58" width="250" height="88" rx="10" fill="var(--dgm-accent)"/>
    <text class="m" x="135" y="110" font-size="22" fill="#fff" text-anchor="middle">mystore.com</text>
    <line x1="286" y1="102" x2="414" y2="102" stroke="currentColor" stroke-width="2" marker-end="url(#d1a)"/>
    <text x="350" y="89" font-size="14" font-weight="700" fill="currentColor" text-anchor="middle">DNS translates</text>
    <text x="350" y="128" font-size="12" fill="var(--secondary)" text-anchor="middle">the internet's phone book</text>
    <text x="440" y="42" font-size="13" font-weight="700" fill="var(--secondary)">What computers use</text>
    <rect x="440" y="58" width="270" height="88" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text class="m" x="575" y="110" font-size="22" fill="currentColor" text-anchor="middle">203.0.113.42</text>
    <text x="10" y="188" font-size="13.5" fill="var(--secondary)">Without names, we'd have to memorize this number every time.</text>
  </svg>
  </div>
  <figcaption><p>Turning a domain name into an IP address — that is all DNS does.</p></figcaption>
</figure>

## Four layers hand out addresses

Domains aren't sold by one place. The body that makes the rules, the one that holds the ledger, the counter you buy at, and you. Four layers.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 440" role="img" aria-label="ICANN delegates operation to the registry, the registry delegates retail to registrars, the registrant applies through a registrar, and the record lands in the registry ledger">
    <defs>
      <marker id="d2a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
      <marker id="d2b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-accent)"/></marker>
    </defs>
    <rect x="170" y="12" width="380" height="72" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="192" y="42" font-size="16.5" font-weight="700" fill="currentColor">ICANN</text>
    <text x="192" y="66" font-size="13" fill="var(--secondary)">Oversees all names on the internet</text>
    <line x1="360" y1="84" x2="360" y2="118" stroke="currentColor" stroke-width="2" marker-end="url(#d2a)"/>
    <text x="562" y="106" font-size="12.5" fill="var(--secondary)">delegates operation</text>
    <rect x="170" y="118" width="380" height="72" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="192" y="148" font-size="16.5" font-weight="700" fill="currentColor">Registry · keeper of the ledger</text>
    <text x="192" y="172" font-size="13" fill="var(--secondary)">.com is Verisign, .kr is KISA</text>
    <line x1="360" y1="190" x2="360" y2="224" stroke="currentColor" stroke-width="2" marker-end="url(#d2a)"/>
    <text x="562" y="212" font-size="12.5" fill="var(--secondary)">delegates retail</text>
    <rect x="170" y="224" width="380" height="72" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="192" y="254" font-size="16.5" font-weight="700" fill="currentColor">Registrar · the counter</text>
    <text x="192" y="278" font-size="13" fill="var(--secondary)">Cloudflare, GoDaddy, Namecheap…</text>
    <line x1="360" y1="296" x2="360" y2="330" stroke="currentColor" stroke-width="2" marker-end="url(#d2a)"/>
    <text x="562" y="318" font-size="12.5" fill="var(--secondary)">apply · pay</text>
    <rect x="170" y="330" width="380" height="72" rx="10" fill="var(--dgm-accent)"/>
    <text x="192" y="360" font-size="16.5" font-weight="700" fill="#fff">Me · the registrant</text>
    <text x="192" y="384" font-size="13" fill="rgba(255,255,255,.82)">Rents the right to use, a year at a time</text>
    <path d="M170,366 L96,366 L96,154 L164,154" fill="none" stroke="var(--dgm-accent)" stroke-width="2" marker-end="url(#d2b)"/>
    <text x="82" y="260" font-size="12.5" font-weight="700" fill="var(--dgm-accent)" text-anchor="middle" transform="rotate(-90 82 260)">my name enters the ledger</text>
    <text x="10" y="428" font-size="13" fill="var(--secondary)">You pay the counter, but the record lives in the registry's ledger.</text>
  </svg>
  </div>
  <figcaption><p>You can switch counters. The domain in the ledger follows you.</p></figcaption>
</figure>

## Registration is five steps

What you actually do at the counter is this much.

### 1. Pick a name

You invent the front half and choose the back half. That back half — `.com`, `.kr`, `.io` — is the TLD (top-level domain).

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 175" role="img" aria-label="A domain splits into the name you invent and the TLD you choose">
    <rect x="140" y="26" width="280" height="80" rx="10" fill="var(--dgm-accent)"/>
    <text class="m" x="280" y="76" font-size="26" fill="#fff" text-anchor="middle">mystore</text>
    <rect x="420" y="26" width="160" height="80" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text class="m" x="500" y="76" font-size="26" fill="currentColor" text-anchor="middle">.com</text>
    <line x1="280" y1="114" x2="280" y2="128" stroke="var(--tertiary)" stroke-width="1.5"/>
    <line x1="500" y1="114" x2="500" y2="128" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="280" y="150" font-size="14" font-weight="700" fill="var(--secondary)" text-anchor="middle">the name you invent</text>
    <text x="500" y="150" font-size="14" font-weight="700" fill="var(--secondary)" text-anchor="middle">the TLD you choose</text>
  </svg>
  </div>
  <figcaption><p>Every TLD has its own registry, its own price, and its own policy.</p></figcaption>
</figure>

### 2. Check whether it's free

First come, first served. If someone already holds it, that name is gone — look at another TLD or change the name.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 185" role="img" aria-label="A search returns which names are available and which are already taken">
    <rect x="30" y="16" width="660" height="50" rx="25" fill="none" stroke="var(--tertiary)" stroke-width="1.5"/>
    <circle cx="64" cy="41" r="9" fill="none" stroke="var(--secondary)" stroke-width="2"/>
    <line x1="71" y1="48" x2="78" y2="55" stroke="var(--secondary)" stroke-width="2" stroke-linecap="round"/>
    <text class="m" x="96" y="47" font-size="18" fill="currentColor">mystore</text>
    <polyline points="36,106 46,116 64,96" fill="none" stroke="var(--dgm-go)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    <text class="m" x="86" y="113" font-size="17" fill="currentColor">mystore.com</text>
    <text x="690" y="113" font-size="15" font-weight="700" fill="var(--dgm-go)" text-anchor="end">available</text>
    <line x1="37" y1="148" x2="56" y2="167" stroke="var(--dgm-stop)" stroke-width="3" stroke-linecap="round"/>
    <line x1="56" y1="148" x2="37" y2="167" stroke="var(--dgm-stop)" stroke-width="3" stroke-linecap="round"/>
    <text class="m" x="86" y="161" font-size="17" fill="var(--secondary)">mystore.io</text>
    <text x="690" y="161" font-size="15" font-weight="700" fill="var(--dgm-stop)" text-anchor="end">already taken</text>
  </svg>
  </div>
  <figcaption><p>Those results are a live query against the registry's ledger.</p></figcaption>
</figure>

### 3. Pay a year at the counter

You don't buy a domain, you **rent** it. Usually one year at a time, up to ten years prepaid.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 180" role="img" aria-label="A domain runs one year from registration, then a grace period, then deletion">
    <defs>
      <marker id="d5a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-accent)"/></marker>
    </defs>
    <path d="M520,84 C 520,26 40,26 40,78" fill="none" stroke="var(--dgm-accent)" stroke-width="2" marker-end="url(#d5a)"/>
    <text x="280" y="22" font-size="14" font-weight="700" fill="var(--dgm-accent)" text-anchor="middle">renew every year and it stays yours</text>
    <rect x="40" y="94" width="480" height="32" rx="6" fill="var(--dgm-accent)"/>
    <text x="280" y="116" font-size="14" font-weight="700" fill="#fff" text-anchor="middle">1 year of use</text>
    <rect x="524" y="94" width="120" height="32" rx="6" fill="none" stroke="var(--dgm-stop)" stroke-width="2" stroke-dasharray="5 4"/>
    <text x="584" y="116" font-size="13" font-weight="700" fill="var(--dgm-stop)" text-anchor="middle">30-day grace</text>
    <line x1="40" y1="132" x2="40" y2="144" stroke="var(--tertiary)" stroke-width="1.5"/>
    <line x1="520" y1="132" x2="520" y2="144" stroke="var(--tertiary)" stroke-width="1.5"/>
    <line x1="644" y1="132" x2="644" y2="144" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="40" y="164" font-size="13" fill="var(--secondary)">registered</text>
    <text x="520" y="164" font-size="13" fill="var(--secondary)" text-anchor="middle">expires</text>
    <text x="644" y="164" font-size="13" font-weight="700" fill="var(--dgm-stop)" text-anchor="middle">deleted</text>
  </svg>
  </div>
  <figcaption><p>After the grace period it is deleted and goes back on the market. Redemption before that is possible, but expensive.</p></figcaption>
</figure>

### 4. Verify the email

This confirms the registrant's contact is real. Paying isn't the end of it. **Miss the 15-day window and the domain gets suspended.**

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 175" role="img" aria-label="Clicking the link in the verification email activates the domain">
    <defs>
      <marker id="d6a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
    </defs>
    <rect x="40" y="42" width="150" height="86" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <polyline points="40,52 115,105 190,52" fill="none" stroke="var(--secondary)" stroke-width="2"/>
    <text x="115" y="152" font-size="13.5" fill="var(--secondary)" text-anchor="middle">verification email</text>
    <line x1="204" y1="85" x2="244" y2="85" stroke="currentColor" stroke-width="2" marker-end="url(#d6a)"/>
    <rect x="256" y="42" width="170" height="86" rx="10" fill="var(--dgm-accent)"/>
    <text x="341" y="92" font-size="17" font-weight="700" fill="#fff" text-anchor="middle">click the link</text>
    <text x="341" y="152" font-size="13.5" fill="var(--secondary)" text-anchor="middle">within 15 days</text>
    <line x1="440" y1="85" x2="480" y2="85" stroke="currentColor" stroke-width="2" marker-end="url(#d6a)"/>
    <rect x="492" y="42" width="188" height="86" rx="10" fill="none" stroke="var(--dgm-go)" stroke-width="2"/>
    <polyline points="556,86 570,100 624,62" fill="none" stroke="var(--dgm-go)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    <text x="586" y="152" font-size="13.5" font-weight="700" fill="var(--dgm-go)" text-anchor="middle">domain active</text>
  </svg>
  </div>
  <figcaption><p>ICANN requires this, not your registrar — which is why there is no way to skip it.</p></figcaption>
</figure>

### 5. Point it at your server

This is where you write "my server is over here" on the sign. Skip it and you own an address that opens nothing.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 185" role="img" aria-label="The domain points at a nameserver, and the nameserver answers with the server IP">
    <defs>
      <marker id="d7a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
    </defs>
    <rect x="20" y="56" width="205" height="82" rx="10" fill="var(--dgm-accent)"/>
    <text x="122" y="88" font-size="13" fill="rgba(255,255,255,.8)" text-anchor="middle">domain</text>
    <text class="m" x="122" y="114" font-size="16" fill="#fff" text-anchor="middle">mystore.com</text>
    <line x1="233" y1="97" x2="265" y2="97" stroke="currentColor" stroke-width="2" marker-end="url(#d7a)"/>
    <text x="249" y="44" font-size="13" font-weight="700" fill="var(--secondary)" text-anchor="middle">set NS</text>
    <rect x="273" y="56" width="205" height="82" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="375" y="88" font-size="13" fill="var(--secondary)" text-anchor="middle">nameserver</text>
    <text class="m" x="375" y="114" font-size="16" fill="currentColor" text-anchor="middle">ns1.host.com</text>
    <line x1="486" y1="97" x2="518" y2="97" stroke="currentColor" stroke-width="2" marker-end="url(#d7a)"/>
    <text x="502" y="44" font-size="13" font-weight="700" fill="var(--secondary)" text-anchor="middle">A record</text>
    <rect x="526" y="56" width="174" height="82" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="613" y="88" font-size="13" fill="var(--secondary)" text-anchor="middle">my server</text>
    <text class="m" x="613" y="114" font-size="16" fill="currentColor" text-anchor="middle">203.0.113.42</text>
    <text x="360" y="170" font-size="13.5" fill="var(--secondary)" text-anchor="middle">minutes to hours to propagate worldwide</text>
  </svg>
  </div>
  <figcaption><p>NS answers "who knows this domain"; the A record answers "and what is the answer".</p></figcaption>
</figure>

## How the address gets found

Once registration is done and someone types the name, a few queries fly back and forth in about a tenth of a second. Only the first time, though.

### The first time

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 596" role="img" aria-label="The browser asks a resolver whose cache is empty, so it walks the root server and the .com server to the authoritative nameserver, returns the IP to the browser, and stores that answer in its cache">
    <defs>
      <marker id="d8a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
      <marker id="d8b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-accent)"/></marker>
      <marker id="d8c" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-go)"/></marker>
    </defs>
    <rect x="190" y="14" width="330" height="66" rx="10" fill="var(--dgm-accent)"/>
    <text x="212" y="43" font-size="16.5" font-weight="700" fill="#fff">Browser</text>
    <text x="212" y="66" font-size="13" fill="rgba(255,255,255,.82)">opening&#160;<tspan class="m">mystore.com</tspan></text>
    <line x1="355" y1="80" x2="355" y2="118" stroke="currentColor" stroke-width="2" marker-end="url(#d8a)"/>
    <text x="370" y="104" font-size="12.5" fill="var(--secondary)">where is this name?</text>
    <rect x="190" y="118" width="330" height="94" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="212" y="147" font-size="16.5" font-weight="700" fill="currentColor">Resolver · the help desk</text>
    <text x="212" y="170" font-size="13" fill="var(--secondary)">your ISP or a public DNS asks for you</text>
    <text x="212" y="192" font-size="13" fill="var(--secondary)">it checks its own cache first</text>
    <line x1="520" y1="165" x2="538" y2="165" stroke="var(--tertiary)" stroke-width="1.5"/>
    <rect x="540" y="130" width="168" height="70" rx="10" fill="none" stroke="var(--tertiary)" stroke-width="1.5" stroke-dasharray="5 4"/>
    <text x="560" y="159" font-size="14" font-weight="700" fill="var(--secondary)">Cache</text>
    <text x="560" y="181" font-size="12.5" fill="var(--secondary)">empty right now</text>
    <line x1="355" y1="212" x2="355" y2="254" stroke="currentColor" stroke-width="2" marker-end="url(#d8a)"/>
    <text x="370" y="237" font-size="12.5" fill="var(--secondary)">query 1</text>
    <rect x="190" y="254" width="330" height="68" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="212" y="283" font-size="16.5" font-weight="700" fill="currentColor">Root server</text>
    <text x="212" y="306" font-size="13" fill="var(--secondary)">".com is handled over there"</text>
    <line x1="355" y1="322" x2="355" y2="364" stroke="currentColor" stroke-width="2" marker-end="url(#d8a)"/>
    <text x="370" y="347" font-size="12.5" fill="var(--secondary)">query 2</text>
    <rect x="190" y="364" width="330" height="68" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="212" y="393" font-size="16.5" font-weight="700" fill="currentColor">.com server · the registry</text>
    <text x="212" y="416" font-size="13" fill="var(--secondary)">nameserver is&#160;<tspan class="m">ns1.host.com</tspan></text>
    <line x1="355" y1="432" x2="355" y2="474" stroke="currentColor" stroke-width="2" marker-end="url(#d8a)"/>
    <text x="370" y="457" font-size="12.5" fill="var(--secondary)">query 3</text>
    <rect x="190" y="474" width="330" height="72" rx="10" fill="var(--code-bg)" stroke="var(--dgm-go)" stroke-width="2"/>
    <text x="212" y="503" font-size="16.5" font-weight="700" fill="currentColor">Authoritative nameserver</text>
    <text x="212" y="526" font-size="13" fill="var(--secondary)">the address is&#160;<tspan class="m">203.0.113.42</tspan></text>
    <path d="M190,516 L82,516 L82,48 L184,48" fill="none" stroke="var(--dgm-accent)" stroke-width="2" marker-end="url(#d8b)"/>
    <text x="66" y="282" font-size="12.5" font-weight="700" fill="var(--dgm-accent)" text-anchor="middle" transform="rotate(-90 66 282)">returns the IP → connect</text>
    <path d="M520,505 L628,505 L628,206" fill="none" stroke="var(--dgm-go)" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#d8c)"/>
    <text x="650" y="356" font-size="12.5" font-weight="700" fill="var(--dgm-go)" text-anchor="middle" transform="rotate(-90 650 356)">stores the answer for the TTL</text>
    <text x="190" y="576" font-size="13" fill="var(--secondary)">usually under 0.1s — and these queries happen only once.</text>
  </svg>
  </div>
  <figcaption><p>The root and .com servers do not know the answer. They only say "ask over there." One server at the bottom holds the real IP, and that answer lands in the cache on the way back.</p></figcaption>
</figure>

### After that, the cache answers

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 272" role="img" aria-label="The second request is answered straight from the resolver cache without visiting the root server, the .com server, or the authoritative nameserver">
    <defs>
      <marker id="d9a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
      <marker id="d9b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-go)"/></marker>
    </defs>
    <rect x="20" y="48" width="180" height="104" rx="10" fill="var(--dgm-accent)"/>
    <text x="110" y="92" font-size="16" font-weight="700" fill="#fff" text-anchor="middle">Browser</text>
    <text class="m" x="110" y="117" font-size="13" fill="rgba(255,255,255,.82)" text-anchor="middle">mystore.com</text>
    <line x1="208" y1="80" x2="462" y2="80" stroke="currentColor" stroke-width="2" marker-end="url(#d9a)"/>
    <text x="335" y="68" font-size="12.5" fill="var(--secondary)" text-anchor="middle">where is this name?</text>
    <line x1="462" y1="122" x2="208" y2="122" stroke="var(--dgm-go)" stroke-width="2" marker-end="url(#d9b)"/>
    <text x="335" y="143" font-size="12.5" font-weight="700" fill="var(--dgm-go)" text-anchor="middle">in cache → answered at once</text>
    <rect x="470" y="48" width="230" height="104" rx="10" fill="var(--code-bg)" stroke="var(--dgm-go)" stroke-width="2"/>
    <text x="585" y="82" font-size="16" font-weight="700" fill="currentColor" text-anchor="middle">Resolver</text>
    <text x="585" y="105" font-size="12.5" fill="var(--secondary)" text-anchor="middle">the answer is still cached</text>
    <text class="m" x="585" y="130" font-size="14" fill="var(--dgm-go)" text-anchor="middle">203.0.113.42</text>
    <text x="20" y="207" font-size="12.5" font-weight="700" fill="var(--secondary)">not visited this time</text>
    <rect x="190" y="182" width="150" height="40" rx="8" fill="none" stroke="var(--tertiary)" stroke-width="1.5" stroke-dasharray="5 4"/>
    <text x="265" y="207" font-size="13" fill="var(--secondary)" text-anchor="middle">Root server</text>
    <rect x="350" y="182" width="150" height="40" rx="8" fill="none" stroke="var(--tertiary)" stroke-width="1.5" stroke-dasharray="5 4"/>
    <text x="425" y="207" font-size="13" fill="var(--secondary)" text-anchor="middle">.com server</text>
    <rect x="510" y="182" width="190" height="40" rx="8" fill="none" stroke="var(--tertiary)" stroke-width="1.5" stroke-dasharray="5 4"/>
    <text x="605" y="207" font-size="13" fill="var(--secondary)" text-anchor="middle">Authoritative NS</text>
    <text x="20" y="254" font-size="13" fill="var(--secondary)">When the TTL runs out the entry is dropped, and the next request asks all three again.</text>
  </svg>
  </div>
  <figcaption><p>Zero queries. Most real traffic looks like this — which is also why a DNS change does not show up right away.</p></figcaption>
</figure>

### What the authoritative nameserver actually does

The name says it: it is the server that holds the **authoritative** answer for this name. That is what separates it from the two servers above it.

The root server and the .com server do not know the IP of `mystore.com`. They only **hand you off** — ".com is over there," "that domain is known by `ns1.host.com`." One server at the bottom actually stores the records and produces the final answer. It is the server you pointed the NS records at back in step 5, and it is usually run for you by the registrar, the hosting provider, or a DNS service like Cloudflare.

What it holds is exactly the set of records you edit in a domain control panel.

- `A` / `AAAA` — the IP address for this name (IPv4 / IPv6)
- `CNAME` — "this name is the same as that name"
- `MX` — the server that receives mail for this domain
- `TXT` — notes such as ownership proofs and mail authentication (SPF, DKIM)

Strictly speaking, the root server is the authoritative nameserver for the root zone, and the .com server is the authoritative nameserver for the .com zone. Each one is authoritative for its own layer. But the final answer for the name you asked about lives in exactly one place at the bottom, and that is the one people usually mean.

What a resolver hands you out of its cache is a copy, not the original. With `dig` you can tell them apart by the `aa` (authoritative answer) flag in the response header.

```
$ dig mystore.com                   # asking the resolver
;; flags: qr rd ra;                 ← no aa = a copy from the cache

$ dig @ns1.host.com mystore.com     # asking the authoritative nameserver directly
;; flags: qr aa rd;                 ← aa = the original
```

This is also the place that actually changes when you edit a record. The original flips immediately, but resolver caches around the world keep the old answer for as long as the TTL says. That is why an edit is not visible right away — and why, when a server move is coming, the trick is to drop the TTL to something like 300 seconds a few days ahead.

## Three things worth remembering

Registration itself rarely goes wrong. These three do.

- **You rent it, you don't own it.** Registration grants a right to use, not ownership. Stop renewing and someone else can take it.
- **Turn on auto-renew.** Roughly 30 days of grace after expiry, then a steep redemption fee, then deletion back onto the market. Set the expiry reminder the day you register.
- **You can hide your details.** The registrant's name, address, and phone go into WHOIS. Most registrars offer privacy protection for free.

## The practical follow-up

That is the concept. Actually buying `byeorim.com` and wiring a page to it, **the order turned out different and things showed up that none of these diagrams mention.**

- **"No such address" gets cached too.** Look the domain up before you have finished setting it up, and that "no" sits in your resolver for about half an hour. It is the most common cause of "I definitely configured this, so why isn't it working."
- **An apex domain (`byeorim.com` — the root, with no subdomain) cannot have a CNAME.** That is why GitHub Pages tells you to hard-code four fixed IPs.
- **DNSSEC was listed as included, and was switched off.**

→ [Buying a Domain and Wiring Up a Page, For Real](/en/posts/buying-a-domain-in-practice/) — ninety minutes and $10.46 a year, written down.

---

The `mystore.com` and `203.0.113.42` above are illustrative. The `203.0.113.0/24` block is reserved for documentation by [RFC 5737](https://datatracker.ietf.org/doc/html/rfc5737).
