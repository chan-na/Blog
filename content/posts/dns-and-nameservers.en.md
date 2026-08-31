---
title: "DNS and Nameservers, in Pictures"
date: 2026-09-01T00:46:19+09:00
draft: false
slug: "dns-and-nameservers"
translationKey: "dns-and-nameservers"
categories: ["Engineering"]
tags: ["dns", "nameserver", "networking", "intro"]
summary: "One name, 'DNS server', covers two jobs that point in opposite directions. The asking side and the answering side, zones and delegation, the NS record that lives in both parent and child, caching and TTL, all pulled apart in nine pictures."
---

<style>
.dgm { --dgm-accent: #14468C; --dgm-go: #1B7A54; --dgm-stop: #A8402A; margin: 0 0 var(--content-gap); }
:root[data-theme="dark"] .dgm { --dgm-accent: #2E6BC4; --dgm-go: #4FBE90; --dgm-stop: #E5876A; }
.dgm .dgm-scroll { overflow-x: auto; }
.dgm svg { display: block; width: 100%; height: auto; color: var(--content); }
.dgm svg text { font-family: inherit; }
.dgm svg .m { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
</style>

The last two posts each brushed past a "resolver" and an "authoritative nameserver," one apiece. [How a Domain Gets Registered, in Pictures](/en/posts/how-domains-get-registered/) had them as a picture of three questions going back and forth, and as the `aa` flag that `dig` spits out; [Buying a Domain and Wiring Up a Page, For Real](/en/posts/buying-a-domain-in-practice/) had them in the stretch where `dig` worked and `curl` didn't.

The trouble is that the names overlap. Read the two sentences below and you can't tell which one each is talking about, a resolver or an authoritative nameserver.

- "Try switching your DNS server to `8.8.8.8`."
- "You need to change your nameservers to Cloudflare."

The `8.8.8.8` in the first is a resolver, the side I send my questions to; the nameservers in the second are authoritative nameservers, the side the world asks about my domain. Both are about DNS, but **they point at opposite things.** This post starts by pulling the two apart.

## One name, two different jobs

There is no single thing called a DNS server. There are two kinds that share a name and do completely different work.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 344" role="img" aria-label="A resolver holds no originals — it answers from a cached copy or goes and finds out for you; an authoritative nameserver keeps the original and answers only for its own">
    <rect x="16" y="12" width="330" height="282" rx="12" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="40" y="52" font-size="18" font-weight="700" fill="currentColor">Resolver</text>
    <text x="40" y="76" font-size="13" fill="var(--secondary)">the asking side · handles my question for me</text>
    <line x1="40" y1="92" x2="322" y2="92" stroke="var(--tertiary)" stroke-width="1" opacity="0.6"/>
    <text x="40" y="124" font-size="13.5" fill="currentColor">Holds no originals</text>
    <text x="40" y="156" font-size="13.5" fill="currentColor">Answers from cache if it has a copy</text>
    <text x="40" y="188" font-size="13.5" fill="currentColor">If not, it goes and finds out for you</text>
    <text x="40" y="220" font-size="13.5" fill="currentColor">You pick it, in your own settings</text>
    <text class="m" x="40" y="266" font-size="13" fill="var(--secondary)">1.1.1.1 · 8.8.8.8 · your ISP</text>
    <rect x="374" y="12" width="330" height="282" rx="12" fill="var(--dgm-accent)"/>
    <text x="398" y="52" font-size="18" font-weight="700" fill="#fff">Authoritative Nameserver</text>
    <text x="398" y="76" font-size="13" fill="rgba(255,255,255,.82)">the answering side · keeps the final answer</text>
    <line x1="398" y1="92" x2="680" y2="92" stroke="rgba(255,255,255,.35)" stroke-width="1"/>
    <text x="398" y="124" font-size="13.5" fill="#fff">Holds the original</text>
    <text x="398" y="156" font-size="13.5" fill="#fff">Won't go looking. Answers only for its own</text>
    <text x="398" y="188" font-size="13.5" fill="#fff">It's the original, so no cache</text>
    <text x="398" y="220" font-size="13.5" fill="#fff">The domain owner sets it</text>
    <text class="m" x="398" y="266" font-size="13" fill="rgba(255,255,255,.82)">david.ns.cloudflare.com</text>
    <text x="16" y="330" font-size="13.5" fill="var(--secondary)">"Change your DNS server" and "change your nameservers" are opposite sides.</text>
  </svg>
  </div>
  <figcaption><p>The <strong>resolver</strong> is who I ask; the <strong>authoritative nameserver</strong> is who the world asks about my domain.</p></figcaption>
</figure>

Which means you fix them in different places. You change a resolver in your laptop's network settings, and only you are affected. You change an authoritative nameserver in your domain's control panel, and the whole world is affected.

You already saw how to tell them apart in [How a Domain Gets Registered, in Pictures](/en/posts/how-domains-get-registered/). If the `;; flags:` line of a `dig` response carries `aa` (authoritative answer), the original answered it directly; if not, it's a copy pulled out of a resolver's cache.

## A DNS query passes through four layers

But the resolver isn't a single layer either. There's a smaller resolver inside your own computer.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 452" role="img" aria-label="A DNS query passes in turn through four layers: the browser, the OS stub resolver, the recursive resolver, and the authoritative nameserver">
    <defs>
      <marker id="n2a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
      <marker id="n2b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-go)"/></marker>
    </defs>
    <path d="M112,20 L96,20 L96,196 L112,196" fill="none" stroke="var(--dgm-accent)" stroke-width="2"/>
    <text x="80" y="108" font-size="12.5" font-weight="700" fill="var(--dgm-accent)" text-anchor="middle" transform="rotate(-90 80 108)">Inside my computer</text>
    <rect x="118" y="14" width="392" height="76" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="142" y="46" font-size="16" font-weight="700" fill="currentColor">Browser</text>
    <text x="142" y="70" font-size="12.5" fill="var(--secondary)">Keeps a DNS cache of its own</text>
    <line x1="314" y1="90" x2="314" y2="116" stroke="currentColor" stroke-width="2" marker-end="url(#n2a)"/>
    <rect x="118" y="120" width="392" height="76" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="142" y="152" font-size="16" font-weight="700" fill="currentColor">Stub resolver · OS</text>
    <text x="142" y="176" font-size="12.5" fill="var(--secondary)">Doesn't search. Checks its cache, then passes it on</text>
    <line x1="314" y1="196" x2="314" y2="222" stroke="currentColor" stroke-width="2" marker-end="url(#n2a)"/>
    <rect x="118" y="226" width="392" height="76" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="142" y="258" font-size="16" font-weight="700" fill="currentColor">Recursive resolver</text>
    <text x="142" y="282" font-size="12.5" fill="var(--secondary)">The real searching starts here</text>
    <line x1="314" y1="302" x2="314" y2="328" stroke="currentColor" stroke-width="2" marker-end="url(#n2a)"/>
    <rect x="118" y="332" width="392" height="76" rx="10" fill="var(--dgm-accent)"/>
    <text x="142" y="364" font-size="16" font-weight="700" fill="#fff">Authoritative NS</text>
    <text x="142" y="388" font-size="12.5" fill="rgba(255,255,255,.82)">The original lives here</text>
    <path d="M600,40 L600,264 L518,264" fill="none" stroke="var(--dgm-go)" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#n2b)"/>
    <text class="m" x="600" y="28" font-size="14" font-weight="700" fill="var(--dgm-go)" text-anchor="middle">dig</text>
    <text x="624" y="152" font-size="12.5" font-weight="700" fill="var(--dgm-go)" text-anchor="middle" transform="rotate(-90 624 152)">skips the two layers above</text>
    <text x="16" y="440" font-size="13.5" fill="var(--secondary)">Every layer has its own cache. Flushing one still leaves the others holding the old answer.</text>
  </svg>
  </div>
  <figcaption><p>A stub is a stump. A stub resolver has the looking-up part cut away: it checks its cache, hands the query to a recursive resolver if the cache comes up empty, and passes the answer back to the program.</p></figcaption>
</figure>

The thing that held me up longest in [Buying a Domain and Wiring Up a Page, For Real](/en/posts/buying-a-domain-in-practice/) is exactly this picture. On the same machine at the same moment, `dig byeorim.com A` returned the IPs just fine while `curl https://byeorim.com` died with `Could not resolve host`. `dig` fires DNS packets straight at the recursive resolver; `curl` goes through `getaddrinfo()` to ask the OS, and on macOS that request lands in `mDNSResponder`, which checks its own cache first. `dig` and `curl` ask different layers, and every layer keeps its own cache. While one layer's cache still holds an old, unexpired response, every path through that layer keeps getting the old response back. What `mDNSResponder` had cached that day was "no A record," and `dig` skipped that cache entirely — which is how one name produced two different answers.

## Zones: the territory a nameserver answers for

The unit an authoritative nameserver holds the original of, and answers for, is not a single domain but a **zone**. One zone contains many names, and the nameserver answers for every name in it.

A domain name is a hierarchy split by dots. Draw that hierarchy as a tree, and the right-hand end of the domain is the top of the tree. `www.byeorim.com` actually has one more dot at the very end: `www.byeorim.com.` That last dot is the root.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 402" role="img" aria-label="Each piece the dashed lines cut out of the name tree descending from root through .com to byeorim.com is a zone">
    <rect x="296" y="4" width="128" height="64" rx="10" fill="none" stroke="var(--dgm-accent)" stroke-width="1.5" stroke-dasharray="5 4"/>
    <rect x="310" y="14" width="100" height="44" rx="8" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text class="m" x="360" y="44" font-size="20" fill="currentColor" text-anchor="middle">.</text>
    <text x="436" y="40" font-size="12.5" font-weight="700" fill="var(--dgm-accent)">root zone</text>
    <line x1="360" y1="68" x2="250" y2="106" stroke="var(--tertiary)" stroke-width="1.5"/>
    <line x1="360" y1="68" x2="490" y2="106" stroke="var(--tertiary)" stroke-width="1.5"/>
    <rect x="181" y="100" width="138" height="64" rx="10" fill="none" stroke="var(--dgm-accent)" stroke-width="1.5" stroke-dasharray="5 4"/>
    <rect x="195" y="110" width="110" height="44" rx="8" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text class="m" x="250" y="139" font-size="15" fill="currentColor" text-anchor="middle">.com</text>
    <text x="172" y="136" font-size="12.5" font-weight="700" fill="var(--dgm-accent)" text-anchor="end">.com zone</text>
    <rect x="421" y="100" width="138" height="64" rx="10" fill="none" stroke="var(--dgm-accent)" stroke-width="1.5" stroke-dasharray="5 4"/>
    <rect x="435" y="110" width="110" height="44" rx="8" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text class="m" x="490" y="139" font-size="15" fill="currentColor" text-anchor="middle">.kr</text>
    <text x="568" y="136" font-size="12.5" font-weight="700" fill="var(--dgm-accent)">.kr zone</text>
    <line x1="250" y1="164" x2="180" y2="212" stroke="var(--tertiary)" stroke-width="1.5"/>
    <line x1="250" y1="164" x2="400" y2="212" stroke="var(--tertiary)" stroke-width="1.5"/>
    <rect x="72" y="206" width="202" height="142" rx="12" fill="none" stroke="var(--dgm-accent)" stroke-width="1.5" stroke-dasharray="5 4"/>
    <rect x="105" y="216" width="150" height="44" rx="8" fill="var(--dgm-accent)"/>
    <text class="m" x="180" y="245" font-size="14" fill="#fff" text-anchor="middle">byeorim.com</text>
    <rect x="325" y="216" width="150" height="44" rx="8" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text class="m" x="400" y="245" font-size="14" fill="var(--secondary)" text-anchor="middle">example.com</text>
    <line x1="180" y1="260" x2="128" y2="298" stroke="var(--tertiary)" stroke-width="1.5"/>
    <line x1="180" y1="260" x2="222" y2="298" stroke="var(--tertiary)" stroke-width="1.5"/>
    <rect x="85" y="300" width="85" height="40" rx="8" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text class="m" x="128" y="326" font-size="13" fill="currentColor" text-anchor="middle">www</text>
    <rect x="180" y="300" width="85" height="40" rx="8" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text class="m" x="222" y="326" font-size="13" fill="currentColor" text-anchor="middle">blog</text>
    <text x="292" y="288" font-size="12.5" font-weight="700" fill="var(--dgm-accent)">byeorim.com zone</text>
    <text x="292" y="310" font-size="12.5" fill="var(--secondary)">subdomains usually sit</text>
    <text x="292" y="330" font-size="12.5" fill="var(--secondary)">inside the same zone</text>
    <text x="16" y="386" font-size="13.5" fill="var(--secondary)">A zone isn't a domain but "one chunk a single administrator answers for."</text>
  </svg>
  </div>
  <figcaption><p>Each piece the dotted lines cut out of the tree is a zone, and each has its own nameservers.</p></figcaption>
</figure>

Here is where it forks. **A domain and a zone are not the same thing.** `blog.byeorim.com` normally just sits inside the `byeorim.com` zone as a record, but you can cut it out into its own zone and hand it to a different nameserver if you want. That's how a company gives each team its own subdomain.

## Delegation: the NS record exists in two copies

The parent zone telling the child zone "everything under here is yours to answer" is **delegation**, and the record that names the nameservers the answering is handed to is the **NS record**.

The catch is that the same NS record sits in both the parent and the child. It looks redundant at first, but the two have completely different character.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 378" role="img" aria-label="The parent zone's NS record carries no authority and the child zone's does, but what resolvers actually follow is the parent's">
    <defs>
      <marker id="n4a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-go)"/></marker>
    </defs>
    <rect x="16" y="36" width="336" height="256" rx="12" fill="var(--dgm-accent)"/>
    <text x="40" y="70" font-size="17" font-weight="700" fill="#fff">.com zone · parent</text>
    <text x="40" y="92" font-size="12.5" fill="rgba(255,255,255,.82)">Held by Verisign</text>
    <line x1="40" y1="106" x2="328" y2="106" stroke="rgba(255,255,255,.35)" stroke-width="1"/>
    <text class="m" x="40" y="134" font-size="12" fill="rgba(255,255,255,.9)">byeorim.com NS david.ns…</text>
    <text x="40" y="164" font-size="13" fill="#fff">AUTHORITY section · no aa</text>
    <text x="40" y="192" font-size="13" fill="#fff">TTL 172800 = 2 days</text>
    <text x="40" y="224" font-size="14.5" font-weight="700" fill="#fff">Not an answer — the server to ask next</text>
    <text x="40" y="264" font-size="12.5" fill="rgba(255,255,255,.82)">Edit this NS record in: the registrar's panel</text>
    <rect x="368" y="36" width="336" height="256" rx="12" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="392" y="70" font-size="17" font-weight="700" fill="currentColor">byeorim.com zone · child</text>
    <text x="392" y="92" font-size="12.5" fill="var(--secondary)">Held by Cloudflare</text>
    <line x1="392" y1="106" x2="680" y2="106" stroke="var(--tertiary)" stroke-width="1" opacity="0.6"/>
    <text class="m" x="392" y="134" font-size="12" fill="currentColor">byeorim.com NS david.ns…</text>
    <text x="392" y="164" font-size="13" fill="currentColor">ANSWER section · aa set</text>
    <text x="392" y="192" font-size="13" fill="currentColor">TTL 86400 = 1 day</text>
    <text x="392" y="224" font-size="14.5" font-weight="700" fill="currentColor">An answer with authority over this zone</text>
    <text x="392" y="264" font-size="12.5" fill="var(--secondary)">Edit this NS record in: the DNS panel</text>
    <path d="M184,16 L184,30" fill="none" stroke="var(--dgm-go)" stroke-width="2" marker-end="url(#n4a)"/>
    <text x="204" y="24" font-size="12.5" font-weight="700" fill="var(--dgm-go)">resolvers come down from above, and only read this side</text>
    <text x="16" y="336" font-size="13.5" fill="var(--secondary)">The NS values for byeorim.com are identical in parent and child; the place, TTL and authority are not.</text>
    <text x="16" y="358" font-size="13.5" fill="var(--secondary)">And the copy that decides which nameserver the query goes to is the one on the left.</text>
  </svg>
  </div>
  <figcaption><p>Authority to answer for byeorim.com sits on the right, but of the two NS records written down, the one actually used is the copy on the left, in the parent zone.</p></figcaption>
</figure>

Ask both sides directly and the difference shows up plainly.

```
$ dig @a.gtld-servers.net byeorim.com NS        # to the parent .com
;; flags: qr rd;                                ← no aa
;; AUTHORITY SECTION:
byeorim.com.  172800  IN  NS  david.ns.cloudflare.com.
byeorim.com.  172800  IN  NS  kami.ns.cloudflare.com.

$ dig @david.ns.cloudflare.com byeorim.com NS   # to the child zone
;; flags: qr aa rd;                             ← aa present
;; ANSWER SECTION:
byeorim.com.  86400   IN  NS  david.ns.cloudflare.com.
byeorim.com.  86400   IN  NS  kami.ns.cloudflare.com.
```

The values match to the letter. Three things differ.

- **The section.** The parent replies in `AUTHORITY` (the server to ask next), the child in `ANSWER` (the answer).
- **The `aa` flag.** The parent doesn't have it. The `.com` servers hold no authority over `byeorim.com`.
- **The TTL.** Two days from the parent, one day from the child. Different people set them, so there's no reason they'd match.

And this is where the conclusion falls out. **Resolvers always come down from the zone above, so they read the parent zone's NS record and send their next query to the server named there.** The NS records written in the child zone are almost never read in practice. That's why changing your nameservers happens in your **registrar's** panel and not your DNS panel. The parent zone has to change, only the registry can write the parent zone, and the only one who can file that request with the registry is your registrar.

The state where the two disagree is called a **lame delegation**: the parent zone's NS record points at nameserver A, but A has no data for that zone and so cannot answer for it with authority. When several nameservers are listed, only the queries where the resolver happens to pick A fail — which is where the nasty symptom of a domain working only intermittently comes from.

## Glue: why the parent hands over the nameserver's IP too

When a nameserver's name sits inside the very domain it answers for, the delegation turns into a loop. `google.com`, whose nameserver is named `ns1.google.com`, is exactly that case.

Walk it through as the resolver. The `.com` servers say "for `google.com`, go ask `ns1.google.com`." To send a query to that server, you need the IP of `ns1.google.com`. To get the IP, you have to look up the A record for `ns1.google.com` — and that A record lives inside the `google.com` zone. The server that can answer for the `google.com` zone is, once again, `ns1.google.com`. **You would need the answer to the query before you could send it**, so the resolver cannot take a single step.

The parent zone breaks the loop. Along with the delegation, the `.com` servers ship the IP of `ns1.google.com` in the `ADDITIONAL` section of the response. That tagged-along IP is the **glue record**. The resolver skips the A lookup entirely and queries that address directly.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 336" role="img" aria-label="A nameserver named inside its own domain creates a loop where the address cannot be resolved, and the glue record, in which the parent supplies that address, breaks it">
    <defs>
      <marker id="n5a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-stop)"/></marker>
    </defs>
    <text x="16" y="28" font-size="13" font-weight="700" fill="var(--secondary)">① the loop</text>
    <rect x="30" y="40" width="290" height="72" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text class="m" x="175" y="74" font-size="13.5" fill="currentColor" text-anchor="middle">ns1.google.com</text>
    <text x="175" y="96" font-size="12.5" fill="var(--secondary)" text-anchor="middle">to query this,</text>
    <line x1="326" y1="76" x2="396" y2="76" stroke="var(--dgm-stop)" stroke-width="2" marker-end="url(#n5a)"/>
    <rect x="402" y="40" width="290" height="72" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="547" y="74" font-size="13.5" fill="currentColor" text-anchor="middle">you need that name's IP</text>
    <text x="547" y="96" font-size="12.5" fill="var(--secondary)" text-anchor="middle">before you can ask</text>
    <path d="M547,116 C547,152 175,152 175,118" fill="none" stroke="var(--dgm-stop)" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#n5a)"/>
    <text x="360" y="176" font-size="13" font-weight="700" fill="var(--dgm-stop)" text-anchor="middle">but that IP lives inside the google.com zone</text>
    <text x="16" y="216" font-size="13" font-weight="700" fill="var(--secondary)">② glue</text>
    <rect x="30" y="228" width="662" height="66" rx="10" fill="var(--dgm-accent)"/>
    <text x="54" y="256" font-size="15" font-weight="700" fill="#fff">the parent hands over that IP along with the delegation</text>
    <text x="54" y="280" font-size="12.5" fill="rgba(255,255,255,.82)">the adhesive stuck to the delegation, a glue record</text>
    <text x="16" y="326" font-size="13.5" fill="var(--secondary)">Name a nameserver inside your own domain and glue is mandatory; inside someone else's, it isn't.</text>
  </svg>
  </div>
  <figcaption><p>A glue record is stored in the parent zone, not the child. Which means changing that IP also happens in the registrar's panel.</p></figcaption>
</figure>

And that is exactly what the `.com` servers hand back.

```
$ dig @a.gtld-servers.net google.com NS
;; AUTHORITY SECTION:
google.com.      172800  IN  NS  ns1.google.com.
google.com.      172800  IN  NS  ns2.google.com.
;; ADDITIONAL SECTION:
ns1.google.com.  172800  IN  A   216.239.32.10      ← glue
ns2.google.com.  172800  IN  A   216.239.34.10
```

`byeorim.com` doesn't have this problem. Its nameservers are named `david.ns.cloudflare.com`, **inside someone else's domain**, so no loop forms. The resolver just does one extra lookup for `cloudflare.com` and moves on.

That's also why services like Cloudflare and Gabia lend you nameservers under their own domain. No loop, so no glue to manage.

## Following a single query all the way down

`dig +trace` skips the resolver: **`dig` itself walks down from the root, one step at a time.** It shows you what your resolver normally does on your behalf.

```
$ dig +trace byeorim.com A

.             389730  IN  NS  a.root-servers.net.  …          ← the root list first
;; Received 1109 bytes from 168.126.63.1#53 in 6 ms

com.          172800  IN  NS  a.gtld-servers.net.  …          ← ".com is over there"
;; Received 1171 bytes from 192.33.4.12#53(c.root-servers.net) in 133 ms

byeorim.com.  172800  IN  NS  david.ns.cloudflare.com.        ← "that domain is over there"
byeorim.com.  172800  IN  NS  kami.ns.cloudflare.com.
;; Received 504 bytes from 192.12.94.30#53(e.gtld-servers.net) in 38 ms

byeorim.com.  300     IN  A   104.21.81.254                   ← the answer, at last
byeorim.com.  300     IN  A   172.67.192.105
;; Received 179 bytes from 173.245.58.177#53(kami.ns.cloudflare.com) in 7 ms
```

That each of the four chunks came from a different server is stamped right there in the `Received … from` lines. And the first three chunks **are not answers.** They say "I don't know, go ask over there," which is called a **referral**.

Two things are worth noticing as you read it.

The root server list on the first line came from `168.126.63.1`, my ISP's resolver. Even `dig` has to get its starting point from somewhere. And only the final answer has a TTL of `300`. Delegation data lasts days; the actual address lasts five minutes. That gap is the subject of the next section.

## The cache holds more than the final answer

What a resolver caches isn't one line of `byeorim.com → IP`. **It keeps every referral it picked up on the way down.**

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 330" role="img" aria-label="A resolver cache holds the root NS, the .com NS, the byeorim.com NS and the final A record, each with its own lifetime">
    <defs>
      <marker id="n6a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-stop)"/></marker>
    </defs>
    <rect x="16" y="40" width="400" height="238" rx="12" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="40" y="74" font-size="16" font-weight="700" fill="currentColor">Resolver cache</text>
    <line x1="40" y1="90" x2="392" y2="90" stroke="var(--tertiary)" stroke-width="1" opacity="0.6"/>
    <text class="m" x="40" y="122" font-size="13" fill="var(--secondary)">. NS</text>
    <text x="392" y="122" font-size="13" fill="var(--secondary)" text-anchor="end">6 days</text>
    <text class="m" x="40" y="160" font-size="13" fill="var(--secondary)">com. NS</text>
    <text x="392" y="160" font-size="13" fill="var(--secondary)" text-anchor="end">2 days</text>
    <text class="m" x="40" y="198" font-size="13" fill="var(--secondary)">byeorim.com NS</text>
    <text x="392" y="198" font-size="13" fill="var(--secondary)" text-anchor="end">2 days</text>
    <line x1="40" y1="216" x2="392" y2="216" stroke="var(--tertiary)" stroke-width="1" opacity="0.6"/>
    <text class="m" x="40" y="248" font-size="13" font-weight="700" fill="var(--dgm-stop)">byeorim.com A</text>
    <text x="392" y="248" font-size="13" font-weight="700" fill="var(--dgm-stop)" text-anchor="end">5 min</text>
    <path d="M424,110 L440,110 L440,200 L424,200" fill="none" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="460" y="146" font-size="13" fill="currentColor">while these three are alive</text>
    <text x="460" y="170" font-size="13" font-weight="700" fill="currentColor">no going back to root or .com</text>
    <line x1="420" y1="243" x2="452" y2="243" stroke="var(--dgm-stop)" stroke-width="2" marker-end="url(#n6a)"/>
    <text x="462" y="240" font-size="13" font-weight="700" fill="var(--dgm-stop)">only this one expires every 5 min</text>
    <text x="462" y="262" font-size="12.5" fill="var(--secondary)">→ usually only the last hop goes out</text>
    <text x="16" y="312" font-size="13.5" fill="var(--secondary)">The "three questions" picture almost never happens in practice.</text>
  </svg>
  </div>
  <figcaption><p>NS records have TTLs measured in days, so they stay in the cache a long time. The only entry that expires often enough to be fetched again is the A record, with its 300-second TTL.</p></figcaption>
</figure>

You can peek into the cache. `+norecurse` means **"don't go looking, just hand over what you have right now."**

```
$ dig +norecurse @168.126.63.1 com. NS      # my ISP resolver's cache
com.  44878   IN  NS  d.gtld-servers.net.

$ dig @a.gtld-servers.net com. NS           # the original
com.  172800  IN  NS  m.gtld-servers.net.
```

The original is 172800 seconds (two days), but only 44878 are left on my resolver. The subtraction is the age: **a copy taken about 35 hours ago.**

Ask again twelve seconds later:

```
com.  44866   IN  NS  h.gtld-servers.net.
```

Down by exactly twelve. **A TTL is a counter ticking down the remaining lifetime in real time, not a fixed setting.** If the number in a response is some odd value instead of 300, it came from a cache.

## A changed record does not spread. Resolver caches simply expire

People say a change to your domain's DNS "takes 48 hours to propagate." But during those 48 hours **the authoritative nameserver sends nothing to anyone.**

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 322" role="img" aria-label="The authoritative nameserver does not push the change out; each resolver's cache expires on its own schedule and comes back to ask again">
    <defs>
      <marker id="n7a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-stop)"/></marker>
      <marker id="n7b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-go)"/></marker>
    </defs>
    <line x1="360" y1="10" x2="360" y2="270" stroke="var(--tertiary)" stroke-width="1" stroke-dasharray="4 4"/>
    <text x="176" y="26" font-size="14" font-weight="700" fill="var(--dgm-stop)" text-anchor="middle">What we imagine</text>
    <text x="540" y="26" font-size="14" font-weight="700" fill="var(--dgm-go)" text-anchor="middle">What actually happens</text>
    <rect x="56" y="46" width="240" height="48" rx="8" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="176" y="76" font-size="13.5" fill="currentColor" text-anchor="middle">Authoritative NS</text>
    <line x1="176" y1="94" x2="76" y2="196" stroke="var(--dgm-stop)" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#n7a)"/>
    <line x1="176" y1="94" x2="176" y2="196" stroke="var(--dgm-stop)" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#n7a)"/>
    <line x1="176" y1="94" x2="276" y2="196" stroke="var(--dgm-stop)" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#n7a)"/>
    <line x1="40" y1="146" x2="312" y2="146" stroke="var(--dgm-stop)" stroke-width="2"/>
    <line x1="160" y1="130" x2="192" y2="162" stroke="var(--dgm-stop)" stroke-width="3.5" stroke-linecap="round"/>
    <line x1="192" y1="130" x2="160" y2="162" stroke="var(--dgm-stop)" stroke-width="3.5" stroke-linecap="round"/>
    <rect x="36" y="200" width="80" height="40" rx="8" fill="none" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="76" y="225" font-size="12" fill="var(--secondary)" text-anchor="middle">Resolver A</text>
    <rect x="136" y="200" width="80" height="40" rx="8" fill="none" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="176" y="225" font-size="12" fill="var(--secondary)" text-anchor="middle">Resolver B</text>
    <rect x="236" y="200" width="80" height="40" rx="8" fill="none" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="276" y="225" font-size="12" fill="var(--secondary)" text-anchor="middle">Resolver C</text>
    <text x="176" y="264" font-size="12.5" font-weight="700" fill="var(--dgm-stop)" text-anchor="middle">the authoritative nameserver pushes nothing</text>
    <rect x="392" y="46" width="86" height="44" rx="8" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="435" y="73" font-size="12.5" fill="currentColor" text-anchor="middle">Resolver A</text>
    <rect x="496" y="46" width="86" height="44" rx="8" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="539" y="73" font-size="12.5" fill="currentColor" text-anchor="middle">Resolver B</text>
    <rect x="600" y="46" width="86" height="44" rx="8" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="643" y="73" font-size="12.5" fill="currentColor" text-anchor="middle">Resolver C</text>
    <text x="435" y="110" font-size="12" fill="var(--secondary)" text-anchor="middle">expires in 5 min</text>
    <text x="539" y="110" font-size="12" fill="var(--secondary)" text-anchor="middle">1 hour later</text>
    <text x="643" y="110" font-size="12" fill="var(--secondary)" text-anchor="middle">2 days later</text>
    <line x1="435" y1="120" x2="500" y2="192" stroke="var(--dgm-go)" stroke-width="2" marker-end="url(#n7b)"/>
    <line x1="539" y1="120" x2="539" y2="192" stroke="var(--dgm-go)" stroke-width="2" marker-end="url(#n7b)"/>
    <line x1="643" y1="120" x2="578" y2="192" stroke="var(--dgm-go)" stroke-width="2" marker-end="url(#n7b)"/>
    <rect x="420" y="196" width="240" height="48" rx="8" fill="var(--dgm-accent)"/>
    <text x="540" y="226" font-size="13.5" font-weight="700" fill="#fff" text-anchor="middle">Authoritative NS</text>
    <text x="540" y="264" font-size="12.5" font-weight="700" fill="var(--dgm-go)" text-anchor="middle">each comes back to ask when its own copy expires</text>
    <text x="16" y="302" font-size="13.5" fill="var(--secondary)">"48 hours to propagate" is really the parent NS record's TTL of 172800 seconds.</text>
  </svg>
  </div>
  <figcaption><p>It's expiry, not propagation. The arrow points the other way.</p></figcaption>
</figure>

The original changes the moment you save it. Resolvers around the world come back to ask again on their own, each when its own copy expires. The expiry times are all over the place, so **at any given moment one person sees the new answer and another still sees the old one.**

So the maximum delay is the TTL of the record you changed. Change the A record for `byeorim.com` and that is its 300-second TTL; change the domain's nameservers themselves and it is the TTL of the NS record written in the parent zone, 172800 seconds, or two days. The "48 hours" figure of speech comes from the second one.

An A record is no different. The moment you save the new IP, the authoritative nameserver's answer changes — but **visitors never ask the authoritative nameserver directly.** They ask their own resolver, which is already holding a copy of the old IP, and until that copy expires it has no reason to ask again, so it keeps sending them to the old server. If the TTL was 86400 seconds — a day — then for up to a day some visitors land on the new server and some on the old one.

The trick was in [How a Domain Gets Registered, in Pictures](/en/posts/how-domains-get-registered/) too, but the reason for it is clear here. **If you know a server move is coming, drop that A record's TTL to 300 seconds a few days ahead.** Then, at the moment you switch, every copy out in the world has five minutes or less left on it, and five minutes after the change it is over. The reason it has to be *days* ahead is that the TTL value travels with the record: a resolver holding the old 86400-second copy only learns about the new value of 300 when it asks again a day later. Drop it on moving day and those resolvers are still running on the old TTL.

What you can lower ahead of time, though, is only **the TTL of records inside your own zone** — the ones whose values you set in your DNS panel, like an A record. **The TTL on the NS record in the parent zone is set by the registry, and the domain owner cannot change it**; for `.com` it is fixed at 172800 seconds. The child zone has NS records too, and you do control their TTL, but resolvers follow the parent's copy, so it buys you nothing. Which means a full nameserver change is the one case you cannot shorten in advance. You leave the old nameservers answering with the same records and wait out the two days.

## Why you need at least two nameservers

`byeorim.com` had two NS records, `david` and `kami`. Most registries require at least two.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 356" role="img" aria-label="A resolver picks any of the several nameservers; behind each nameserver name are several IPs, and behind each IP are many locations spread out by anycast">
    <defs>
      <marker id="n8a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
    </defs>
    <rect x="16" y="56" width="140" height="64" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="86" y="94" font-size="14" font-weight="700" fill="currentColor" text-anchor="middle">Resolver</text>
    <line x1="162" y1="76" x2="214" y2="52" stroke="currentColor" stroke-width="2" marker-end="url(#n8a)"/>
    <line x1="162" y1="100" x2="214" y2="142" stroke="currentColor" stroke-width="2" marker-end="url(#n8a)"/>
    <rect x="220" y="22" width="280" height="56" rx="10" fill="var(--dgm-accent)"/>
    <text class="m" x="360" y="56" font-size="14" fill="#fff" text-anchor="middle">david.ns.cloudflare.com</text>
    <rect x="220" y="112" width="280" height="56" rx="10" fill="var(--dgm-accent)"/>
    <text class="m" x="360" y="146" font-size="14" fill="#fff" text-anchor="middle">kami.ns.cloudflare.com</text>
    <text x="516" y="46" font-size="12.5" fill="currentColor">the order carries no meaning</text>
    <text x="516" y="68" font-size="12.5" fill="var(--secondary)">picks whichever</text>
    <text x="516" y="136" font-size="12.5" fill="currentColor">if one dies</text>
    <text x="516" y="158" font-size="12.5" fill="var(--secondary)">it moves to the rest</text>
    <line x1="16" y1="196" x2="704" y2="196" stroke="var(--tertiary)" stroke-width="1" opacity="0.6"/>
    <text x="16" y="226" font-size="13.5" font-weight="700" fill="currentColor">And one IP is not one server</text>
    <rect x="16" y="244" width="180" height="48" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text class="m" x="106" y="274" font-size="13.5" fill="currentColor" text-anchor="middle">172.64.33.152</text>
    <line x1="202" y1="268" x2="232" y2="268" stroke="currentColor" stroke-width="2" marker-end="url(#n8a)"/>
    <rect x="240" y="248" width="140" height="40" rx="8" fill="none" stroke="var(--dgm-go)" stroke-width="1.5"/>
    <text x="310" y="273" font-size="13" fill="currentColor" text-anchor="middle">Seoul</text>
    <rect x="392" y="248" width="140" height="40" rx="8" fill="none" stroke="var(--dgm-go)" stroke-width="1.5"/>
    <text x="462" y="273" font-size="13" fill="currentColor" text-anchor="middle">Frankfurt</text>
    <rect x="544" y="248" width="140" height="40" rx="8" fill="none" stroke="var(--dgm-go)" stroke-width="1.5"/>
    <text x="614" y="273" font-size="13" fill="currentColor" text-anchor="middle">São Paulo</text>
    <text x="16" y="322" font-size="13.5" fill="var(--secondary)">Data centers worldwide all advertise the same IP as their own at once. That's anycast.</text>
    <text x="16" y="344" font-size="13.5" fill="var(--secondary)">Routers send you to the nearest one, so the same destination IP reaches different servers.</text>
  </svg>
  </div>
  <figcaption><p>It's also why only 13 root server names never go down.</p></figcaption>
</figure>

When there are several NS records, the resolver **picks whichever one it likes.** The order they're listed in carries no priority. Usually it remembers which one answered fastest and picks that one.

So how do two servers keep the same answers? The traditional way is that one is the original (primary) and the rest copy from it by **zone transfer**. The query type that asks for a whole zone is called `AXFR`; there is also `IXFR` (incremental zone transfer), which fetches only what changed. When to copy is decided by the **serial number** in the **SOA** (Start of Authority) record, which holds the zone's administrative details.

```
$ dig +short byeorim.com SOA
david.ns.cloudflare.com. dns.cloudflare.com. 2413581597 10000 2400 604800 1800

  david.ns.cloudflare.com.    primary nameserver
  dns.cloudflare.com.         admin email address
  2413581597                  serial number
  10000 · 2400 · 604800       refresh · retry · expire
  1800                        negative TTL
```

The secondaries check the primary's serial periodically and pull the whole zone when the number has gone up. The admin email address uses a dot instead of `@` because DNS can't handle `@`. `dns.cloudflare.com` means `dns@cloudflare.com`.

Large services like Cloudflare run things differently under the hood. Instead of a primary and secondaries pulling zone transfers, they push zone data out to their own nodes worldwide by their own means. From the outside, though, it looks exactly like the traditional setup: ask `david.ns.cloudflare.com` or ask `kami.ns.cloudflare.com`, and the response comes back with the `aa` flag set.

All that `aa` certifies is one thing: **the answer came straight from a server with authority over this zone.** It says nothing about which of them holds the original as primary. A secondary answering out of data it pulled in by zone transfer sets `aa` just the same. So as far as a resolver is concerned the two servers in the NS list are perfectly equal, and either one gives it an authoritative answer rather than a cached copy.

And a nameserver name doesn't get just one IP either. You can hang several A records off a single name, and `david.ns.cloudflare.com` does.

```
$ dig +short david.ns.cloudflare.com A
108.162.193.152
172.64.33.152
173.245.59.152
```

Three IPs, and each of those is **anycast** in turn. Normally one IP means one server, but under anycast data centers all over the world advertise the same IP as their own at the same time. Internet routers each pick whichever path is closest to them and send the packet there. A query sent from Seoul and one sent from São Paulo carry the same destination IP and still land on different servers. That's how the root servers cope with only 13 names, `a` through `m`. Thirteen names, hundreds of actual servers worldwide.

## "It doesn't exist" is an answer too

Query a domain that doesn't exist and the resolver doesn't go quiet — **it tells you explicitly that there is nothing there.** And that "nothing there" answer gets cached too.

And there are two kinds of not existing.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 302" role="img" aria-label="There are two kinds. NXDOMAIN means the name itself does not exist; NODATA means the name exists but that record type does not. Both are cached for the SOA's last value.">
    <rect x="16" y="16" width="336" height="152" rx="12" fill="var(--code-bg)" stroke="var(--dgm-stop)" stroke-width="2"/>
    <text x="40" y="52" font-size="17" font-weight="700" fill="currentColor">NXDOMAIN</text>
    <text x="40" y="76" font-size="13" fill="var(--secondary)">no such name at all</text>
    <line x1="40" y1="92" x2="328" y2="92" stroke="var(--tertiary)" stroke-width="1" opacity="0.6"/>
    <text class="m" x="40" y="120" font-size="13" fill="currentColor">nope-xyz.google.com</text>
    <text class="m" x="40" y="148" font-size="12.5" fill="var(--dgm-stop)">status: NXDOMAIN</text>
    <rect x="368" y="16" width="336" height="152" rx="12" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="392" y="52" font-size="17" font-weight="700" fill="currentColor">NODATA</text>
    <text x="392" y="76" font-size="13" fill="var(--secondary)">the name exists, that type doesn't</text>
    <line x1="392" y1="92" x2="680" y2="92" stroke="var(--tertiary)" stroke-width="1" opacity="0.6"/>
    <text class="m" x="392" y="120" font-size="13" fill="currentColor">byeorim.com MX</text>
    <text class="m" x="392" y="148" font-size="12.5" fill="var(--secondary)">NOERROR · ANSWER: 0</text>
    <rect x="16" y="192" width="688" height="66" rx="10" fill="var(--dgm-accent)"/>
    <text x="40" y="220" font-size="15" font-weight="700" fill="#fff">both get cached, and the lifetime is the last number in the SOA</text>
    <text class="m" x="40" y="244" font-size="12.5" fill="rgba(255,255,255,.82)">… 604800 1800  ← a 30-minute "no"</text>
    <text x="16" y="292" font-size="13.5" fill="var(--secondary)">Look it up before you finish setting up and that "no" is cached in your resolver for 30 minutes.</text>
  </svg>
  </div>
  <figcaption><p>The most common cause of "I set it up, so why isn't it working?"</p></figcaption>
</figure>

```
$ dig @1.1.1.1 nope-xyz.google.com A
;; ->>HEADER<<- status: NXDOMAIN
;; AUTHORITY SECTION:
google.com.  60  IN  SOA  ns1.google.com. dns-admin.google.com. 973049826 900 900 1800 60
                                                                                       ^^
                                                                  negative lifetime = 60s
```

A negative answer **comes with an SOA record attached.** Its last number decides how long to believe this particular "doesn't exist." `google.com` says 60 seconds; `byeorim.com` (Cloudflare's default) says 1800 seconds, or 30 minutes. That number is why I lost half an hour in [Buying a Domain and Wiring Up a Page, For Real](/en/posts/buying-a-domain-in-practice/). Before I had finished setting things up, I got curious and looked `byeorim.com` up once — and that single lookup got "no A record" cached in my resolver for 30 minutes, so the same answer kept coming back long after the setup was done.

## Worth remembering

- **"DNS server" is two jobs.** The side I ask (the resolver) and the side the world asks about my domain (the authoritative nameserver). Different control panel, different blast radius, different person who can fix it.
- **The NS record that actually gets used is the one in the parent.** Authority lives in the child, but resolvers come down from the zone above, so they read the parent zone's NS record and go to that server. That's why changing nameservers lives in the registrar's panel.
- **A changed record doesn't spread — it gets replaced as resolver caches expire.** The authoritative nameserver pushes nothing to anyone. The maximum delay is the TTL of the record you changed. For records in your own zone you can shorten that delay by lowering the TTL a few days ahead; the NS TTL in the parent zone isn't yours to change, so a nameserver switch has to be waited out.
- **"Doesn't exist" gets cached too.** Better not to look the domain up until you've finished setting it up.

Four commands are enough to check.

```
$ dig +trace <domain>                      # from the root, one step at a time
$ dig @<parent-ns> <domain> NS             # the delegation actually used
$ dig @<auth-ns> <domain> A                # the original (check the aa flag)
$ dig +norecurse @<resolver> <domain> A    # what's left in the cache
```

---

Every `dig` output in this post is a real query against `byeorim.com`. The two earlier posts, [How a Domain Gets Registered, in Pictures](/en/posts/how-domains-get-registered/) and [Buying a Domain and Wiring Up a Page, For Real](/en/posts/buying-a-domain-in-practice/), passed over a few things, and this post covers them.
