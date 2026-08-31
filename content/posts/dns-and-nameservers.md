---
title: "DNS와 네임서버, 그림으로 이해하기"
date: 2026-09-01T00:46:19+09:00
draft: false
slug: "dns-and-nameservers"
translationKey: "dns-and-nameservers"
categories: ["개발"]
tags: ["dns", "네임서버", "네트워크", "입문"]
summary: "'DNS 서버'라는 이름 하나에 정반대인 역할 두 개가 들어 있다. 묻는 쪽과 답하는 쪽, 존과 위임, 부모에도 자식에도 있는 NS 레코드, 캐시와 TTL까지 그림 아홉 장으로 갈라놓았다."
---

<style>
.dgm { --dgm-accent: #14468C; --dgm-go: #1B7A54; --dgm-stop: #A8402A; margin: 0 0 var(--content-gap); }
:root[data-theme="dark"] .dgm { --dgm-accent: #2E6BC4; --dgm-go: #4FBE90; --dgm-stop: #E5876A; }
.dgm .dgm-scroll { overflow-x: auto; }
.dgm svg { display: block; width: 100%; height: auto; color: var(--content); }
.dgm svg text { font-family: inherit; }
.dgm svg .m { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
</style>

앞의 두 글에서 "리졸버"와 "권한 네임서버"가 각각 한 번씩 언급되었다. [「도메인 등록, 그림으로 이해하기」](/posts/how-domains-get-registered/)에서는 질문이 세 번 오가는 그림과 `dig`가 뱉는 `aa` 플래그로, [「도메인 사서 웹페이지 붙이기, 실제로 해봤다」](/posts/buying-a-domain-in-practice/)에서는 `dig`는 되는데 `curl`은 안 되던 대목에서.

문제는 이 둘을 부르는 이름이 겹친다는 점이다. 아래 두 문장을 보면, 각각이 말하는 서버가 리졸버인지 권한 네임서버인지 헷갈릴 수 있다.

- "DNS 서버를 `8.8.8.8`로 바꿔봐."
- "네임서버를 Cloudflare로 바꿔야 해."

앞 문장의 `8.8.8.8`은 내가 질문을 던지는 쪽인 리졸버고, 뒤 문장의 네임서버는 세상이 내 도메인을 물어보는 쪽인 권한 네임서버다. 둘 다 DNS 얘기인데 **가리키는 대상이 정반대다.** 이 글은 그 둘을 갈라놓는 데서 시작한다.

## 같은 이름, 다른 역할 두 개

DNS 서버라는 단일한 대상은 없다. 이름만 같고 하는 일이 완전히 다른 두 종류가 있다.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 344" role="img" aria-label="리졸버는 원본을 갖고 있지 않고 캐시의 사본으로 답하거나 대신 찾아 나서는 쪽이고, 권한 네임서버는 원본을 보관하고 자기 것만 답하는 쪽이다">
    <rect x="16" y="12" width="330" height="282" rx="12" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="40" y="52" font-size="18" font-weight="700" fill="currentColor">리졸버 <tspan dx="8" font-size="12.5" font-weight="400" fill="var(--secondary)">Resolver</tspan></text>
    <text x="40" y="76" font-size="13" fill="var(--secondary)">묻는 쪽 · 내 질문을 대신 처리한다</text>
    <line x1="40" y1="92" x2="322" y2="92" stroke="var(--tertiary)" stroke-width="1" opacity="0.6"/>
    <text x="40" y="124" font-size="13.5" fill="currentColor">원본을 갖고 있지 않다</text>
    <text x="40" y="156" font-size="13.5" fill="currentColor">캐시에 사본이 있으면 그걸로 답한다</text>
    <text x="40" y="188" font-size="13.5" fill="currentColor">없으면 대신 찾아 나선다</text>
    <text x="40" y="220" font-size="13.5" fill="currentColor">내 컴퓨터 설정에서 내가 고른다</text>
    <text class="m" x="40" y="266" font-size="13" fill="var(--secondary)">1.1.1.1 · 8.8.8.8 · 통신사</text>
    <rect x="374" y="12" width="330" height="282" rx="12" fill="var(--dgm-accent)"/>
    <text x="398" y="52" font-size="18" font-weight="700" fill="#fff">권한 네임서버 <tspan dx="8" font-size="12.5" font-weight="400" fill="rgba(255,255,255,.7)">Authoritative Nameserver</tspan></text>
    <text x="398" y="76" font-size="13" fill="rgba(255,255,255,.82)">답하는 쪽 · 최종 답을 보관한다</text>
    <line x1="398" y1="92" x2="680" y2="92" stroke="rgba(255,255,255,.35)" stroke-width="1"/>
    <text x="398" y="124" font-size="13.5" fill="#fff">원본을 갖고 있다</text>
    <text x="398" y="156" font-size="13.5" fill="#fff">찾아주지 않는다. 자기 것만 답한다</text>
    <text x="398" y="188" font-size="13.5" fill="#fff">원본이라 캐시가 없다</text>
    <text x="398" y="220" font-size="13.5" fill="#fff">도메인 주인이 지정한다</text>
    <text class="m" x="398" y="266" font-size="13" fill="rgba(255,255,255,.82)">david.ns.cloudflare.com</text>
    <text x="16" y="330" font-size="13.5" fill="var(--secondary)">"DNS 서버 바꿔라"와 "네임서버 바꿔라"는 서로 반대편 이야기다.</text>
  </svg>
  </div>
  <figcaption><p><strong>리졸버</strong>는 내가 누구에게 묻느냐, <strong>권한 네임서버</strong>는 세상이 내 도메인을 누구에게 묻느냐다.</p></figcaption>
</figure>

그래서 고치는 곳도 다르다. 리졸버는 내 노트북의 네트워크 설정에서 바꾸고 나만 영향을 받는다. 권한 네임서버는 도메인 관리 화면에서 바꾸고 전 세계가 영향을 받는다.

구별하는 방법은 [「도메인 등록, 그림으로 이해하기」](/posts/how-domains-get-registered/)에서 이미 봤다. `dig` 응답 헤더의 `;; flags:` 줄에 `aa`(authoritative answer)가 찍혀 있으면 원본이 직접 준 답이고, 없으면 리졸버 캐시에서 꺼낸 사본이다.

## DNS 질의는 네 층을 거친다

그런데 리졸버도 한 층이 아니다. 내 컴퓨터 안에도 작은 리졸버가 하나 더 있다.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 452" role="img" aria-label="DNS 질의는 브라우저, OS 스텁 리졸버, 재귀 리졸버, 권한 네임서버 네 층을 차례로 거친다">
    <defs>
      <marker id="n2a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
      <marker id="n2b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-go)"/></marker>
    </defs>
    <path d="M112,20 L96,20 L96,196 L112,196" fill="none" stroke="var(--dgm-accent)" stroke-width="2"/>
    <text x="80" y="108" font-size="12.5" font-weight="700" fill="var(--dgm-accent)" text-anchor="middle" transform="rotate(-90 80 108)">내 컴퓨터 안</text>
    <rect x="118" y="14" width="392" height="76" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="142" y="46" font-size="16" font-weight="700" fill="currentColor">브라우저</text>
    <text x="142" y="70" font-size="12.5" fill="var(--secondary)">자체 DNS 캐시를 따로 갖고 있다</text>
    <line x1="314" y1="90" x2="314" y2="116" stroke="currentColor" stroke-width="2" marker-end="url(#n2a)"/>
    <rect x="118" y="120" width="392" height="76" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="142" y="152" font-size="16" font-weight="700" fill="currentColor">스텁 리졸버 · OS<tspan dx="7" font-size="12" font-weight="400" fill="var(--secondary)">Stub Resolver</tspan></text>
    <text x="142" y="176" font-size="12.5" fill="var(--secondary)">찾지 않는다. 캐시를 보고 없으면 떠넘긴다</text>
    <line x1="314" y1="196" x2="314" y2="222" stroke="currentColor" stroke-width="2" marker-end="url(#n2a)"/>
    <rect x="118" y="226" width="392" height="76" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="142" y="258" font-size="16" font-weight="700" fill="currentColor">재귀 리졸버 <tspan dx="7" font-size="12" font-weight="400" fill="var(--secondary)">Recursive Resolver</tspan></text>
    <text x="142" y="282" font-size="12.5" fill="var(--secondary)">여기서부터 진짜로 찾아 나선다</text>
    <line x1="314" y1="302" x2="314" y2="328" stroke="currentColor" stroke-width="2" marker-end="url(#n2a)"/>
    <rect x="118" y="332" width="392" height="76" rx="10" fill="var(--dgm-accent)"/>
    <text x="142" y="364" font-size="16" font-weight="700" fill="#fff">권한 네임서버 <tspan dx="7" font-size="12" font-weight="400" fill="rgba(255,255,255,.7)">Authoritative Nameserver</tspan></text>
    <text x="142" y="388" font-size="12.5" fill="rgba(255,255,255,.82)">원본이 여기 있다</text>
    <path d="M600,40 L600,264 L518,264" fill="none" stroke="var(--dgm-go)" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#n2b)"/>
    <text class="m" x="600" y="28" font-size="14" font-weight="700" fill="var(--dgm-go)" text-anchor="middle">dig</text>
    <text x="624" y="152" font-size="12.5" font-weight="700" fill="var(--dgm-go)" text-anchor="middle" transform="rotate(-90 624 152)">위 두 층을 건너뛴다</text>
    <text x="16" y="440" font-size="13.5" fill="var(--secondary)">캐시가 층마다 따로 있다. 하나를 비워도 다른 층이 옛 답을 들고 있을 수 있다.</text>
  </svg>
  </div>
  <figcaption><p>스텁(stub)은 그루터기라는 뜻이다. 스텁 리졸버는 직접 찾아 나서는 기능을 뺀 채, 캐시를 확인하고 없으면 재귀 리졸버에 질의를 넘긴 뒤 그 답을 프로그램에 돌려주는 일만 한다.</p></figcaption>
</figure>

[「도메인 사서 웹페이지 붙이기, 실제로 해봤다」](/posts/buying-a-domain-in-practice/)에서 제일 오래 붙잡았던 문제가 정확히 이 그림이다. 같은 컴퓨터에서 같은 시각에 `dig byeorim.com A`는 IP를 제대로 뱉는데 `curl https://byeorim.com`은 `Could not resolve host`로 실패했다. `dig`는 재귀 리졸버에 DNS 패킷을 직접 쏘고, `curl`은 `getaddrinfo()`를 거쳐 OS에 물어본다. macOS라면 그 요청을 `mDNSResponder`가 받아 자기 캐시부터 본다. `dig`와 `curl`은 서로 다른 층에 묻고, 층마다 캐시가 따로 있다. 한 층의 캐시에 만료되지 않은 옛 응답이 남아 있으면 그 층을 지나는 경로만 계속 그 옛 응답을 받는다. 그때 `mDNSResponder`의 캐시에 들어 있던 것이 "A 레코드 없음"이었고, `dig`는 그 캐시를 건너뛰었기 때문에 같은 이름에 서로 다른 답이 나온 것이다.

## 존: 네임서버가 책임지는 구역

권한 네임서버가 원본을 갖고 답하는 단위는 도메인 하나가 아니라 **존(zone)** 이다. 존 하나에는 여러 이름이 들어 있고, 네임서버는 그 존에 든 이름 전부를 책임진다.

도메인 이름은 점으로 나뉜 계층이다. 계층을 트리로 표현한다면, 도메인의 오른쪽이 트리의 위다. `www.byeorim.com`은 사실 맨 끝에 점이 하나 더 있다. `www.byeorim.com.` 그 마지막 점이 루트다.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 402" role="img" aria-label="루트, .com, byeorim.com으로 내려가는 이름 트리를 점선으로 자른 조각이 각각의 존이다">
    <rect x="296" y="4" width="128" height="64" rx="10" fill="none" stroke="var(--dgm-accent)" stroke-width="1.5" stroke-dasharray="5 4"/>
    <rect x="310" y="14" width="100" height="44" rx="8" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text class="m" x="360" y="44" font-size="20" fill="currentColor" text-anchor="middle">.</text>
    <text x="436" y="40" font-size="12.5" font-weight="700" fill="var(--dgm-accent)">루트 존 <tspan dx="6" font-size="10.5" font-weight="400" fill="var(--secondary)">Root Zone</tspan></text>
    <line x1="360" y1="68" x2="250" y2="106" stroke="var(--tertiary)" stroke-width="1.5"/>
    <line x1="360" y1="68" x2="490" y2="106" stroke="var(--tertiary)" stroke-width="1.5"/>
    <rect x="181" y="100" width="138" height="64" rx="10" fill="none" stroke="var(--dgm-accent)" stroke-width="1.5" stroke-dasharray="5 4"/>
    <rect x="195" y="110" width="110" height="44" rx="8" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text class="m" x="250" y="139" font-size="15" fill="currentColor" text-anchor="middle">.com</text>
    <text x="172" y="136" font-size="12.5" font-weight="700" fill="var(--dgm-accent)" text-anchor="end">.com 존</text>
    <rect x="421" y="100" width="138" height="64" rx="10" fill="none" stroke="var(--dgm-accent)" stroke-width="1.5" stroke-dasharray="5 4"/>
    <rect x="435" y="110" width="110" height="44" rx="8" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text class="m" x="490" y="139" font-size="15" fill="currentColor" text-anchor="middle">.kr</text>
    <text x="568" y="136" font-size="12.5" font-weight="700" fill="var(--dgm-accent)">.kr 존</text>
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
    <text x="292" y="288" font-size="12.5" font-weight="700" fill="var(--dgm-accent)">byeorim.com 존</text>
    <text x="292" y="310" font-size="12.5" fill="var(--secondary)">서브도메인은 대개</text>
    <text x="292" y="330" font-size="12.5" fill="var(--secondary)">같은 존 안에 있다</text>
    <text x="16" y="386" font-size="13.5" fill="var(--secondary)">존은 도메인이 아니라 "한 관리자가 통째로 책임지는 덩어리"다.</text>
  </svg>
  </div>
  <figcaption><p>트리를 점선으로 자른 조각 하나가 존이고, 그 조각마다 담당 네임서버가 따로 있다.</p></figcaption>
</figure>

여기서 갈리는 지점이 하나 있다. **도메인과 존은 같은 말이 아니다.** `blog.byeorim.com`은 보통 `byeorim.com` 존 안에 그냥 레코드로 들어 있지만 원하면 잘라내서 별도 존으로 만들고 다른 네임서버에 맡길 수도 있다. 회사에서 팀별로 서브도메인을 떼어주는 게 그 방식이다.

## 위임: NS 레코드는 두 벌 있다

부모 존이 자식 존에게 "이 아래는 네가 답해라"라고 넘기는 것이 **위임(delegation)** 이고, 그 답을 맡길 네임서버를 적어둔 것이 **NS 레코드**다.

그런데 같은 NS 레코드가 부모에도 있고 자식에도 있다. 처음 보면 중복 같은데 성격이 완전히 다르다.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 378" role="img" aria-label="부모 존의 NS 레코드는 권한이 없고 자식 존의 NS 레코드는 권한이 있지만, 리졸버가 실제로 따라가는 것은 부모 쪽이다">
    <defs>
      <marker id="n4a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-go)"/></marker>
    </defs>
    <rect x="16" y="36" width="336" height="256" rx="12" fill="var(--dgm-accent)"/>
    <text x="40" y="70" font-size="17" font-weight="700" fill="#fff">.com 존 · 부모 <tspan dx="7" font-size="12" font-weight="400" fill="rgba(255,255,255,.7)">Parent</tspan></text>
    <text x="40" y="92" font-size="12.5" fill="rgba(255,255,255,.82)">Verisign이 갖고 있다</text>
    <line x1="40" y1="106" x2="328" y2="106" stroke="rgba(255,255,255,.35)" stroke-width="1"/>
    <text class="m" x="40" y="134" font-size="12" fill="rgba(255,255,255,.9)">byeorim.com NS david.ns…</text>
    <text x="40" y="164" font-size="13" fill="#fff">AUTHORITY 섹션 · aa 없음</text>
    <text x="40" y="192" font-size="13" fill="#fff">TTL 172800 = 2일</text>
    <text x="40" y="224" font-size="14.5" font-weight="700" fill="#fff">답이 아니라 다음에 물을 서버다</text>
    <text x="40" y="264" font-size="12.5" fill="rgba(255,255,255,.82)">이 NS 레코드를 고치는 곳: 레지스트라 화면</text>
    <rect x="368" y="36" width="336" height="256" rx="12" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="392" y="70" font-size="17" font-weight="700" fill="currentColor">byeorim.com 존 · 자식 <tspan dx="7" font-size="12" font-weight="400" fill="var(--secondary)">Child</tspan></text>
    <text x="392" y="92" font-size="12.5" fill="var(--secondary)">Cloudflare가 갖고 있다</text>
    <line x1="392" y1="106" x2="680" y2="106" stroke="var(--tertiary)" stroke-width="1" opacity="0.6"/>
    <text class="m" x="392" y="134" font-size="12" fill="currentColor">byeorim.com NS david.ns…</text>
    <text x="392" y="164" font-size="13" fill="currentColor">ANSWER 섹션 · aa 있음</text>
    <text x="392" y="192" font-size="13" fill="currentColor">TTL 86400 = 1일</text>
    <text x="392" y="224" font-size="14.5" font-weight="700" fill="currentColor">이 존에 대해 권한을 가진 답이다</text>
    <text x="392" y="264" font-size="12.5" fill="var(--secondary)">이 NS 레코드를 고치는 곳: DNS 관리 화면</text>
    <path d="M184,16 L184,30" fill="none" stroke="var(--dgm-go)" stroke-width="2" marker-end="url(#n4a)"/>
    <text x="204" y="24" font-size="12.5" font-weight="700" fill="var(--dgm-go)">리졸버는 위에서 내려온다. 이쪽만 읽고 간다</text>
    <text x="16" y="336" font-size="13.5" fill="var(--secondary)">byeorim.com의 NS 값은 부모와 자식이 같은데, 위치도 TTL도 권한도 다르다.</text>
    <text x="16" y="358" font-size="13.5" fill="var(--secondary)">그리고 리졸버가 그 NS로 질의를 보내도록 결정하는 것은 왼쪽이다.</text>
  </svg>
  </div>
  <figcaption><p>byeorim.com에 대한 응답 권한이 있는 쪽은 오른쪽이지만, 두 곳에 적힌 NS 레코드 중 실제로 쓰이는 것은 왼쪽 곧 부모 존에 저장된 레코드다.</p></figcaption>
</figure>

직접 양쪽에 물어보면 차이가 그대로 보인다.

```
$ dig @a.gtld-servers.net byeorim.com NS        # 부모 .com 에게
;; flags: qr rd;                                ← aa 없음
;; AUTHORITY SECTION:
byeorim.com.  172800  IN  NS  david.ns.cloudflare.com.
byeorim.com.  172800  IN  NS  kami.ns.cloudflare.com.

$ dig @david.ns.cloudflare.com byeorim.com NS   # 자식 존에게
;; flags: qr aa rd;                             ← aa 있음
;; ANSWER SECTION:
byeorim.com.  86400   IN  NS  david.ns.cloudflare.com.
byeorim.com.  86400   IN  NS  kami.ns.cloudflare.com.
```

값은 글자 하나까지 같다. 다른 건 셋이다.

- **섹션.** 부모는 `AUTHORITY`(다음에 물을 서버), 자식은 `ANSWER`(답).
- **`aa` 플래그.** 부모에게는 없다. `.com` 서버는 `byeorim.com`에 대해 권한이 없다.
- **TTL.** 부모는 2일, 자식은 1일. 서로 다른 사람이 정한 값이라 같을 이유가 없다.

그리고 결론이 여기서 나온다. **리졸버는 항상 상위 존에서부터 내려오기 때문에, 부모 존의 NS 레코드를 보고 거기 적힌 서버에 다음 질의를 한다.** 자식 존에 적힌 NS는 실전에서 거의 읽히지 않는다. 그래서 네임서버를 바꾸는 일은 DNS 관리 화면이 아니라 **레지스트라(registrar) 화면**에서 한다. 부모 존을 고쳐야 하고, 부모 존은 레지스트리(registry)만 쓸 수 있고, 레지스트리에 요청을 넣을 수 있는 건 레지스트라뿐이다.

둘이 어긋난 상태를 **lame delegation**이라고 부른다. 부모 존의 NS 레코드는 네임서버 A를 가리키는데, 정작 A에는 그 존의 데이터가 없어서 권한 있는 답을 못 하는 경우다. NS가 여러 대일 때 리졸버가 하필 A를 고른 질의만 실패하기 때문에, 도메인이 됐다 안 됐다 하는 고약한 증상으로 나타난다.

## 글루: 부모가 네임서버의 IP까지 함께 주는 이유

네임서버 이름이 자기가 책임지는 도메인 안에 들어 있으면 위임에 순환이 생긴다. `google.com`의 네임서버 이름이 `ns1.google.com`인 경우가 그렇다.

리졸버 입장에서 따라가 보면 이렇다. `.com` 서버가 "`google.com`은 `ns1.google.com`에 물어봐"라고 알려준다. 그 서버에 질의를 보내려면 `ns1.google.com`의 IP가 필요하다. IP를 알려면 `ns1.google.com`의 A 레코드를 조회해야 하는데, 그 A 레코드는 `google.com` 존 안에 들어 있다. 그리고 `google.com` 존에 답할 수 있는 서버는 다시 `ns1.google.com`이다. **질의를 보내려면 그 질의의 답이 이미 있어야 하는 상태**라 리졸버는 한 발도 못 나간다.

부모 존이 이 고리를 끊는다. `.com` 서버는 위임을 알려줄 때 `ns1.google.com`의 IP를 응답의 `ADDITIONAL` 섹션에 함께 실어 보낸다. 이렇게 딸려 오는 IP가 **글루 레코드**(glue record)다. 리졸버는 A 레코드를 따로 조회하지 않고 그 주소로 바로 질의한다.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 336" role="img" aria-label="네임서버 이름이 자기 도메인 안에 있으면 주소를 알 수 없는 순환이 생기고 부모가 주소를 함께 주는 글루 레코드가 그것을 끊는다">
    <defs>
      <marker id="n5a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-stop)"/></marker>
    </defs>
    <text x="16" y="28" font-size="13" font-weight="700" fill="var(--secondary)">① 순환</text>
    <rect x="30" y="40" width="290" height="72" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text class="m" x="175" y="74" font-size="13.5" fill="currentColor" text-anchor="middle">ns1.google.com</text>
    <text x="175" y="96" font-size="12.5" fill="var(--secondary)" text-anchor="middle">에 물어보려면</text>
    <line x1="326" y1="76" x2="396" y2="76" stroke="var(--dgm-stop)" stroke-width="2" marker-end="url(#n5a)"/>
    <rect x="402" y="40" width="290" height="72" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="547" y="74" font-size="13.5" fill="currentColor" text-anchor="middle">그 이름의 IP를</text>
    <text x="547" y="96" font-size="12.5" fill="var(--secondary)" text-anchor="middle">먼저 알아야 한다</text>
    <path d="M547,116 C547,152 175,152 175,118" fill="none" stroke="var(--dgm-stop)" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#n5a)"/>
    <text x="360" y="176" font-size="13" font-weight="700" fill="var(--dgm-stop)" text-anchor="middle">그런데 그 IP는 google.com 존 안에 있다</text>
    <text x="16" y="216" font-size="13" font-weight="700" fill="var(--secondary)">② 글루</text>
    <rect x="30" y="228" width="662" height="66" rx="10" fill="var(--dgm-accent)"/>
    <text x="54" y="256" font-size="15" font-weight="700" fill="#fff">부모 존이 위임과 함께 그 IP를 같이 얹어 준다</text>
    <text x="54" y="280" font-size="12.5" fill="rgba(255,255,255,.82)">위임 정보를 붙여주는 접착제라서 glue record</text>
    <text x="16" y="326" font-size="13.5" fill="var(--secondary)">네임서버 이름을 자기 도메인 안에 두면 글루가 필수, 남의 도메인에 두면 불필요.</text>
  </svg>
  </div>
  <figcaption><p>글루 레코드는 자식 존이 아니라 부모 존에 저장된다. 그래서 이 IP를 바꾸는 것도 레지스트라 화면에서 한다.</p></figcaption>
</figure>

`.com` 서버가 실제로 그렇게 준다.

```
$ dig @a.gtld-servers.net google.com NS
;; AUTHORITY SECTION:
google.com.      172800  IN  NS  ns1.google.com.
google.com.      172800  IN  NS  ns2.google.com.
;; ADDITIONAL SECTION:
ns1.google.com.  172800  IN  A   216.239.32.10      ← 글루
ns2.google.com.  172800  IN  A   216.239.34.10
```

`byeorim.com`은 이 문제가 없다. 네임서버 이름이 `david.ns.cloudflare.com`, **남의 도메인 안**이라 순환이 생기지 않는다. 리졸버가 `cloudflare.com`을 따로 한 번 더 조회하면 그만이다.

그래서 Cloudflare나 가비아 같은 서비스도 자기 도메인의 네임서버를 빌려준다. 순환이 없으니 글루를 관리할 일도 없다.

## 한 번의 질의를 끝까지 따라가기

`dig +trace`는 리졸버를 안 쓰고 **`dig`가 직접 루트부터 한 계단씩 내려간다.** 평소에 리졸버가 대신 해주는 일을 눈으로 보여주는 셈이다.

```
$ dig +trace byeorim.com A

.             389730  IN  NS  a.root-servers.net.  …          ← 루트 서버 목록부터
;; Received 1109 bytes from 168.126.63.1#53 in 6 ms

com.          172800  IN  NS  a.gtld-servers.net.  …          ← ".com은 저쪽"
;; Received 1171 bytes from 192.33.4.12#53(c.root-servers.net) in 133 ms

byeorim.com.  172800  IN  NS  david.ns.cloudflare.com.        ← "그 도메인은 저쪽"
byeorim.com.  172800  IN  NS  kami.ns.cloudflare.com.
;; Received 504 bytes from 192.12.94.30#53(e.gtld-servers.net) in 38 ms

byeorim.com.  300     IN  A   104.21.81.254                   ← 드디어 답
byeorim.com.  300     IN  A   172.67.192.105
;; Received 179 bytes from 173.245.58.177#53(kami.ns.cloudflare.com) in 7 ms
```

네 덩어리가 각각 다른 서버에서 왔다는 게 `Received … from` 줄에 그대로 찍힌다. 그리고 앞의 세 덩어리는 **답이 아니다.** "나는 모르니 저쪽에 물어봐"라는 것이고 이걸 **참조(referral)** 라고 부른다.

읽을 때 눈여겨볼 게 두 가지 있다.

첫 줄의 루트 서버 목록은 내 통신사 리졸버 `168.126.63.1`에서 왔다. `dig`도 시작점은 어딘가에서 받아와야 한다. 그리고 마지막 답의 TTL만 `300`이다. 위임 정보는 며칠을 가고 실제 주소는 5분이다. 이 차이가 다음 절의 주제다.

## 캐시는 최종 답만 담지 않는다

리졸버가 캐시하는 건 `byeorim.com → IP` 한 줄이 아니다. **내려오는 길에 받은 참조를 전부 담는다.**

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 330" role="img" aria-label="리졸버 캐시에는 루트 NS, .com NS, byeorim.com NS, 그리고 최종 A 레코드가 각각 다른 수명으로 들어 있다">
    <defs>
      <marker id="n6a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-stop)"/></marker>
    </defs>
    <rect x="16" y="40" width="400" height="238" rx="12" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="40" y="74" font-size="16" font-weight="700" fill="currentColor">리졸버 캐시</text>
    <line x1="40" y1="90" x2="392" y2="90" stroke="var(--tertiary)" stroke-width="1" opacity="0.6"/>
    <text class="m" x="40" y="122" font-size="13" fill="var(--secondary)">. NS</text>
    <text x="392" y="122" font-size="13" fill="var(--secondary)" text-anchor="end">6일</text>
    <text class="m" x="40" y="160" font-size="13" fill="var(--secondary)">com. NS</text>
    <text x="392" y="160" font-size="13" fill="var(--secondary)" text-anchor="end">2일</text>
    <text class="m" x="40" y="198" font-size="13" fill="var(--secondary)">byeorim.com NS</text>
    <text x="392" y="198" font-size="13" fill="var(--secondary)" text-anchor="end">2일</text>
    <line x1="40" y1="216" x2="392" y2="216" stroke="var(--tertiary)" stroke-width="1" opacity="0.6"/>
    <text class="m" x="40" y="248" font-size="13" font-weight="700" fill="var(--dgm-stop)">byeorim.com A</text>
    <text x="392" y="248" font-size="13" font-weight="700" fill="var(--dgm-stop)" text-anchor="end">5분</text>
    <path d="M424,110 L440,110 L440,200 L424,200" fill="none" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="460" y="146" font-size="13" fill="currentColor">이 셋이 살아 있는 동안</text>
    <text x="460" y="170" font-size="13" font-weight="700" fill="currentColor">루트도 .com도 다시 안 간다</text>
    <line x1="420" y1="243" x2="452" y2="243" stroke="var(--dgm-stop)" stroke-width="2" marker-end="url(#n6a)"/>
    <text x="462" y="240" font-size="13" font-weight="700" fill="var(--dgm-stop)">여기만 5분마다 만료된다</text>
    <text x="462" y="262" font-size="12.5" fill="var(--secondary)">→ 대개 마지막 한 번만 나간다</text>
    <text x="16" y="312" font-size="13.5" fill="var(--secondary)">"질문 세 번"짜리 그림은 실전에서 거의 일어나지 않는다.</text>
  </svg>
  </div>
  <figcaption><p>NS 레코드는 TTL이 며칠이라 캐시에 오래 남는다. 자주 만료돼 다시 조회되는 것은 TTL이 300초인 A 레코드뿐이다.</p></figcaption>
</figure>

캐시를 훔쳐볼 수 있다. `+norecurse`는 **"찾아오지 말고 지금 갖고 있는 것만 내놔"** 라는 뜻이다.

```
$ dig +norecurse @168.126.63.1 com. NS      # 내 통신사 리졸버의 캐시
com.  44878   IN  NS  d.gtld-servers.net.

$ dig @a.gtld-servers.net com. NS           # 원본
com.  172800  IN  NS  m.gtld-servers.net.
```

원본은 172800초(2일)인데 내 리졸버에는 44878초만 남았다. 뺄셈이 곧 나이다. **약 35시간 전에 담긴 사본**이다.

12초 뒤에 다시 물으면 이렇다.

```
com.  44866   IN  NS  h.gtld-servers.net.
```

정확히 12만큼 줄었다. **TTL은 남은 수명을 실시간으로 세는 카운터다. 고정된 설정값이 아니다.** 응답에 찍힌 숫자가 300이 아니라 어중간한 값이면, 그건 캐시에서 온 사본이라는 뜻이다.

## 바꾼 레코드는 퍼지지 않는다. 리졸버 캐시가 만료될 뿐이다

내 도메인의 DNS 설정을 바꾸면 "전파에 48시간 걸린다"고들 한다. 그런데 그 48시간 동안 **권한 네임서버는 아무 데에도 아무것도 보내지 않는다.**

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 322" role="img" aria-label="권한 네임서버가 변경 내용을 밀어내는 것이 아니라 각 리졸버의 캐시가 제각기 만료되어 다시 물으러 오는 것이다">
    <defs>
      <marker id="n7a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-stop)"/></marker>
      <marker id="n7b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-go)"/></marker>
    </defs>
    <line x1="360" y1="10" x2="360" y2="270" stroke="var(--tertiary)" stroke-width="1" stroke-dasharray="4 4"/>
    <text x="176" y="26" font-size="14" font-weight="700" fill="var(--dgm-stop)" text-anchor="middle">우리가 상상하는 것</text>
    <text x="540" y="26" font-size="14" font-weight="700" fill="var(--dgm-go)" text-anchor="middle">실제로 일어나는 것</text>
    <rect x="56" y="46" width="240" height="48" rx="8" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="176" y="76" font-size="13.5" fill="currentColor" text-anchor="middle">권한 네임서버</text>
    <line x1="176" y1="94" x2="76" y2="196" stroke="var(--dgm-stop)" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#n7a)"/>
    <line x1="176" y1="94" x2="176" y2="196" stroke="var(--dgm-stop)" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#n7a)"/>
    <line x1="176" y1="94" x2="276" y2="196" stroke="var(--dgm-stop)" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#n7a)"/>
    <line x1="40" y1="146" x2="312" y2="146" stroke="var(--dgm-stop)" stroke-width="2"/>
    <line x1="160" y1="130" x2="192" y2="162" stroke="var(--dgm-stop)" stroke-width="3.5" stroke-linecap="round"/>
    <line x1="192" y1="130" x2="160" y2="162" stroke="var(--dgm-stop)" stroke-width="3.5" stroke-linecap="round"/>
    <rect x="36" y="200" width="80" height="40" rx="8" fill="none" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="76" y="225" font-size="12" fill="var(--secondary)" text-anchor="middle">리졸버 A</text>
    <rect x="136" y="200" width="80" height="40" rx="8" fill="none" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="176" y="225" font-size="12" fill="var(--secondary)" text-anchor="middle">리졸버 B</text>
    <rect x="236" y="200" width="80" height="40" rx="8" fill="none" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="276" y="225" font-size="12" fill="var(--secondary)" text-anchor="middle">리졸버 C</text>
    <text x="176" y="264" font-size="12.5" font-weight="700" fill="var(--dgm-stop)" text-anchor="middle">권한 네임서버가 변경을 밀어 보내지 않는다</text>
    <rect x="392" y="46" width="86" height="44" rx="8" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="435" y="73" font-size="12.5" fill="currentColor" text-anchor="middle">리졸버 A</text>
    <rect x="496" y="46" width="86" height="44" rx="8" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="539" y="73" font-size="12.5" fill="currentColor" text-anchor="middle">리졸버 B</text>
    <rect x="600" y="46" width="86" height="44" rx="8" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="643" y="73" font-size="12.5" fill="currentColor" text-anchor="middle">리졸버 C</text>
    <text x="435" y="110" font-size="12" fill="var(--secondary)" text-anchor="middle">5분 뒤 만료</text>
    <text x="539" y="110" font-size="12" fill="var(--secondary)" text-anchor="middle">1시간 뒤</text>
    <text x="643" y="110" font-size="12" fill="var(--secondary)" text-anchor="middle">이틀 뒤</text>
    <line x1="435" y1="120" x2="500" y2="192" stroke="var(--dgm-go)" stroke-width="2" marker-end="url(#n7b)"/>
    <line x1="539" y1="120" x2="539" y2="192" stroke="var(--dgm-go)" stroke-width="2" marker-end="url(#n7b)"/>
    <line x1="643" y1="120" x2="578" y2="192" stroke="var(--dgm-go)" stroke-width="2" marker-end="url(#n7b)"/>
    <rect x="420" y="196" width="240" height="48" rx="8" fill="var(--dgm-accent)"/>
    <text x="540" y="226" font-size="13.5" font-weight="700" fill="#fff" text-anchor="middle">권한 네임서버</text>
    <text x="540" y="264" font-size="12.5" font-weight="700" fill="var(--dgm-go)" text-anchor="middle">각자 만료되면 각자 되물으러 온다</text>
    <text x="16" y="302" font-size="13.5" fill="var(--secondary)">"전파 48시간"의 정체는 부모 NS 레코드의 TTL 172800초다.</text>
  </svg>
  </div>
  <figcaption><p>전파(propagation)가 아니라 만료(expiry)다. 화살표 방향이 반대다.</p></figcaption>
</figure>

원본은 저장하는 즉시 바뀐다. 전 세계 리졸버는 각자 다시 물으러 온다. 그 시점은 자기가 담아둔 사본이 만료될 때다. 만료 시각이 제각각이라 **같은 시간에 어떤 사람은 새 답을, 어떤 사람은 옛 답을 본다.**

그래서 최대 지연은 내가 바꾼 레코드의 TTL이다. `byeorim.com`의 A 레코드를 바꿨다면 그 레코드의 TTL인 300초, 도메인의 네임서버 자체를 바꿨다면 부모 존에 적힌 NS 레코드의 TTL인 172800초(2일)다. "48시간"이라는 관용어의 출처는 뒤쪽이다.

A 레코드도 사정이 다르지 않다. 새 IP를 저장하는 순간 권한 네임서버의 답은 바뀌지만, **방문자는 권한 네임서버에 직접 묻지 않는다.** 자기 리졸버에 묻고, 그 리졸버는 옛 IP를 이미 사본으로 들고 있다. 그 사본이 만료되기 전까지는 다시 물어보지 않으므로 계속 옛 서버로 간다. TTL이 86400초(하루)였다면 최대 하루 동안 방문자마다 새 서버와 옛 서버로 갈린다.

요령은 [「도메인 등록, 그림으로 이해하기」](/posts/how-domains-get-registered/)에도 썼지만 이유가 여기서 분명해진다. **서버를 옮길 예정이면 며칠 전에 그 A 레코드의 TTL을 300초로 줄여둔다.** 그러면 이사하는 시점에 세상이 들고 있는 사본의 수명이 전부 5분 이하라, IP를 바꾸고 5분이면 정리된다. "며칠 전"이어야 하는 이유는 TTL 값 자체도 레코드에 실려 나가기 때문이다. 옛 86400초짜리 사본을 쥔 리졸버는 하루가 지나 다시 물어봐야 300이라는 새 값을 받는다. 이사 당일에 줄이면 그 리졸버들에게는 아직 옛 TTL이 걸려 있다.

다만 이렇게 미리 줄일 수 있는 것은 **내 존 안에 있는 레코드의 TTL뿐이다.** A 레코드처럼 DNS 관리 화면에서 내가 값을 정하는 것들이다. **부모 존에 적힌 NS 레코드의 TTL은 레지스트리가 정하고 도메인 주인은 바꿀 수 없다.** `.com`은 172800초로 고정이다. 자식 존에도 NS 레코드가 있고 그쪽 TTL은 내가 정할 수 있지만, 리졸버가 따라가는 것은 부모 쪽이라 소용이 없다. 그래서 네임서버를 통째로 바꿀 때만큼은 미리 줄여둘 방법이 없다. 옛 네임서버가 같은 답을 계속 주도록 남겨둔 채 최대 2일을 기다리는 수밖에 없다.

## 네임서버가 최소 두 대인 이유

`byeorim.com`의 NS는 `david`와 `kami` 둘이었다. 대부분의 레지스트리가 최소 두 개를 요구한다.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 356" role="img" aria-label="리졸버는 여러 네임서버 중 아무거나 고르고, 각 네임서버 이름 뒤에는 여러 IP가, 각 IP 뒤에는 애니캐스트로 흩어진 여러 지역이 있다">
    <defs>
      <marker id="n8a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
    </defs>
    <rect x="16" y="56" width="140" height="64" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="86" y="94" font-size="14" font-weight="700" fill="currentColor" text-anchor="middle">리졸버</text>
    <line x1="162" y1="76" x2="214" y2="52" stroke="currentColor" stroke-width="2" marker-end="url(#n8a)"/>
    <line x1="162" y1="100" x2="214" y2="142" stroke="currentColor" stroke-width="2" marker-end="url(#n8a)"/>
    <rect x="220" y="22" width="280" height="56" rx="10" fill="var(--dgm-accent)"/>
    <text class="m" x="360" y="56" font-size="14" fill="#fff" text-anchor="middle">david.ns.cloudflare.com</text>
    <rect x="220" y="112" width="280" height="56" rx="10" fill="var(--dgm-accent)"/>
    <text class="m" x="360" y="146" font-size="14" fill="#fff" text-anchor="middle">kami.ns.cloudflare.com</text>
    <text x="516" y="46" font-size="12.5" fill="currentColor">순서에 의미가 없다</text>
    <text x="516" y="68" font-size="12.5" fill="var(--secondary)">아무거나 고른다</text>
    <text x="516" y="136" font-size="12.5" fill="currentColor">하나가 죽으면</text>
    <text x="516" y="158" font-size="12.5" fill="var(--secondary)">나머지로 넘어간다</text>
    <line x1="16" y1="196" x2="704" y2="196" stroke="var(--tertiary)" stroke-width="1" opacity="0.6"/>
    <text x="16" y="226" font-size="13.5" font-weight="700" fill="currentColor">그리고 IP 하나가 서버 한 대가 아니다</text>
    <rect x="16" y="244" width="180" height="48" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text class="m" x="106" y="274" font-size="13.5" fill="currentColor" text-anchor="middle">172.64.33.152</text>
    <line x1="202" y1="268" x2="232" y2="268" stroke="currentColor" stroke-width="2" marker-end="url(#n8a)"/>
    <rect x="240" y="248" width="140" height="40" rx="8" fill="none" stroke="var(--dgm-go)" stroke-width="1.5"/>
    <text x="310" y="273" font-size="13" fill="currentColor" text-anchor="middle">서울</text>
    <rect x="392" y="248" width="140" height="40" rx="8" fill="none" stroke="var(--dgm-go)" stroke-width="1.5"/>
    <text x="462" y="273" font-size="13" fill="currentColor" text-anchor="middle">프랑크푸르트</text>
    <rect x="544" y="248" width="140" height="40" rx="8" fill="none" stroke="var(--dgm-go)" stroke-width="1.5"/>
    <text x="614" y="273" font-size="13" fill="currentColor" text-anchor="middle">상파울루</text>
    <text x="16" y="322" font-size="13.5" fill="var(--secondary)">같은 IP를 세계 여러 데이터센터가 자기 것이라고 동시에 광고한다. 애니캐스트(anycast)다.</text>
    <text x="16" y="344" font-size="13.5" fill="var(--secondary)">라우터가 그중 가장 가까운 곳으로 보내므로, 목적지 IP는 같아도 도착하는 서버는 다르다.</text>
  </svg>
  </div>
  <figcaption><p>루트 서버 이름이 13개뿐인데 안 죽는 이유도 이것이다.</p></figcaption>
</figure>

NS가 여럿이면 리졸버는 **아무거나 고른다.** 적힌 순서에 우선순위 같은 건 없다. 대개 응답이 빨랐던 쪽을 기억해뒀다가 그것을 선택한다.

그럼 두 대가 어떻게 같은 답을 유지하나. 전통적인 방식은 한 대가 원본(primary)이고 나머지는 **존 전송**(zone transfer)으로 복사해 가는 것이다. 존 전체를 요청하는 질의 타입 이름이 `AXFR`이고, 바뀐 부분만 받아 오는 `IXFR`(incremental zone transfer)도 있다. 언제 복사할지는 존의 관리 정보를 담은 **SOA**(Start of Authority) 레코드의 **일련번호**로 판단한다.

```
$ dig +short byeorim.com SOA
david.ns.cloudflare.com. dns.cloudflare.com. 2413581597 10000 2400 604800 1800

  david.ns.cloudflare.com.    프라이머리 네임서버
  dns.cloudflare.com.         관리자 메일 주소
  2413581597                  일련번호 (serial)
  10000 · 2400 · 604800       refresh · retry · expire
  1800                        negative TTL
```

세컨더리(secondary)는 주기적으로 원본의 일련번호를 확인하고 숫자가 커졌으면 존을 통째로 받아 온다. 관리자 메일 주소에서 `@` 대신 점을 쓰는 건 DNS가 `@`를 다루지 못해서다. `dns.cloudflare.com`은 `dns@cloudflare.com`이라는 뜻이다.

Cloudflare 같은 대형 서비스는 내부적으로는 다르게 동작한다. 프라이머리와 세컨더리를 두고 존 전송으로 넘기는 대신, 자체 방식으로 존 데이터를 전 세계 노드에 배포한다. 그래도 밖에서 보이는 모습은 전통적인 구성과 같다. `david.ns.cloudflare.com`에 묻든 `kami.ns.cloudflare.com`에 묻든 응답에 `aa` 플래그가 붙는다.

여기서 `aa`가 보증하는 것은 **이 존에 대해 권한이 있는 서버가 직접 준 답**이라는 사실 하나다. 어느 쪽이 원본을 들고 있는 프라이머리인지는 말해주지 않는다. 세컨더리가 존 전송으로 받아 온 데이터로 답해도 `aa`는 똑같이 붙는다. 그래서 리졸버 입장에서는 NS 목록에 적힌 두 대가 완전히 대등하고, 어느 쪽을 고르든 캐시의 사본이 아닌 권한 있는 답을 받는다.

그리고 네임서버 이름 하나에 IP가 하나만 붙는 것도 아니다. 이름 하나에 A 레코드를 여럿 달아 둘 수 있고, `david.ns.cloudflare.com`이 그렇다.

```
$ dig +short david.ns.cloudflare.com A
108.162.193.152
172.64.33.152
173.245.59.152
```

IP가 셋이고, 그 각각이 다시 **애니캐스트**다. 보통은 IP 하나가 서버 한 대를 가리키지만, 애니캐스트에서는 세계 여러 데이터센터가 같은 IP를 자기 것이라고 동시에 광고한다. 인터넷 라우터는 그중 자기에게 가장 가까운 경로 하나를 골라 패킷을 보낸다. 그래서 서울에서 보낸 질의와 상파울루에서 보낸 질의는 목적지 IP가 같은데도 서로 다른 서버에 도착한다. 루트 서버가 `a`부터 `m`까지 13개 이름뿐인데도 감당이 되는 이유가 이것이다. 이름은 13개지만 실제 서버는 전 세계 수백 곳이다.

## "없다"는 답도 답이다

없는 도메인을 질의해도 리졸버는 침묵하는 대신 **없다는 사실을 명시적으로 답한다.** 그리고 그 "없다"는 답도 캐싱된다.

그리고 없음에는 두 종류가 있다.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 302" role="img" aria-label="이름 자체가 없는 NXDOMAIN과 이름은 있으나 그 타입이 없는 NODATA 두 가지가 있고 둘 다 SOA의 마지막 값만큼 캐싱된다">
    <rect x="16" y="16" width="336" height="152" rx="12" fill="var(--code-bg)" stroke="var(--dgm-stop)" stroke-width="2"/>
    <text x="40" y="52" font-size="17" font-weight="700" fill="currentColor">NXDOMAIN</text>
    <text x="40" y="76" font-size="13" fill="var(--secondary)">그런 이름 자체가 없다</text>
    <line x1="40" y1="92" x2="328" y2="92" stroke="var(--tertiary)" stroke-width="1" opacity="0.6"/>
    <text class="m" x="40" y="120" font-size="13" fill="currentColor">nope-xyz.google.com</text>
    <text class="m" x="40" y="148" font-size="12.5" fill="var(--dgm-stop)">status: NXDOMAIN</text>
    <rect x="368" y="16" width="336" height="152" rx="12" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="392" y="52" font-size="17" font-weight="700" fill="currentColor">NODATA</text>
    <text x="392" y="76" font-size="13" fill="var(--secondary)">이름은 있는데 그 타입이 없다</text>
    <line x1="392" y1="92" x2="680" y2="92" stroke="var(--tertiary)" stroke-width="1" opacity="0.6"/>
    <text class="m" x="392" y="120" font-size="13" fill="currentColor">byeorim.com MX</text>
    <text class="m" x="392" y="148" font-size="12.5" fill="var(--secondary)">NOERROR · ANSWER: 0</text>
    <rect x="16" y="192" width="688" height="66" rx="10" fill="var(--dgm-accent)"/>
    <text x="40" y="220" font-size="15" font-weight="700" fill="#fff">둘 다 캐싱된다. 수명은 SOA의 마지막 숫자</text>
    <text class="m" x="40" y="244" font-size="12.5" fill="rgba(255,255,255,.82)">… 604800 1800  ← 30분짜리 "없음"</text>
    <text x="16" y="292" font-size="13.5" fill="var(--secondary)">설정을 끝내기 전에 조회하면, 그 "없음"이 30분간 내 리졸버에 캐싱된다.</text>
  </svg>
  </div>
  <figcaption><p>"분명 설정했는데 왜 안 되지"의 가장 흔한 정체.</p></figcaption>
</figure>

```
$ dig @1.1.1.1 nope-xyz.google.com A
;; ->>HEADER<<- status: NXDOMAIN
;; AUTHORITY SECTION:
google.com.  60  IN  SOA  ns1.google.com. dns-admin.google.com. 973049826 900 900 1800 60
                                                                                       ^^
                                                                  없음의 수명 = 60초
```

없음의 답에는 **SOA 레코드가 딸려 온다.** 그 마지막 숫자가 이 "없음"을 얼마나 오래 믿을지를 정한다. `google.com`은 60초, `byeorim.com`(Cloudflare 기본값)은 1800초 = 30분이다. 이 숫자 때문에 [「도메인 사서 웹페이지 붙이기, 실제로 해봤다」](/posts/buying-a-domain-in-practice/)에서 30분을 날렸다. 설정을 마치기 전에 궁금해서 `byeorim.com`을 한 번 조회한 게 화근이었다. 그 한 번으로 "A 레코드 없음"이 리졸버에 30분짜리로 캐싱됐고, 설정을 다 끝낸 뒤에도 만료될 때까지 같은 답이 돌아왔다.

## 이것만은 기억하기

- **"DNS 서버"는 역할이 두 개다.** 내가 묻는 쪽(리졸버)과 세상이 내 도메인을 묻는 쪽(권한 네임서버). 설정 화면이 다르고, 영향 범위가 다르고, 고칠 수 있는 사람이 다르다.
- **NS 레코드는 부모에 있는 게 실제로 쓰인다.** 권한은 자식에 있지만 리졸버는 상위 존에서부터 내려오기 때문에 부모 존의 NS 레코드를 읽고 그 서버로 간다. 그래서 네임서버 변경은 레지스트라 화면에 있다.
- **바꾼 레코드는 퍼져 나가는 것이 아니라, 리졸버 캐시가 만료되면서 교체된다.** 권한 네임서버는 아무것도 밀어 보내지 않는다. 최대 지연은 바꾼 레코드의 TTL이다. 내 존 안의 레코드라면 며칠 전에 TTL을 줄여 그 지연을 짧게 만들 수 있고, 부모 존의 NS TTL은 바꿀 수 없으니 네임서버 교체는 기다리는 수밖에 없다.
- **없다는 답도 캐싱된다.** 설정을 끝내기 전에는 그 도메인을 조회하지 않는 게 낫다.

확인은 명령 네 줄이면 된다.

```
$ dig +trace <도메인>                      # 루트부터 한 계단씩
$ dig @<부모서버> <도메인> NS              # 실제로 쓰이는 위임
$ dig @<권한NS> <도메인> A                 # 원본 (aa 플래그 확인)
$ dig +norecurse @<리졸버> <도메인> A      # 캐시에 뭐가 남아 있나
```

---

이 글의 `dig` 출력은 전부 `byeorim.com`에 실제로 조회한 결과다. 앞선 두 글 [「도메인 등록, 그림으로 이해하기」](/posts/how-domains-get-registered/)와 [「도메인 사서 웹페이지 붙이기, 실제로 해봤다」](/posts/buying-a-domain-in-practice/)에서 지나쳤던 것들을 이 글에서 다뤘다.

