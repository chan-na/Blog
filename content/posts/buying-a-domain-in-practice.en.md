---
title: "Buying a Domain and Wiring Up a Page, For Real"
date: 2026-08-31T00:50:19+09:00
draft: false
slug: "buying-a-domain-in-practice"
translationKey: "buying-a-domain-in-practice"
categories: ["Engineering"]
tags: ["dns", "domain", "cloudflare", "workers", "networking"]
summary: "Ninety minutes from buying byeorim.com to serving it from Cloudflare Workers — and everything the diagrams left out: a 'no such record' answer that gets cached too, the CNAME rule at the apex, and a DNSSEC that was included but switched off."
---

In [How a Domain Gets Registered, in Pictures](/en/posts/how-domains-get-registered/) I laid the process out in five steps. Pick a domain, check that it's free, pay a year up front at the counter, verify your email, point it at your server.

The pictures were right. But actually buying `byeorim.com` and wiring a page to it, **the order was different and things showed up that weren't in any diagram.** Ninety minutes, $10.46 a year.

This is that record: what the diagrams in the concept post turn into on a real screen and in a real terminal.

What I built: a domain from Cloudflare Registrar, a GitHub organization landing page, deployed on Cloudflare Workers.

## Picking a counter first

The registrar — what the concept post called "the counter" — isn't a single place. There's Namecheap, Porkbun, AWS Route 53, and locally in Korea, Gabia and Whois.

Wherever you buy, **the domain you end up with is identical.** There's exactly one registry for `.com` (Verisign), and registrars are just the counters lined up in front of it. What gets written into the `.com` zone is the same either way. What differs per counter is price, the DNS management UI, and which extras come bundled.

I picked Cloudflare Registrar for two reasons.

- **Domain, DNS, certificates, and deployment all live in one account.** As you'll see later, this makes a real difference when turning on DNSSEC.
- **Its pricing is unusual.** That's the next section.

Worth stating up front: **the pricing below is Cloudflare's policy, not how registrars generally work.** If anything it's the exception in the industry.

## How to actually check whether a domain is free

The registrar's search box will tell you. But that's one company's answer. Asking the source is more certain.

Start with `whois`, **the tool that queries a domain's registration ledger** — who registered it, when, and when it expires.

```
$ whois byeorim.com | head
% IANA WHOIS server
refer:        whois.verisign-grs.com
domain:       COM
organisation: VeriSign Global Registry Services
```

The first query doesn't answer. **IANA says "not my department, ask Verisign" and hands back a referral.** WHOIS is two-stage: ask the root (IANA) which registry owns the TLD, then ask that registry.

```
$ whois -h whois.verisign-grs.com byeorim.com
No match for domain "BYEORIM.COM".
```

That's the real answer. And there's a simpler check.

`dig` is **the tool that queries DNS directly**. Not the ledger — it answers which IP a domain currently resolves to and which nameservers are responsible for it.

```
$ dig +short byeorim.com NS
                              ← nothing
```

**An empty NS record means unregistered.** A registered domain always has NS records even with no A record, because the registry writes delegation data into the parent zone — "for this domain, go ask those nameservers." No NS means the domain doesn't exist in the `.com` zone at all.

## Paying a year at the counter — first year price equals renewal price

The subtitle on the search page summarizes the whole service.

![Domain search results and pricing](/images/domain-setup/04-search-results.jpg)

> Find and register a new domain **at cost, with no markup.**

| Domain | First year | Renewal |
|---|---|---|
| **byeorim.com** | **$10.46** | **$10.46/year** |
| byeorim.com.mx | $16.75 | $16.75/year |
| byeorim.com.ai | $160.00 | $80.00/year |
| byeorim.computer | $30.20 | $30.20/year |

**The first-year price and the renewal price are the same.** That's the point.

Registrars normally cut the first year to $0.99–$2 and charge $18–20 to renew. A domain is brutally hard to change once you've picked it — your email addresses, every link you've shipped, and your search ranking are all tied to that domain. At renewal time you're effectively a hostage.

The $10.46 breaks down into Verisign's wholesale price for the `.com` registry plus ICANN's $0.18 fee. The registrar's cut is zero.

As an aside, I searched the same domain twice and `byeorim.com.co` had moved from $10.00 to $15.00. This screen passes wholesale prices straight through, so the numbers are only true at the moment you look.

## Why do they want my home address

Right before payment it asks for registrant information. Name, email, phone, country, street, city, postal code. All required.

![Registrant information form and the WHOIS notice](/images/domain-setup/06-checkout-whois-notice.jpg)

Not because Cloudflare wants it. This is where **"you're renting, not buying"** from the concept post becomes concrete. A domain is a yearly lease, and ICANN obliges registrars to record who the tenant is.

The notice at the bottom of the form is honest about the limits.

> Cloudflare Registrar redacts registrant personal information from its public WHOIS service; however, it cannot control whether **the registry** redacts personal information from its own WHOIS service.

There are two separate WHOIS services — the registrar's and the registry's. Cloudflare covers its own and can't reach the other one. What that means in practice, I checked directly later.

The payment screen had this attached:

![Features included at no extra cost on the payment screen](/images/domain-setup/11-payment-screen.jpg)

> **Included at no extra cost**
>
> - WHOIS Privacy — Hide your personal information
> - DNSSEC — DNS security extensions
> - Email Forwarding — Create email aliases

All three are things other registrars sell. WHOIS privacy alone is typically an $8–15/year add-on. Selling at cost and throwing in the paid options has one explanation: they don't intend to make money on domains, they want the traffic from that domain crossing their network.

(There's a catch hiding in the word "included." More on that later.)

## Paid for, but the world doesn't know yet

Payment went through and the screen said so.

![Registration success screen](/images/domain-setup/12-registration-success.jpg)

Then I ran whois immediately:

```
$ whois -h whois.verisign-grs.com byeorim.com
No match for domain "BYEORIM.COM".
```

**My screen says I own it; the registry has never heard of it.** Payment completing is an event in the registrar's ledger. Registry entry is the `.com` zone's truth changing. Two different events, with a gap between them.

Polling every 20 seconds, it showed up about a minute later.

```
Domain Name: BYEORIM.COM
Creation Date: 2026-08-30T12:55:42Z
Registry Expiry Date: 2027-08-30T12:55:42Z
Registrar: Cloudflare, Inc.
Domain Status: clientTransferProhibited
Name Server: DAVID.NS.CLOUDFLARE.COM
Name Server: KAMI.NS.CLOUDFLARE.COM
```

Expiry is registration plus exactly one year. `clientTransferProhibited` is a registrar lock that stops someone quietly moving the domain to another registrar. The nameservers are named `david` and `kami` because Cloudflare assigns each account a pair of human-sounding names. It means nothing functionally.

## How far does WHOIS privacy actually go

The concept post said "you can hide your details." I checked with the details I'd just typed in.

But **who you ask matters.** Query the `.com` registry directly and there's no registrant information at all.

```
$ whois -h whois.verisign-grs.com byeorim.com
Domain Name: BYEORIM.COM
Registrar: Cloudflare, Inc.
Registrar WHOIS Server: whois.cloudflare.com
Creation Date: 2026-08-30T12:55:42Z
...
                                      ← not a single Registrant field
```

`.com` is a **thin registry**. It holds the domain name, dates, registrar, nameservers, and status — and **does not store registrant contacts.** Instead it points at a `Registrar WHOIS Server`: go ask over there. The registrant details live with the registrar.

So, as with the availability check earlier, you have to ask twice.

```
$ whois -h whois.cloudflare.com byeorim.com

Registrant Name:           DATA REDACTED
Registrant Organization:   DATA REDACTED
Registrant Street:         DATA REDACTED
Registrant City:           DATA REDACTED
Registrant Postal Code:    DATA REDACTED
Registrant Email:          (empty)

Registrant State/Province: <state>          ← not redacted
Registrant Country:        KR               ← not redacted
Registrant Phone:          +1.4153197517    ← substituted
```

(Plain `whois byeorim.com` sometimes produces this too. It depends on whether your `whois` client automatically follows the `Registrar WHOIS Server` pointer in the registry's reply, which varies by implementation — the default macOS `whois` does follow it. If yours doesn't, name the registrar with `-h` as above.)

Three things stand out.

**Name, address, and email really are hidden.** The details I grumbled about handing over don't get published.

**But state and country are not.** ICANN requires those two to stay public — the argument being that you need something to determine which country's law applies in a dispute. A privacy service doesn't hide everything.

**The phone number isn't blanked, it's replaced.** `+1.415` is a San Francisco area code — Cloudflare's own number. Legal notices still have somewhere to land, while the real number stays hidden.

And the notice at the bottom of the checkout form — *"it cannot control whether the registry redacts personal information"* — resolves here. `.com` is a thin registry, so **the registry never had the registrant details in the first place. There's nothing for it to leak.** But some TLDs, `.org` among them, run **thick registries** that store contacts directly. On those, there really is a surface the registrar's redaction doesn't reach. That notice wasn't boilerplate — it was a condition that depends on your TLD.

## The site went live before the domain did

In the concept post, "point it at your server" was the **last** step. It turned out the order doesn't matter.

While waiting on payment I deployed the landing page first. Before that I had to decide where to put it. Three candidates:

| | How it deploys | Custom domain | Server-side logic |
|---|---|---|---|
| **GitHub Pages** | push to the repo | four fixed A records at the apex, by hand | none (static only) |
| **Cloudflare Pages** | git-connected builds | a few clicks if you're on Cloudflare DNS | Functions |
| **Cloudflare Workers** | upload via `wrangler` | one line in the config; DNS records created for you | available from the start |

This blog itself runs on GitHub Pages. It's free and plenty for a static site. Two things gave me pause this time. **Attaching an apex domain means hard-coding four GitHub IPs** (why, later in this post), and adding any server-side behavior later would mean moving off it entirely.

That leaves Cloudflare's Pages and Workers — and Cloudflare answers that one itself. The Pages documentation opens by telling you to "Start new projects with Workers." Workers covers most of what Pages does, with a broader feature set, and it's their primary platform.

**The deciding factor was that the domain already lived at Cloudflare.** Registrar, DNS, certificates, and hosting in one account removes whole steps. As you'll see later, I never had to create a DNS record by hand.

So, Workers. This is the entire Cloudflare Workers config file, `wrangler.jsonc`:

```jsonc
{
  "name": "byeorim-landing",
  "compatibility_date": "2026-08-30",
  "assets": { "directory": "./public" }
}
```

The thing worth noticing is that there's no `main`. A Worker normally points `main` at an entry script, and that script builds the response when a request arrives. With `assets` and no `main`, you get **a Worker with zero lines of JavaScript.** Cloudflare serves the static files straight from the edge, and those requests don't even count as Worker invocations.

Deploying is done with `wrangler`, **the official CLI for Cloudflare Workers**. It reads the config file, uploads your code and static files to Cloudflare, and handles both running locally (`wrangler dev`) and shipping (`wrangler deploy`). Prefixing it with `npx` runs it without installing anything.

```
$ npx wrangler deploy
✨ Read 1 file from the assets directory ./public
+ /index.html
Total Upload: 0.34 KiB / gzip: 0.25 KiB
  https://byeorim-landing.byeorim-com.workers.dev
```

Eight seconds and the site was on the internet. **The domain hadn't even been bought yet.**

That accident illustrates something important. **A site and a domain are independent.** A site can exist without a domain (as it did right then), and a domain can exist with nothing to point at. What joins them is one DNS record at the end.

## DNS resolves but HTTPS doesn't

Checking right after deploy showed a strange state.

```
$ dig +short byeorim-landing.byeorim-com.workers.dev
104.21.63.79
172.67.144.54                    ← the domain already resolves to an IP

$ curl https://byeorim-landing.byeorim-com.workers.dev
curl: (35) SSL routines:ST_CONNECT:sslv3 alert handshake failure
                                 ← but TLS is refused
```

**A domain resolving to an IP and that IP being ready to serve HTTPS for that domain are two different things.** DNS records apply instantly; a certificate has to be requested from a CA and delivered. This is what's really going on most times "the site is up but the browser shows a warning."

Poking it every 15 seconds:

```
[21:23:46] attempt 1 → handshake failure
[21:24:01] attempt 2 → handshake failure
[21:24:16] attempt 3 → handshake failure
[21:24:31] attempt 4 → handshake failure
[21:24:47] attempt 5 → 200          ← issued
```

About a minute and a half from deploy. Inspecting the certificate shows why this only happens once.

```
issuer=C=US, O=Google Trust Services, CN=WE1
subject=CN=byeorim-com.workers.dev
X509v3 Subject Alternative Name:
    DNS:byeorim-com.workers.dev, DNS:*.byeorim-com.workers.dev
```

The issuer isn't Cloudflare, it's Google Trust Services. Cloudflare isn't a CA — it's a broker that pulls certificates from several CAs and installs them for you. And it's a **wildcard**, so this one certificate covers every Worker on the account. The 90 seconds I waited was the price of this account's first deploy.

Who issues that certificate, and why does the browser believe them? The CA, the signature, and the chain of trust I skated past in one line here are unfolded in [Certificates and CAs, in Pictures](/en/posts/certificates-and-cas/).

## You can't put a CNAME on the apex

Now to attach the domain. Three more lines in the same Cloudflare Workers config file, `wrangler.jsonc`:

```jsonc
"routes": [
  { "pattern": "byeorim.com",     "custom_domain": true },
  { "pattern": "www.byeorim.com", "custom_domain": true }
]
```

With `custom_domain: true`, wrangler **creates the DNS records for you.** Nothing to click in the dashboard. But the record it created wasn't what I expected.

![The DNS record type is Worker](/images/domain-setup/13-dns-records-worker.jpg)

| Name | Type | Content | Proxy status |
|---|---|---|---|
| byeorim.com | **Worker** | byeorim-landing | 🟠 Proxied |
| www.byeorim.com | **Worker** | byeorim-landing | 🟠 Proxied |

The type is neither `A` nor `CNAME` but **`Worker`**. No such record type exists in DNS. It's a virtual record inside Cloudflare, locked so you can't even edit it by hand.

**This is the answer to the apex problem.**

DNS forbids a CNAME on the apex — `byeorim.com` with no subdomain.

A CNAME means "hand every record for this DNS name over to that one." Which is why **a name carrying a CNAME cannot carry any other record.** And the apex has two records it can never do without.

- **NS** (Name Server) — the list of nameservers responsible for this zone. The same record we queried earlier to check whether the domain was free.
- **SOA** (Start of Authority) — the zone's administrative record: primary nameserver, admin email, serial number, and a set of TTLs, all on one line. The negative TTL we'll meet later is read from here.

Neither can be removed from the apex. So putting a CNAME there runs straight into the "no other records" rule. That's why services like GitHub Pages tell you to hard-code four fixed IPs as A records at the apex. If those IPs change, you fix it yourself.

Cloudflare takes a different route entirely. Because it *is* the authoritative nameserver — the server with the final say on this domain — it **synthesizes the A/AAAA answer on the spot** when a query arrives. From outside it looks like an ordinary A record.

```
$ dig @david.ns.cloudflare.com +short byeorim.com A
172.67.192.105
104.21.81.254
```

Those IPs aren't dedicated to this domain — they're Cloudflare anycast space. When a request lands, the `Host` header and TLS SNI decide which Worker it goes to. That's what `Proxied` (the orange cloud) means.

## The trap: adding routes turns off workers.dev

There was a warning in the deploy log.

```
▲ WARNING  Because 'workers_dev' is not in your Wrangler file,
           it will be disabled for this deployment by default.
```

I skipped past it, then checked:

```
$ curl -o /dev/null -w "%{http_code}" https://byeorim-landing.byeorim-com.workers.dev
404
```

The URL that had been working was dead. With no `routes`, workers.dev defaults to on; the moment you declare `routes`, the default flips to off. The assumption is that you attached a custom domain so you won't need workers.dev.

To keep both you have to write `"workers_dev": true` explicitly. If you'd been sharing the workers.dev URL with your team, one deploy breaks every one of those links.

## dig works, curl doesn't

This is the part I spent longest on. Right after the custom domain deploy:

| How I checked | Result |
|---|---|
| `https://byeorim.com` in Chrome | ✅ fine |
| `dig byeorim.com A` | ✅ `172.67.192.105`, `104.21.81.254` |
| `curl https://byeorim.com` | ❌ Could not resolve host |
| `getaddrinfo()` in Python | ❌ gaierror |

**On the same machine, at the same time.** The exact inverse of the usual "dig works but the browser doesn't."

They take three different paths.

- **`dig`** sends **DNS packets directly** to the resolver. It never touches the OS cache.
- **`curl`, and most programs,** call `getaddrinfo()` and **ask the OS.** On macOS `mDNSResponder` handles that and checks its own cache first.
- **Chrome** has its own DNS stack, and with Secure DNS (DoH) it skips the OS entirely.

I could see exactly what `mDNSResponder` was holding onto:

```
$ dscacheutil -q host -a name byeorim.com
name: byeorim.com
ipv6_address: 2606:4700:3030::ac43:c069
ipv6_address: 2606:4700:3034::6815:51fe
```

AAAA (IPv6) but no A (IPv4). It was **caching the "no such record" answer** to the A query. How long it keeps that is written in the last field of the SOA record.

```
$ dig +short byeorim.com SOA
david.ns.cloudflare.com. dns.cloudflare.com. 2413580434 10000 2400 604800 1800
                                                                        ^^^^
                                                   negative TTL = 1800s = 30 minutes
```

**"No" gets cached too.** If you looked the domain up *before* you finished setting it up, you can finish and still get "no such domain" for up to 30 minutes. This is the most common thing behind "I definitely configured it, why isn't it working."

The lesson is simple. **Don't look up the domain until you've finished configuring it.** That one curious query plants a 30-minute "no" in your own resolver.

If you don't want to wait, you can bypass the local cache and verify the server side first.

```
$ curl -sS --resolve byeorim.com:443:172.67.192.105 \
    -o /dev/null -w "status=%{http_code} ip=%{remote_ip}\n" https://byeorim.com
status=200  ip=172.67.192.105
```

`--resolve` pins the IP and skips DNS entirely. A 200 here means the server, the routing, and the certificate are all fine, and what's left is purely your own machine. Flushing the cache fixed it immediately.

```
$ sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder
$ curl -o /dev/null -w "%{http_code}\n" https://byeorim.com
200
```

As a debugging order:

1. `curl --resolve <domain>:443:<IP>` → 200 means the server is fine. It's DNS.
2. `dig @<authoritative NS> <domain>` → an answer means the record exists. It's cache.
3. `dig <domain>` works but `curl` doesn't → it's the **OS cache**.
4. Flush the cache.

## "Included" and "on" are different words

Once `byeorim.com` was serving from the Worker over HTTPS, I went through the security settings in the Cloudflare dashboard from the top. Two defaults weren't what I assumed.

**First, plain HTTP was wide open.**

```
$ curl -sSI http://byeorim.com
HTTP/1.1 200 OK
Server: cloudflare
                        ← no Location header
```

A plain 200, no redirect. And no `Strict-Transport-Security` header on the HTTPS responses either. It's a static page with nothing to steal, but it does mean someone on the path can read it — or **swap it out**.

In the Cloudflare dashboard, open the domain and go to **SSL/TLS → Edge Certificates**; there's an `Always Use HTTPS` toggle. Turning it on:

```
$ curl -sSI http://byeorim.com
HTTP/1.1 301 Moved Permanently
Location: https://byeorim.com/
```

**Second, DNSSEC was off** — the item the payment screen listed as included at no extra cost.

DNSSEC is the standard for attaching digital signatures to DNS answers. Plain DNS never verifies anything: a resolver has no way to tell whether the answer it got really came from the domain's owner or was swapped out along the way. DNSSEC signs each record so a resolver can check.

I checked three ways whether it was actually on.

```
$ dig +short byeorim.com DS
                                  ← no DS at the parent
$ dig @david.ns.cloudflare.com +short byeorim.com DNSKEY
                                  ← no keys in the zone either
$ dig @1.1.1.1 byeorim.com A +dnssec | grep "^;; flags:"
;; flags: qr rd ra;               ← no ad flag
```

All empty. **Being included in your plan and being switched on are different claims.** In the same dashboard, **DNS → Settings** has an `Enable DNSSEC` button, and that's what turns it on.

Clicking it gave the zone a set of keys.

```
$ dig @david.ns.cloudflare.com +short byeorim.com DNSKEY
257 3 13 mdsswUyr3DPW132mOi8V9xESWE8jTo0dxCjjnopKl+Gq...
256 3 13 oJMRESz5E4gYzS/q6XDrvU1qMPYIjCWzJaOau8XNEZeq...
```

`257` is the KSK (Key Signing Key), `256` the ZSK (Zone Signing Key), `13` the ECDSA P-256 algorithm.

**Those keys mean the zone is now signed.** Cloudflare generated a key pair for the `byeorim.com` zone and signed every record in it with the private key. The public key is published as the `DNSKEY` record above. Answers from this zone now carry signatures, and a resolver can verify them against that `DNSKEY`.

Which leaves one problem. **Who vouches for the `DNSKEY` itself?** An attacker who forges the whole zone can plant their own key alongside it — verification passes, and the content is still fake.

That's where the parent zone comes in. A **DS record** (Delegation Signer) is registered in the parent zone, `.com`. It's a hash of the child zone's key — a **fingerprint**. A resolver asks `.com` for byeorim.com's key fingerprint and checks it against the `DNSKEY` it actually received. If they match, the key can be trusted.

The same logic continues upward. `.com`'s key is vouched for by the root, and the root's key is known to everyone in advance. Root → `.com` → `byeorim.com`: that linkage is the **chain of trust**.

**But the DS record didn't show up for a while.** The zone had keys while the parent still knew nothing about them. That intermediate state shows the structure exactly — signing alone proves nothing. Verification only becomes possible once the parent vouches for you.

And a DS has to be filed with the registry, so **only a registrar can put it there.** This is where keeping your registrar and your DNS at the same company pays off. If they're different, you copy the DS value out of Cloudflare and paste it by hand into the registrar's panel.

A few minutes later the DS record appeared and the chain connected.

```
$ dig +short byeorim.com DS
2371 13 2 F2DA3F181BBB3FB515DD197B7BC511539CD374BF23D1B328A47730E240CC4212

$ dig @1.1.1.1 byeorim.com A +dnssec | grep "^;; flags:"
;; flags: qr rd ra ad;
                  ^^
```

**`ad` = Authenticated Data.** It was just `qr rd ra` before. Now 1.1.1.1 has actually walked the signature chain from the root and is telling me this answer isn't forged. Two extra characters in the same command's output — and those two characters are the whole of DNSSEC.

## Final state

```
$ whois byeorim.com | grep Creation
Creation Date: 2026-08-30T12:55:42Z

$ dig +short byeorim.com NS
david.ns.cloudflare.com.  kami.ns.cloudflare.com.

$ dig +short byeorim.com A
172.67.192.105  104.21.81.254

$ dig +short byeorim.com DS
2371 13 2 F2DA3F18...40CC4212

$ curl -sSL -o /dev/null -w "%{url_effective} %{http_code}\n" http://byeorim.com
https://byeorim.com/ 200
```

The three warnings from the concept post, rewritten from the perspective of having actually done it:

- **You're renting, not buying.** The checkout screen keeps reminding you. Expiry is pinned to registration plus a year, it demands registrant details, and it says "non-refundable" right there.
- **Leave auto-renew on.** It was on by default. Not turning it off is the only work required.
- **You can hide your details — but not all of them.** Name, address, and email are redacted; state and country stay.

I'd add one more: **don't trust the defaults, go look.** DNSSEC said "included" and was off. Forced HTTPS was off. A few lines of `dig` and `curl` will tell you.

→ [Certificates and CAs, in Pictures](/en/posts/certificates-and-cas/) — how many hands it passes through before a padlock appears in the address bar.
