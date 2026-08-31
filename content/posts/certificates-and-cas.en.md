---
title: "Certificates and CAs, in Pictures"
date: 2026-08-31T11:25:47+09:00
draft: false
slug: "certificates-and-cas"
translationKey: "certificates-and-cas"
categories: ["Engineering"]
tags: ["https", "tls", "certificates", "security", "networking"]
summary: "How many hands it passes through before a padlock appears in the address bar, and which of them you trust and why — certificates, CAs, the chain of trust, and domain validation in eight pictures."
---

<style>
.dgm { --dgm-accent: #14468C; --dgm-go: #1B7A54; --dgm-stop: #A8402A; margin: 0 0 var(--content-gap); }
:root[data-theme="dark"] .dgm { --dgm-accent: #2E6BC4; --dgm-go: #4FBE90; --dgm-stop: #E5876A; }
.dgm .dgm-scroll { overflow-x: auto; }
.dgm svg { display: block; width: 100%; height: auto; color: var(--content); }
.dgm svg text { font-family: inherit; }
.dgm svg .m { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
</style>

There was a moment in [Buying a Domain and Wiring Up a Page, For Real](/en/posts/buying-a-domain-in-practice/) where the domain resolved to an IP but `curl` still got turned away.

```
curl: (35) SSL routines:ST_CONNECT:sslv3 alert handshake failure
```

It cleared 90 seconds later, and when I opened up the certificate the issuer was Google Trust Services, not Cloudflare. I wrote one line about it — "Cloudflare isn't a CA, it's a middleman" — and moved on.

Quite a lot is folded into that line. Here is the unfolded version: how many hands it passes through before a padlock appears in the address bar, and which of them you trust and why.

## What the padlock actually is

Worth pinning down before anything else.

It's the small icon at the left of the address bar, just before the domain name. The browser doesn't put it there on a hunch — it means **a check passed**, and there are exactly two conditions: a TLS connection to that server was established, and the certificate the server presented survived verification. Miss either one and you get "Not secure" in that spot, or a full warning page instead.

So the padlock isn't a stamp somebody granted after review. It's **a verdict a machine reached on the spot.** What that verdict does and does not cover is the subject of this whole post.

## And that verdict says two things

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 250" role="img" aria-label="The padlock in the address bar means two things: the contents are encrypted, and the other end is genuine">
    <defs>
      <marker id="c1a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
    </defs>
    <rect x="30" y="16" width="660" height="54" rx="27" fill="none" stroke="var(--tertiary)" stroke-width="1.5"/>
    <path d="M62,40 v-6 a8,8 0 0 1 16,0 v6" fill="none" stroke="var(--dgm-go)" stroke-width="2.5"/>
    <rect x="58" y="40" width="24" height="18" rx="3" fill="var(--dgm-go)"/>
    <text class="m" x="102" y="50" font-size="18" fill="currentColor">https://byeorim.com</text>
    <line x1="188" y1="76" x2="188" y2="106" stroke="currentColor" stroke-width="2" marker-end="url(#c1a)"/>
    <line x1="532" y1="76" x2="532" y2="106" stroke="currentColor" stroke-width="2" marker-end="url(#c1a)"/>
    <rect x="30" y="112" width="316" height="100" rx="10" fill="var(--dgm-accent)"/>
    <text x="52" y="150" font-size="16.5" font-weight="700" fill="#fff">① Nobody can read it</text>
    <text x="52" y="178" font-size="13" fill="rgba(255,255,255,.82)">What goes back and forth is encrypted</text>
    <rect x="374" y="112" width="316" height="100" rx="10" fill="var(--dgm-accent)"/>
    <text x="396" y="150" font-size="16.5" font-weight="700" fill="#fff">② The other end is genuine</text>
    <text x="396" y="178" font-size="13" fill="rgba(255,255,255,.82)">This server really owns that domain</text>
    <text x="30" y="240" font-size="13.5" fill="var(--secondary)">Certificates and CAs are entirely about the second one.</text>
  </svg>
  </div>
  <figcaption><p>The hard part isn't the encryption. It's knowing who you're talking to.</p></figcaption>
</figure>

## Encryption alone protects nothing

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 250" role="img" aria-label="An encrypted conversation with the real server and one with an impostor look identical as far as the encryption is concerned">
    <defs>
      <marker id="c2a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
    </defs>
    <rect x="20" y="34" width="110" height="62" rx="10" fill="var(--dgm-accent)"/>
    <text x="75" y="72" font-size="16" font-weight="700" fill="#fff" text-anchor="middle">me</text>
    <line x1="140" y1="65" x2="304" y2="65" stroke="currentColor" stroke-width="2" marker-end="url(#c2a)"/>
    <text x="222" y="52" font-size="12.5" fill="var(--secondary)" text-anchor="middle">encrypted</text>
    <rect x="314" y="34" width="256" height="62" rx="10" fill="var(--code-bg)" stroke="var(--dgm-go)" stroke-width="2"/>
    <text x="442" y="72" font-size="15" font-weight="700" fill="currentColor" text-anchor="middle">the real byeorim.com</text>
    <polyline points="600,66 612,78 636,50" fill="none" stroke="var(--dgm-go)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
    <rect x="20" y="134" width="110" height="62" rx="10" fill="var(--dgm-accent)"/>
    <text x="75" y="172" font-size="16" font-weight="700" fill="#fff" text-anchor="middle">me</text>
    <line x1="140" y1="165" x2="304" y2="165" stroke="currentColor" stroke-width="2" marker-end="url(#c2a)"/>
    <text x="222" y="152" font-size="12.5" fill="var(--secondary)" text-anchor="middle">encrypted</text>
    <rect x="314" y="134" width="256" height="62" rx="10" fill="var(--code-bg)" stroke="var(--dgm-stop)" stroke-width="2"/>
    <text x="442" y="172" font-size="15" font-weight="700" fill="currentColor" text-anchor="middle">an impostor</text>
    <line x1="602" y1="150" x2="634" y2="182" stroke="var(--dgm-stop)" stroke-width="3.5" stroke-linecap="round"/>
    <line x1="634" y1="150" x2="602" y2="182" stroke="var(--dgm-stop)" stroke-width="3.5" stroke-linecap="round"/>
    <text x="20" y="234" font-size="13.5" fill="var(--secondary)">Both are perfectly encrypted. The only difference is who is on the other end.</text>
  </svg>
  </div>
  <figcaption><p>A secret conversation with a thief is still a secret conversation. That's why identity has to be checked.</p></figcaption>
</figure>

## A certificate is the ID card the server hands you

When you connect, the server hands over a card. That card is the certificate.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 400" role="img" aria-label="A certificate carries a domain name, additional domain names, a public key, a validity period, an issuer, and the issuer's signature">
    <rect x="60" y="16" width="600" height="310" rx="14" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <rect x="60" y="16" width="600" height="52" rx="14" fill="var(--dgm-accent)"/>
    <rect x="60" y="50" width="600" height="18" fill="var(--dgm-accent)"/>
    <text x="84" y="50" font-size="16.5" font-weight="700" fill="#fff">Certificate · the card the server hands you</text>
    <text x="84" y="104" font-size="13" fill="var(--secondary)">Domain name</text>
    <text class="m" x="250" y="104" font-size="14" fill="currentColor">byeorim.com</text>
    <line x1="84" y1="122" x2="636" y2="122" stroke="var(--tertiary)" stroke-width="1" opacity="0.5"/>
    <text x="84" y="146" font-size="13" fill="var(--secondary)">Also covers</text>
    <text class="m" x="250" y="146" font-size="12.5" fill="currentColor">www.byeorim.com</text>
    <line x1="84" y1="164" x2="636" y2="164" stroke="var(--tertiary)" stroke-width="1" opacity="0.5"/>
    <text x="84" y="188" font-size="13" fill="var(--secondary)">Public key</text>
    <text class="m" x="250" y="188" font-size="12.5" fill="currentColor">EC prime256v1</text>
    <line x1="84" y1="206" x2="636" y2="206" stroke="var(--tertiary)" stroke-width="1" opacity="0.5"/>
    <text x="84" y="230" font-size="13" fill="var(--secondary)">Valid</text>
    <text class="m" x="250" y="230" font-size="12.5" fill="currentColor">2026-08-30 → 2026-11-28</text>
    <line x1="84" y1="248" x2="636" y2="248" stroke="var(--tertiary)" stroke-width="1" opacity="0.5"/>
    <text x="84" y="272" font-size="13" fill="var(--secondary)">Issued by</text>
    <text class="m" x="250" y="272" font-size="12.5" fill="currentColor">Google Trust Services · WE1</text>
    <line x1="84" y1="290" x2="636" y2="290" stroke="var(--tertiary)" stroke-width="1" opacity="0.5"/>
    <text x="84" y="313" font-size="14" font-weight="700" fill="var(--dgm-accent)">Issuer's signature</text>
    <text class="m" x="250" y="313" font-size="12.5" fill="var(--dgm-accent)">3045 0221 00f1 987e ...</text>
    <text x="60" y="362" font-size="13.5" fill="var(--secondary)">The browser checks three things — the domain name, the dates, the last row.</text>
  </svg>
  </div>
  <figcaption><p>The last row is what makes this an ID card. The rest is just text.</p></figcaption>
</figure>

Here's the real thing.

```
$ echo | openssl s_client -connect byeorim.com:443 -servername byeorim.com 2>/dev/null \
    | openssl x509 -noout -subject -issuer -dates -ext subjectAltName

subject=CN=byeorim.com
issuer=C=US, O=Google Trust Services, CN=WE1
notBefore=Aug 30 12:01:03 2026 GMT
notAfter=Nov 28 13:01:00 2026 GMT
X509v3 Subject Alternative Name:
    DNS:byeorim.com, DNS:www.byeorim.com, DNS:*.www.byeorim.com
```

`subject` is the domain name, `issuer` is who signed it. **The field the browser actually matches the hostname against is not `subject` but `Subject Alternative Name` (SAN).** Names used to live in `CN` alone, which couldn't hold more than one, so SAN was added; today `CN` is closer to decoration for humans. One certificate covers both `byeorim.com` and `www.byeorim.com` because both are listed in SAN.

## Why it can't be forged

Anyone can copy the text on a card. The signature on the last row is what stops them.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 300" role="img" aria-label="The CA signs the certificate with its private key, and the browser verifies that signature with the CA public key it already has">
    <defs>
      <marker id="c4a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
    </defs>
    <text x="10" y="28" font-size="13" font-weight="700" fill="var(--secondary)">Issuing — the CA does this</text>
    <rect x="10" y="40" width="168" height="66" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="94" y="79" font-size="14" fill="currentColor" text-anchor="middle">Certificate body</text>
    <line x1="184" y1="73" x2="252" y2="73" stroke="currentColor" stroke-width="2" marker-end="url(#c4a)"/>
    <rect x="258" y="40" width="164" height="66" rx="10" fill="var(--dgm-accent)"/>
    <text x="340" y="72" font-size="14" font-weight="700" fill="#fff" text-anchor="middle">CA private key</text>
    <text x="340" y="92" font-size="11.5" fill="rgba(255,255,255,.82)" text-anchor="middle">only the CA has it</text>
    <line x1="428" y1="73" x2="496" y2="73" stroke="currentColor" stroke-width="2" marker-end="url(#c4a)"/>
    <rect x="502" y="40" width="208" height="66" rx="10" fill="var(--code-bg)" stroke="var(--dgm-go)" stroke-width="2"/>
    <text x="606" y="79" font-size="14" fill="currentColor" text-anchor="middle">Signed certificate</text>
    <text x="10" y="170" font-size="13" font-weight="700" fill="var(--secondary)">Verifying — the browser does this</text>
    <rect x="10" y="182" width="168" height="66" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="94" y="221" font-size="14" fill="currentColor" text-anchor="middle">Received certificate</text>
    <line x1="184" y1="215" x2="252" y2="215" stroke="currentColor" stroke-width="2" marker-end="url(#c4a)"/>
    <rect x="258" y="182" width="164" height="66" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="340" y="214" font-size="14" font-weight="700" fill="currentColor" text-anchor="middle">CA public key</text>
    <text x="340" y="234" font-size="11.5" fill="var(--secondary)" text-anchor="middle">everyone has it</text>
    <line x1="428" y1="215" x2="496" y2="215" stroke="currentColor" stroke-width="2" marker-end="url(#c4a)"/>
    <rect x="502" y="182" width="208" height="66" rx="10" fill="var(--code-bg)" stroke="var(--dgm-go)" stroke-width="2"/>
    <text x="606" y="221" font-size="14" fill="currentColor" text-anchor="middle">Not one byte changed</text>
    <text x="10" y="284" font-size="13.5" fill="var(--secondary)">Change the contents and the signature breaks. A new one needs the CA's private key.</text>
  </svg>
  </div>
  <figcaption><p>It's a seal, not a lock. It doesn't hide the contents — it reveals whether they changed.</p></figcaption>
</figure>

## Two key pairs, and that's what trips people up

This is where it usually goes sideways. **Two key pairs show up in this story, and they have nothing to do with each other.**

| | Owner | What the private key does | Where the public key lives |
|---|---|---|---|
| **Server key pair** | the byeorim.com server | proves in the handshake that it owns this certificate | **inside** the certificate |
| **CA key pair** | Google Trust Services | signs the certificate | **preinstalled** in the browser |

That distinction matters for one reason. **A certificate is not a secret.** Anyone who connects gets a copy — that's exactly what `openssl` did above. So nothing stops you from copying someone else's certificate onto your own server.

It still gets you nowhere. After receiving the certificate the browser checks, during the handshake, **whether the other end currently holds the private key that pairs with the public key inside it.** The copycat doesn't have that private key and never gets past that step. You can duplicate the card; you can't become its holder.

## So why trust the CA?

Verifying the signature needs the CA's public key. That key lives in the CA's own certificate. And who vouches for *that* certificate? The question keeps climbing, and it has to stop somewhere.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 390" role="img" aria-label="A chain of trust in which a root CA signs an intermediate CA which signs the server certificate, with the root preinstalled on the device">
    <defs>
      <marker id="c5a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
    </defs>
    <rect x="180" y="12" width="380" height="76" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="202" y="42" font-size="16.5" font-weight="700" fill="currentColor">GTS Root R4 · root CA</text>
    <text x="202" y="66" font-size="13" fill="var(--secondary)">Signs itself. Nobody vouches for it.</text>
    <line x1="150" y1="50" x2="174" y2="50" stroke="var(--dgm-accent)" stroke-width="2" stroke-dasharray="4 3"/>
    <text x="76" y="44" font-size="12.5" font-weight="700" fill="var(--dgm-accent)" text-anchor="middle">already on</text>
    <text x="76" y="62" font-size="12.5" font-weight="700" fill="var(--dgm-accent)" text-anchor="middle">my laptop</text>
    <line x1="370" y1="88" x2="370" y2="124" stroke="currentColor" stroke-width="2" marker-end="url(#c5a)"/>
    <text x="600" y="112" font-size="12.5" fill="var(--secondary)">signs</text>
    <rect x="180" y="124" width="380" height="76" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="202" y="154" font-size="16.5" font-weight="700" fill="currentColor">WE1 · intermediate CA</text>
    <text x="202" y="178" font-size="13" fill="var(--secondary)">Millions of certificates a day come from here</text>
    <line x1="370" y1="200" x2="370" y2="236" stroke="currentColor" stroke-width="2" marker-end="url(#c5a)"/>
    <text x="600" y="224" font-size="12.5" fill="var(--secondary)">signs</text>
    <rect x="180" y="236" width="380" height="76" rx="10" fill="var(--dgm-accent)"/>
    <text class="m" x="202" y="266" font-size="16" font-weight="700" fill="#fff">byeorim.com</text>
    <text x="202" y="290" font-size="13" fill="rgba(255,255,255,.82)">the card the server hands you</text>
    <text x="10" y="352" font-size="13.5" fill="var(--secondary)">The root is never verified. It is the end of verification, so it is simply trusted.</text>
  </svg>
  </div>
  <figcaption><p>A domain's chain of trust ends at the root zone; a certificate's chain ends at the roots installed on your machine.</p></figcaption>
</figure>

`openssl` prints that chain verbatim.

```
$ echo | openssl s_client -connect byeorim.com:443 -servername byeorim.com

depth=2 C=US, O=Google Trust Services LLC, CN=GTS Root R4
depth=1 C=US, O=Google Trust Services, CN=WE1
depth=0 CN=byeorim.com
```

`depth=0` is the card the server handed over; `depth=2` is the end of the chain. And where does that end live?

```
$ security find-certificate -a -p /System/Library/Keychains/SystemRootCertificates.keychain | grep -c "BEGIN CERTIFICATE"
158
```

**On my Mac there were 158 of them preinstalled.** GTS Root R4 is one. How many there are varies by OS, browser, and version, so the number itself doesn't matter. What matters is that all HTTPS trust on the internet ultimately starts from a list like this one. The browser trusts a root not because it verified it, but **because it's on the list.**

Which makes the list itself a form of power. To get on it a CA has to pass audits and compliance reviews, and a CA that misbehaves gets removed. Several have been, and it effectively put them out of business.

Turn it around: **anyone who can add something to that list can open up all of your HTTPS.** That's what's happening when a corporate laptop's security software asks to install a root certificate, and it's the same mechanism that lets a debugging proxy read HTTPS traffic.

## Why doesn't the root issue directly?

There's a reason the chain has three links.

The root private key sits in a vault, offline. Using it means gathering several people for something close to a ceremony. You can't pull it out to sign millions of certificates a day.

So the root **delegates signing authority to an intermediate CA**, and the actual issuing is done online by that intermediate. If an intermediate key leaks, you revoke that intermediate and the root survives. `WE1` is that intermediate.

## How does the CA know I own the domain?

This is the part people actually wonder about. What if someone else requests a certificate for `byeorim.com`?

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 390" role="img" aria-label="Domain validation: request a certificate, receive a token from the CA, place the token on the domain, and the CA looks it up and issues">
    <defs>
      <marker id="c6a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
    </defs>
    <rect x="40" y="12" width="640" height="60" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="64" y="48" font-size="14.5" fill="currentColor">① me → CA · I'd like a certificate for byeorim.com</text>
    <line x1="360" y1="72" x2="360" y2="92" stroke="currentColor" stroke-width="2" marker-end="url(#c6a)"/>
    <rect x="40" y="96" width="640" height="60" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="64" y="132" font-size="14.5" fill="currentColor">② CA → me · then go put this token on that domain</text>
    <line x1="360" y1="156" x2="360" y2="176" stroke="currentColor" stroke-width="2" marker-end="url(#c6a)"/>
    <rect x="40" y="180" width="640" height="84" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="64" y="212" font-size="14.5" fill="currentColor">③ Put a file on that domain's web server · HTTP-01</text>
    <text x="84" y="240" font-size="14.5" fill="currentColor">or a TXT record in that domain's DNS · DNS-01</text>
    <line x1="360" y1="264" x2="360" y2="284" stroke="currentColor" stroke-width="2" marker-end="url(#c6a)"/>
    <rect x="40" y="288" width="640" height="60" rx="10" fill="var(--dgm-accent)"/>
    <text x="64" y="324" font-size="14.5" font-weight="700" fill="#fff">④ The CA looks it up itself, confirms, and issues</text>
    <text x="40" y="376" font-size="13.5" fill="var(--secondary)">Control the web server or the DNS and you count as the owner. Hence 'domain validation'.</text>
  </svg>
  </div>
  <figcaption><p>Nobody reads what you wrote on the form. They only check whether you can actually move that domain.</p></figcaption>
</figure>

The protocol that automates this exchange is **ACME**. Let's Encrypt created it and it's now a standard. What a tool like `certbot` does is run those four steps without a human.

The validation method ends up recorded in the certificate too.

```
X509v3 Certificate Policies:
    Policy: 2.23.140.1.2.1
```

That number means **DV (Domain Validation)** — "we only confirmed control of the domain." OV and EV, which also verify the legal entity, exist, but browsers no longer distinguish the three on screen. Every padlock looks the same.

## What the padlock does not vouch for

Worth stating plainly:

- **It vouches** that the server you're connected to controls `byeorim.com`.
- **It does not vouch** that the site is honest, that a company exists behind it, or that it's safe to pay them.

Phishing sites have padlocks. Buy a domain and a DV certificate is five minutes away. **The padlock doesn't mean "safe site," it means "you're connected to the domain written in the address bar."** So the thing to check isn't the padlock — it's the spelling of the domain next to it.

The misreading is widespread enough that **browsers are moving away from the padlock.** Chrome is the clearest case: version 117 in 2023 dropped it and put a settings-slider icon in that spot. Google's stated reason is exactly the paragraph above — in its own research only 11% of users could correctly identify what the lock icon meant, and most read it as "this site is trustworthy."

Which browsers still draw a padlock changes from version to version, so check rather than assume. Only the direction is worth remembering — **the padlock is going away not because security got weaker, but because the metaphor itself was judged misleading.**

## When a CA gets it wrong

If a CA is breached or mistakenly issues a certificate for someone else's domain, the whole structure collapses. That has actually happened.

The answer was to force **every issuance into a public ledger**: Certificate Transparency (CT). When a CA issues a certificate it submits it to public logs and embeds the receipts (SCTs) the logs return. Chrome outright rejects certificates without them.

```
$ echo | openssl s_client -connect byeorim.com:443 -servername byeorim.com 2>/dev/null \
    | openssl x509 -noout -text | grep -A2 "Signed Certificate Timestamp"

Signed Certificate Timestamp:
    Log ID    : D7:6D:7D:10:D1:A7:F5:77:...
    Timestamp : Aug 30 13:01:03.738 2026 GMT
```

Two receipts were embedded — one from each of two different logs.

The effect is this: **if someone quietly obtains a certificate for your domain, that fact lands in a public ledger.** Put a domain into [crt.sh](https://crt.sh) and you see every certificate ever issued for it. Quietly is no longer an option, and that's what CT changed.

## A 90-day lifetime

Look at the dates again.

```
notBefore=Aug 30 12:01:03 2026 GMT
notAfter =Nov 28 13:01:00 2026 GMT      ← 90 days
```

Short. There's a reason.

**Revocation — invalidating a certificate — doesn't really work in practice.** If a private key leaks and the CA declares the certificate revoked, there's no guarantee that news reaches browsers worldwide in time. Plenty of implementations skip revocation checks entirely.

So the industry went the other way: **don't let them live long in the first place.** A leak then has a much narrower window to do damage. The maximum keeps dropping — once five years, then 398 days, and as of March 2026 it's 200 days, dropping to 100 days in 2027 and 47 days in 2029.

One consequence follows. **As lifetimes shrink, renewing by hand stops being possible.** An operation where a person remembers every 47 days will eventually go down on an expired certificate. That's why automation like ACME became a premise rather than a choice.

## So what Cloudflare actually did

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 250" role="img" aria-label="Cloudflare is not a CA but a middleman that obtains certificates from real CAs on your behalf and installs them">
    <defs>
      <marker id="c7a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
    </defs>
    <rect x="16" y="88" width="130" height="76" rx="10" fill="var(--dgm-accent)"/>
    <text x="81" y="132" font-size="16" font-weight="700" fill="#fff" text-anchor="middle">me</text>
    <line x1="152" y1="126" x2="230" y2="126" stroke="currentColor" stroke-width="2" marker-end="url(#c7a)"/>
    <rect x="236" y="74" width="204" height="104" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="338" y="112" font-size="16" font-weight="700" fill="currentColor" text-anchor="middle">Cloudflare</text>
    <text x="338" y="136" font-size="12.5" fill="var(--secondary)" text-anchor="middle">It runs both DNS and server</text>
    <text x="338" y="156" font-size="12.5" fill="var(--secondary)" text-anchor="middle">so it clears the challenge</text>
    <text x="612" y="44" font-size="13" font-weight="700" fill="var(--secondary)" text-anchor="middle">the real CAs</text>
    <line x1="446" y1="110" x2="518" y2="88" stroke="currentColor" stroke-width="2" marker-end="url(#c7a)"/>
    <line x1="446" y1="146" x2="518" y2="168" stroke="currentColor" stroke-width="2" marker-end="url(#c7a)"/>
    <rect x="524" y="60" width="180" height="56" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="614" y="94" font-size="13" fill="currentColor" text-anchor="middle">Google Trust Services</text>
    <rect x="524" y="140" width="180" height="56" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="614" y="174" font-size="13" fill="currentColor" text-anchor="middle">Let's Encrypt</text>
    <text x="16" y="232" font-size="13.5" fill="var(--secondary)">Cloudflare is not a CA. It installs what it fetches and swaps it before expiry.</text>
  </svg>
  </div>
  <figcaption><p>Those 90 seconds from the last post are how long this round trip took.</p></figcaption>
</figure>

Everything from the last post falls out of this.

**Why it was `handshake failure` and not a 404.** If the server has no certificate to present for that domain, the conversation never starts. HTTPS is HTTP carried over TLS: the TLS connection has to be established before a single HTTP request can travel over it. Fail the certificate exchange and you never get to send one. A 404 says "I got your request and there's no such page"; `handshake failure` is a layer below that.

**Why the issuer wasn't Cloudflare.** Cloudflare isn't a CA in the root stores. Signing under its own name would get it nowhere with browsers. So it fetches from Google Trust Services or Let's Encrypt.

**Why one certificate covered everything.** Back then a single `*.byeorim-com.workers.dev` wildcard covered every Worker in the account. A `*` in a SAN stands in for one label. But only one — `*.example.com` matches `a.example.com` but not `a.b.example.com`, and not `example.com` itself. That's why the real certificate lists `byeorim.com` and `www.byeorim.com` separately.

## How is this different from DNSSEC?

DNSSEC got turned on in the last post too. Both are described as a "chain of trust," but they're different chains.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 400" role="img" aria-label="The DNSSEC chain of trust and the TLS certificate chain of trust are two separate chains">
    <defs>
      <marker id="c8a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
    </defs>
    <line x1="360" y1="12" x2="360" y2="352" stroke="var(--tertiary)" stroke-width="1" stroke-dasharray="4 4"/>
    <text x="176" y="30" font-size="16.5" font-weight="700" fill="currentColor" text-anchor="middle">DNSSEC</text>
    <text x="176" y="52" font-size="12.5" fill="var(--secondary)" text-anchor="middle">Is the domain → IP answer genuine?</text>
    <text x="544" y="30" font-size="16.5" font-weight="700" fill="currentColor" text-anchor="middle">TLS certificate</text>
    <text x="544" y="52" font-size="12.5" fill="var(--secondary)" text-anchor="middle">Is the other end genuine?</text>
    <rect x="46" y="70" width="260" height="52" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="176" y="102" font-size="14" fill="currentColor" text-anchor="middle">root zone</text>
    <line x1="176" y1="122" x2="176" y2="146" stroke="currentColor" stroke-width="2" marker-end="url(#c8a)"/>
    <rect x="46" y="150" width="260" height="52" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text class="m" x="176" y="182" font-size="14" fill="currentColor" text-anchor="middle">.com zone</text>
    <line x1="176" y1="202" x2="176" y2="226" stroke="currentColor" stroke-width="2" marker-end="url(#c8a)"/>
    <rect x="46" y="230" width="260" height="52" rx="10" fill="var(--dgm-accent)"/>
    <text class="m" x="176" y="262" font-size="14" font-weight="700" fill="#fff" text-anchor="middle">byeorim.com zone</text>
    <rect x="414" y="70" width="260" height="52" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="544" y="102" font-size="14" fill="currentColor" text-anchor="middle">root CA</text>
    <line x1="544" y1="122" x2="544" y2="146" stroke="currentColor" stroke-width="2" marker-end="url(#c8a)"/>
    <rect x="414" y="150" width="260" height="52" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="544" y="182" font-size="14" fill="currentColor" text-anchor="middle">intermediate CA</text>
    <line x1="544" y1="202" x2="544" y2="226" stroke="currentColor" stroke-width="2" marker-end="url(#c8a)"/>
    <rect x="414" y="230" width="260" height="52" rx="10" fill="var(--dgm-accent)"/>
    <text class="m" x="544" y="262" font-size="14" font-weight="700" fill="#fff" text-anchor="middle">byeorim.com cert</text>
    <text x="176" y="312" font-size="12.5" fill="var(--secondary)" text-anchor="middle">a zone is vouched for by the zone above</text>
    <text x="544" y="312" font-size="12.5" fill="var(--secondary)" text-anchor="middle">a cert is vouched for by the CA above</text>
    <text x="176" y="336" font-size="12.5" fill="var(--secondary)" text-anchor="middle">starts at the root key everyone knows</text>
    <text x="544" y="336" font-size="12.5" fill="var(--secondary)" text-anchor="middle">starts at the root list on my device</text>
    <text x="20" y="378" font-size="13.5" fill="var(--secondary)">Two chains that never touch. Having one does not give you the other.</text>
  </svg>
  </div>
  <figcaption><p>DNSSEC asks whether you found the right address; the certificate asks whether what's there is real.</p></figcaption>
</figure>

DNSSEC protects **"did I find the right address"**; the certificate protects **"is what's at that address real."** DNSSEC comes first in sequence, but HTTPS holds up without it. Even if the answer points at a forged IP, that server can't produce a `byeorim.com` certificate.

The reverse doesn't hold. DNSSEC without HTTPS protects nothing — you found the right address, and then the entire conversation is in the clear.

## If the first request is plaintext, none of it counts

`Always Use HTTPS` being off in the last post is the final piece.

```
$ curl -sSI http://byeorim.com
HTTP/1.1 200 OK
                        ← no Location header
```

Type just `byeorim.com` in the address bar and the browser usually tries `http://` first. No certificate is involved in that request — there's no card to check. Adding a redirect doesn't close it either, because **the redirect response itself is plaintext** and can be swapped for somewhere else in transit.

`Always Use HTTPS` doesn't fully plug the hole. That first round trip is still plaintext. Removing it takes a `Strict-Transport-Security` (HSTS) header, which tells the browser **"from now on this domain is https only."** Once remembered, typing `http://` gets rewritten by the browser before the request ever leaves.

## What to remember

- **The padlock doesn't mean "safe site," it means "you're connected to the domain in the address bar."** Phishing sites have padlocks too.
- **Trust is rooted in the list of roots preinstalled on your device.** Whoever can add to that list can read all of your HTTPS.
- **Certificates live briefly and renew automatically.** Without automation, a site eventually goes down on an expired one.
- **Checking takes one command.** Domain name, validity dates, and issuer all come back.

```
$ echo | openssl s_client -connect <domain>:443 -servername <domain> 2>/dev/null \
    | openssl x509 -noout -subject -issuer -dates -ext subjectAltName
```
