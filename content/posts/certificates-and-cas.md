---
title: "인증서와 CA, 그림으로 이해하기"
date: 2026-08-31T11:25:47+09:00
draft: false
slug: "certificates-and-cas"
translationKey: "certificates-and-cas"
categories: ["개발"]
tags: ["https", "tls", "인증서", "보안", "네트워크"]
summary: "주소창에 자물쇠 하나가 뜨기까지 몇 명의 손을 거치고, 그중 누구를 왜 믿는 것인지 — 인증서, CA, 신뢰 사슬, 도메인 검증을 그림 여덟 장으로 정리했다."
---

<style>
.dgm { --dgm-accent: #14468C; --dgm-go: #1B7A54; --dgm-stop: #A8402A; margin: 0 0 var(--content-gap); }
:root[data-theme="dark"] .dgm { --dgm-accent: #2E6BC4; --dgm-go: #4FBE90; --dgm-stop: #E5876A; }
.dgm .dgm-scroll { overflow-x: auto; }
.dgm svg { display: block; width: 100%; height: auto; color: var(--content); }
.dgm svg text { font-family: inherit; }
.dgm svg .m { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
</style>

지난 글 [「도메인 사서 웹페이지 붙이기, 실제로 해봤다」](/posts/buying-a-domain-in-practice/)에서 이런 장면이 있었다. 도메인은 IP로 풀리는데 `curl`은 거절당한다.

```
curl: (35) SSL routines:ST_CONNECT:sslv3 alert handshake failure
```

1분 30초 뒤에 풀렸고, 인증서를 뜯어보니 발급자가 Cloudflare가 아니라 Google Trust Services였다. 그때는 "Cloudflare는 CA가 아니라 중개자다"라고 한 줄 쓰고 넘어갔다.

그 한 줄 안에 꽤 많은 게 접혀 있다. 주소창에 자물쇠 하나가 뜨기까지 몇 명의 손을 거치는지, 그중 누구를 왜 믿는 것인지를 그림으로 폈다.

## 자물쇠가 정확히 뭔가

먼저 이것부터 정하고 가야 한다.

주소창 왼쪽, 도메인 이름 바로 앞에 뜨는 작은 아이콘이다. 브라우저가 기분으로 붙이는 게 아니라 **검사를 통과했다는 표시**이고, 통과 조건은 딱 둘이다 — 그 서버와 TLS 연결이 맺어졌을 것, 그리고 서버가 내민 인증서가 검증을 통과했을 것. 하나라도 어긋나면 자물쇠 대신 "안전하지 않음"이 뜨거나 아예 경고 화면으로 막힌다.

그러니까 자물쇠는 누가 심사해서 찍어준 도장이 아니라 **기계가 그 자리에서 낸 판정**이다. 그 판정이 무엇을 보증하고 무엇을 보증하지 않는지가 이 글 전체의 주제다.

## 그 판정은 두 가지를 말한다

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 250" role="img" aria-label="주소창의 자물쇠는 내용이 암호화된다는 것과 상대가 진짜라는 것 두 가지를 뜻한다">
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
    <text x="52" y="150" font-size="16.5" font-weight="700" fill="#fff">① 아무도 못 읽는다</text>
    <text x="52" y="178" font-size="13" fill="rgba(255,255,255,.82)">오가는 내용이 암호화된다</text>
    <rect x="374" y="112" width="316" height="100" rx="10" fill="var(--dgm-accent)"/>
    <text x="396" y="150" font-size="16.5" font-weight="700" fill="#fff">② 상대가 진짜다</text>
    <text x="396" y="178" font-size="13" fill="rgba(255,255,255,.82)">지금 연결된 서버가 정말 그 도메인의 주인이다</text>
    <text x="30" y="240" font-size="13.5" fill="var(--secondary)">인증서와 CA는 전부 두 번째 이야기다.</text>
  </svg>
  </div>
  <figcaption><p>어려운 쪽은 암호화가 아니라 상대 확인이다.</p></figcaption>
</figure>

## 암호화만으로는 아무것도 못 지킨다

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 250" role="img" aria-label="진짜 서버와의 암호화된 대화와 가짜 서버와의 암호화된 대화는 암호화 자체로는 구별되지 않는다">
    <defs>
      <marker id="c2a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
    </defs>
    <rect x="20" y="34" width="110" height="62" rx="10" fill="var(--dgm-accent)"/>
    <text x="75" y="72" font-size="16" font-weight="700" fill="#fff" text-anchor="middle">나</text>
    <line x1="140" y1="65" x2="304" y2="65" stroke="currentColor" stroke-width="2" marker-end="url(#c2a)"/>
    <text x="222" y="52" font-size="12.5" fill="var(--secondary)" text-anchor="middle">암호화된 대화</text>
    <rect x="314" y="34" width="256" height="62" rx="10" fill="var(--code-bg)" stroke="var(--dgm-go)" stroke-width="2"/>
    <text x="442" y="72" font-size="15" font-weight="700" fill="currentColor" text-anchor="middle">진짜 byeorim.com</text>
    <polyline points="600,66 612,78 636,50" fill="none" stroke="var(--dgm-go)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
    <rect x="20" y="134" width="110" height="62" rx="10" fill="var(--dgm-accent)"/>
    <text x="75" y="172" font-size="16" font-weight="700" fill="#fff" text-anchor="middle">나</text>
    <line x1="140" y1="165" x2="304" y2="165" stroke="currentColor" stroke-width="2" marker-end="url(#c2a)"/>
    <text x="222" y="152" font-size="12.5" fill="var(--secondary)" text-anchor="middle">암호화된 대화</text>
    <rect x="314" y="134" width="256" height="62" rx="10" fill="var(--code-bg)" stroke="var(--dgm-stop)" stroke-width="2"/>
    <text x="442" y="172" font-size="15" font-weight="700" fill="currentColor" text-anchor="middle">가로챈 가짜 서버</text>
    <line x1="602" y1="150" x2="634" y2="182" stroke="var(--dgm-stop)" stroke-width="3.5" stroke-linecap="round"/>
    <line x1="634" y1="150" x2="602" y2="182" stroke="var(--dgm-stop)" stroke-width="3.5" stroke-linecap="round"/>
    <text x="20" y="234" font-size="13.5" fill="var(--secondary)">암호화는 둘 다 완벽하다. 다른 건 상대가 누구냐뿐이다.</text>
  </svg>
  </div>
  <figcaption><p>도둑과 나누는 비밀 대화도 비밀 대화다. 그래서 신원 확인이 필요하다.</p></figcaption>
</figure>

## 인증서는 서버가 내미는 신분증이다

접속하면 서버가 카드를 한 장 내민다. 그게 인증서다.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 400" role="img" aria-label="인증서에는 도메인 이름, 함께 커버되는 도메인, 공개키, 유효기간, 발급자, 발급자의 서명이 들어 있다">
    <rect x="60" y="16" width="600" height="310" rx="14" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <rect x="60" y="16" width="600" height="52" rx="14" fill="var(--dgm-accent)"/>
    <rect x="60" y="50" width="600" height="18" fill="var(--dgm-accent)"/>
    <text x="84" y="50" font-size="16.5" font-weight="700" fill="#fff">인증서 · 서버가 내미는 카드</text>
    <text x="84" y="104" font-size="13" fill="var(--secondary)">도메인 이름</text>
    <text class="m" x="250" y="104" font-size="14" fill="currentColor">byeorim.com</text>
    <line x1="84" y1="122" x2="636" y2="122" stroke="var(--tertiary)" stroke-width="1" opacity="0.5"/>
    <text x="84" y="146" font-size="13" fill="var(--secondary)">함께 쓰는 도메인</text>
    <text class="m" x="250" y="146" font-size="12.5" fill="currentColor">www.byeorim.com</text>
    <line x1="84" y1="164" x2="636" y2="164" stroke="var(--tertiary)" stroke-width="1" opacity="0.5"/>
    <text x="84" y="188" font-size="13" fill="var(--secondary)">공개키</text>
    <text class="m" x="250" y="188" font-size="12.5" fill="currentColor">EC prime256v1</text>
    <line x1="84" y1="206" x2="636" y2="206" stroke="var(--tertiary)" stroke-width="1" opacity="0.5"/>
    <text x="84" y="230" font-size="13" fill="var(--secondary)">유효기간</text>
    <text class="m" x="250" y="230" font-size="12.5" fill="currentColor">2026-08-30 → 2026-11-28</text>
    <line x1="84" y1="248" x2="636" y2="248" stroke="var(--tertiary)" stroke-width="1" opacity="0.5"/>
    <text x="84" y="272" font-size="13" fill="var(--secondary)">발급자</text>
    <text class="m" x="250" y="272" font-size="12.5" fill="currentColor">Google Trust Services · WE1</text>
    <line x1="84" y1="290" x2="636" y2="290" stroke="var(--tertiary)" stroke-width="1" opacity="0.5"/>
    <text x="84" y="313" font-size="14" font-weight="700" fill="var(--dgm-accent)">발급자의 서명</text>
    <text class="m" x="250" y="313" font-size="12.5" fill="var(--dgm-accent)">3045 0221 00f1 987e ...</text>
    <text x="60" y="362" font-size="13.5" fill="var(--secondary)">브라우저가 이 카드에서 보는 것 — 도메인 이름, 유효기간, 그리고 맨 아랫줄.</text>
  </svg>
  </div>
  <figcaption><p>맨 아랫줄이 이 카드를 신분증으로 만든다. 나머지는 그냥 글자다.</p></figcaption>
</figure>

실물은 이렇게 생겼다.

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

`subject`가 도메인 이름, `issuer`가 발급자다. **브라우저가 주소창의 도메인과 실제로 대조하는 칸은 `subject`가 아니라 `Subject Alternative Name`(SAN)이다.** 옛날에는 `CN` 한 칸에 도메인 이름을 적었는데 그 칸에는 도메인을 하나밖에 못 넣어서 SAN이 생겼고, 지금 `CN`은 사람이 보는 장식에 가깝다. `byeorim.com`과 `www.byeorim.com`이 인증서 한 장으로 커버되는 것도 SAN에 둘 다 적혀 있어서다.

## 위조는 왜 안 되나

카드에 적힌 글자야 누구나 흉내 낼 수 있다. 맨 아랫줄의 서명이 그걸 막는다.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 300" role="img" aria-label="CA는 개인키로 인증서에 서명하고 브라우저는 미리 갖고 있는 CA 공개키로 그 서명을 검증한다">
    <defs>
      <marker id="c4a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
    </defs>
    <text x="10" y="28" font-size="13" font-weight="700" fill="var(--secondary)">발급할 때 — CA가 한다</text>
    <rect x="10" y="40" width="168" height="66" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="94" y="79" font-size="14" fill="currentColor" text-anchor="middle">인증서 내용</text>
    <line x1="184" y1="73" x2="252" y2="73" stroke="currentColor" stroke-width="2" marker-end="url(#c4a)"/>
    <rect x="258" y="40" width="164" height="66" rx="10" fill="var(--dgm-accent)"/>
    <text x="340" y="72" font-size="14" font-weight="700" fill="#fff" text-anchor="middle">CA 개인키</text>
    <text x="340" y="92" font-size="11.5" fill="rgba(255,255,255,.82)" text-anchor="middle">CA만 갖고 있다</text>
    <line x1="428" y1="73" x2="496" y2="73" stroke="currentColor" stroke-width="2" marker-end="url(#c4a)"/>
    <rect x="502" y="40" width="208" height="66" rx="10" fill="var(--code-bg)" stroke="var(--dgm-go)" stroke-width="2"/>
    <text x="606" y="79" font-size="14" fill="currentColor" text-anchor="middle">서명이 붙은 인증서</text>
    <text x="10" y="170" font-size="13" font-weight="700" fill="var(--secondary)">확인할 때 — 브라우저가 한다</text>
    <rect x="10" y="182" width="168" height="66" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="94" y="221" font-size="14" fill="currentColor" text-anchor="middle">받은 인증서</text>
    <line x1="184" y1="215" x2="252" y2="215" stroke="currentColor" stroke-width="2" marker-end="url(#c4a)"/>
    <rect x="258" y="182" width="164" height="66" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="340" y="214" font-size="14" font-weight="700" fill="currentColor" text-anchor="middle">CA 공개키</text>
    <text x="340" y="234" font-size="11.5" fill="var(--secondary)" text-anchor="middle">누구나 갖고 있다</text>
    <line x1="428" y1="215" x2="496" y2="215" stroke="currentColor" stroke-width="2" marker-end="url(#c4a)"/>
    <rect x="502" y="182" width="208" height="66" rx="10" fill="var(--code-bg)" stroke="var(--dgm-go)" stroke-width="2"/>
    <text x="606" y="221" font-size="14" fill="currentColor" text-anchor="middle">한 글자도 안 바뀌었다</text>
    <text x="10" y="284" font-size="13.5" fill="var(--secondary)">내용을 고치면 서명이 깨진다. 새 서명은 CA 개인키 없이 못 만든다.</text>
  </svg>
  </div>
  <figcaption><p>봉인이지 잠금장치가 아니다. 내용을 감추는 게 아니라, 바뀌었는지를 드러낸다.</p></figcaption>
</figure>

## 키가 두 쌍이라 헷갈린다

여기가 제일 자주 꼬이는 지점이다. **인증서 이야기에는 키 쌍이 두 개 나오고, 둘은 아무 상관이 없다.**

| | 주인 | 개인키가 하는 일 | 공개키가 있는 곳 |
|---|---|---|---|
| **서버 키 쌍** | byeorim.com 서버 | 핸드셰이크에서 "내가 이 인증서의 주인"임을 증명 | 인증서 **안에** 들어 있다 |
| **CA 키 쌍** | Google Trust Services | 인증서에 서명 | 브라우저에 **미리 깔려** 있다 |

이 구분이 중요한 이유가 하나 있다. **인증서는 비밀이 아니다.** 접속만 하면 누구나 받아가고, 위에서 `openssl`로 통째로 뽑아본 게 그것이다. 그러니 남의 인증서를 복사해서 내 서버에 걸어둘 수도 있다.

그래도 소용이 없다. 브라우저는 인증서를 받은 뒤 **"그 안에 적힌 공개키와 짝이 되는 개인키를 지금 갖고 있냐"** 를 핸드셰이크에서 확인한다. 복사한 쪽은 그 개인키가 없어서 그 단계를 못 넘긴다. 카드는 베낄 수 있어도 카드 주인은 못 되는 셈이다.

## 그럼 CA는 왜 믿나

서명을 확인하려면 CA의 공개키가 필요하다. 그 공개키는 또 CA의 인증서에 들어 있다. 그 인증서는 또 누가 보증하나 — 이 질문은 위로 계속 올라가고, 어딘가에서 끝나야 한다.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 390" role="img" aria-label="루트 CA가 중간 CA에 서명하고 중간 CA가 서버 인증서에 서명하는 신뢰 사슬. 루트는 기기에 미리 설치되어 있다">
    <defs>
      <marker id="c5a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
    </defs>
    <rect x="180" y="12" width="380" height="76" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="202" y="42" font-size="16.5" font-weight="700" fill="currentColor">GTS Root R4 · 루트 CA</text>
    <text x="202" y="66" font-size="13" fill="var(--secondary)">스스로에게 서명한다. 아무도 보증하지 않는다.</text>
    <line x1="150" y1="50" x2="174" y2="50" stroke="var(--dgm-accent)" stroke-width="2" stroke-dasharray="4 3"/>
    <text x="76" y="44" font-size="12.5" font-weight="700" fill="var(--dgm-accent)" text-anchor="middle">내 노트북에</text>
    <text x="76" y="62" font-size="12.5" font-weight="700" fill="var(--dgm-accent)" text-anchor="middle">미리 깔려 있음</text>
    <line x1="370" y1="88" x2="370" y2="124" stroke="currentColor" stroke-width="2" marker-end="url(#c5a)"/>
    <text x="600" y="112" font-size="12.5" fill="var(--secondary)">서명</text>
    <rect x="180" y="124" width="380" height="76" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="202" y="154" font-size="16.5" font-weight="700" fill="currentColor">WE1 · 중간 CA</text>
    <text x="202" y="178" font-size="13" fill="var(--secondary)">실제 발급은 여기서 매일 수백만 장</text>
    <line x1="370" y1="200" x2="370" y2="236" stroke="currentColor" stroke-width="2" marker-end="url(#c5a)"/>
    <text x="600" y="224" font-size="12.5" fill="var(--secondary)">서명</text>
    <rect x="180" y="236" width="380" height="76" rx="10" fill="var(--dgm-accent)"/>
    <text class="m" x="202" y="266" font-size="16" font-weight="700" fill="#fff">byeorim.com</text>
    <text x="202" y="290" font-size="13" fill="rgba(255,255,255,.82)">서버가 내미는 그 카드</text>
    <text x="10" y="352" font-size="13.5" fill="var(--secondary)">루트는 검증되지 않는다. 검증의 끝이라서 그냥 믿는 것이다.</text>
  </svg>
  </div>
  <figcaption><p>도메인의 신뢰 사슬이 루트 존에서 끝나듯, 인증서의 사슬은 내 기기에 깔린 루트에서 끝난다.</p></figcaption>
</figure>

`openssl`이 그 사슬을 그대로 뱉는다.

```
$ echo | openssl s_client -connect byeorim.com:443 -servername byeorim.com

depth=2 C=US, O=Google Trust Services LLC, CN=GTS Root R4
depth=1 C=US, O=Google Trust Services, CN=WE1
depth=0 CN=byeorim.com
```

`depth=0`이 서버가 내민 카드, `depth=2`가 사슬의 끝이다. 그 끝은 어디에 있나.

```
$ security find-certificate -a -p /System/Library/Keychains/SystemRootCertificates.keychain | grep -c "BEGIN CERTIFICATE"
158
```

**내 맥에는 158장이 미리 깔려 있었다.** GTS Root R4도 그중 하나다. 몇 장인지는 OS·브라우저·버전마다 다르니 이 숫자 자체는 중요하지 않다. 중요한 건 인터넷 전체의 HTTPS 신뢰가 결국 이런 목록에서 출발한다는 사실이다. 브라우저가 루트를 믿는 이유는 검증했기 때문이 아니라 **목록에 있기 때문**이다.

그래서 이 목록이 곧 권력이다. 여기 들어가려면 CA는 감사와 규정 준수를 통과해야 하고, 사고를 내면 쫓겨난다. 실제로 여러 CA가 이 목록에서 제거돼 사실상 문을 닫았다.

거꾸로, **이 목록에 뭔가를 추가할 수 있으면 그 사람은 모든 HTTPS를 열어볼 수 있다.** 회사 노트북에 보안 프로그램을 깔면서 루트 인증서 설치를 요구받는 경우가 그것이고, 개발용 프록시가 HTTPS 트래픽을 뜯어볼 수 있는 것도 같은 원리다.

## 루트는 왜 직접 발급하지 않나

사슬이 굳이 3단인 이유가 있다.

루트 개인키는 인터넷에서 끊긴 금고 안에 있다. 그걸 쓰려면 여러 사람이 모여 의식에 가까운 절차를 밟는다. 매일 수백만 장을 발급하려고 그걸 꺼낼 수는 없다.

그래서 루트는 **중간 CA에게 서명 권한을 위임하고**, 실제 발급은 온라인에 있는 중간 CA가 한다. 중간 키가 털리면 그 중간 CA만 폐기하면 되고, 루트는 무사하다. `WE1`이 그 중간이다.

## CA는 내가 그 도메인 주인인 걸 어떻게 아나

여기가 실제로 제일 궁금한 대목이다. `byeorim.com` 인증서를 아무나 신청하면 어떡하나.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 390" role="img" aria-label="인증서 신청, CA의 토큰 제시, 도메인에 토큰 배치, CA의 확인과 발급으로 이어지는 도메인 검증 절차">
    <defs>
      <marker id="c6a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
    </defs>
    <rect x="40" y="12" width="640" height="60" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="64" y="48" font-size="14.5" fill="currentColor">① 나 → CA · byeorim.com 인증서를 주세요</text>
    <line x1="360" y1="72" x2="360" y2="92" stroke="currentColor" stroke-width="2" marker-end="url(#c6a)"/>
    <rect x="40" y="96" width="640" height="60" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="64" y="132" font-size="14.5" fill="currentColor">② CA → 나 · 그럼 이 토큰을 그 도메인에 놓아 보세요</text>
    <line x1="360" y1="156" x2="360" y2="176" stroke="currentColor" stroke-width="2" marker-end="url(#c6a)"/>
    <rect x="40" y="180" width="640" height="84" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="64" y="212" font-size="14.5" fill="currentColor">③ 그 도메인의 웹서버에 파일을 놓거나 · HTTP-01</text>
    <text x="84" y="240" font-size="14.5" fill="currentColor">그 도메인의 DNS에 TXT를 놓는다 · DNS-01</text>
    <line x1="360" y1="264" x2="360" y2="284" stroke="currentColor" stroke-width="2" marker-end="url(#c6a)"/>
    <rect x="40" y="288" width="640" height="60" rx="10" fill="var(--dgm-accent)"/>
    <text x="64" y="324" font-size="14.5" font-weight="700" fill="#fff">④ CA가 직접 조회해서 확인하고 발급한다</text>
    <text x="40" y="376" font-size="13.5" fill="var(--secondary)">웹서버나 DNS를 통제하면 그 도메인의 주인으로 본다. 그래서 '도메인 검증'이다.</text>
  </svg>
  </div>
  <figcaption><p>신청서에 뭐라고 썼는지는 안 본다. 그 도메인을 실제로 움직일 수 있는지만 본다.</p></figcaption>
</figure>

이 문답을 자동으로 주고받는 규약이 **ACME**다. Let's Encrypt가 만들었고 지금은 표준이 됐다. `certbot` 같은 도구가 하는 일이 이 4단계를 사람 없이 돌리는 것이다.

검증 방식은 인증서에도 기록된다.

```
X509v3 Certificate Policies:
    Policy: 2.23.140.1.2.1
```

이 번호가 **DV(Domain Validation)** 를 뜻한다. "도메인 통제만 확인했다"는 표시다. 회사 실체까지 확인하는 OV·EV도 있지만, 브라우저는 이제 셋을 화면에서 구분해 보여주지 않는다. 자물쇠는 다 똑같이 생겼다.

## 자물쇠가 보증하지 않는 것

그래서 이 지점을 분명히 해둘 필요가 있다.

- **보증한다** — 지금 연결된 서버가 `byeorim.com`을 통제하고 있다.
- **보증하지 않는다** — 그 사이트가 정직한지, 회사가 실존하는지, 결제해도 되는지.

피싱 사이트도 자물쇠를 단다. 도메인만 사면 5분 만에 DV 인증서가 나오기 때문이다. **자물쇠는 "안전한 사이트"라는 뜻이 아니라 "주소창에 적힌 그 도메인과 연결됐다"는 뜻이다.** 그래서 확인해야 할 것은 자물쇠가 아니라 그 옆의 도메인 철자다.

이 오해가 워낙 널리 퍼져서 **브라우저들은 자물쇠를 치우는 쪽으로 가고 있다.** 크롬이 2023년 117 버전에서 자물쇠를 없애고 그 자리에 설정 슬라이더 모양 아이콘을 넣은 것이 대표적이다. 구글이 밝힌 이유가 정확히 위 문단이다 — 자체 조사에서 자물쇠의 의미를 제대로 아는 사용자가 11%뿐이었고, 나머지 대부분은 "이 사이트는 믿을 만하다"로 읽었다.

지금 어느 브라우저가 자물쇠를 띄우고 어느 쪽이 안 띄우는지는 버전마다 바뀌니 직접 확인해야 한다. 방향만 기억하면 된다 — **자물쇠가 사라지는 건 보안이 약해져서가 아니라, 그 비유 자체가 오해를 낳는다고 판단해서다.**

## CA가 실수하면

CA가 해킹당하거나 실수로 남의 도메인 인증서를 찍으면 이 구조 전체가 무너진다. 실제로 그런 사고가 있었다.

대책은 **모든 발급을 공개 장부에 남기게** 한 것이다. Certificate Transparency(CT)다. CA는 인증서를 찍을 때 공개 로그에 등록하고, 로그가 준 영수증(SCT)을 인증서 안에 박아 넣는다. 영수증이 없는 인증서는 크롬이 아예 거부한다.

```
$ echo | openssl s_client -connect byeorim.com:443 -servername byeorim.com 2>/dev/null \
    | openssl x509 -noout -text | grep -A2 "Signed Certificate Timestamp"

Signed Certificate Timestamp:
    Log ID    : D7:6D:7D:10:D1:A7:F5:77:...
    Timestamp : Aug 30 13:01:03.738 2026 GMT
```

영수증이 두 장 박혀 있었다. 서로 다른 로그 두 곳에 등록했다는 뜻이다.

효과는 이렇다. **누가 내 도메인 인증서를 몰래 받아 가면 그 사실이 공개 장부에 남는다.** [crt.sh](https://crt.sh)에 도메인을 넣으면 그 도메인으로 발급된 인증서 전부가 보인다. 몰래는 안 된다는 것, 그게 CT가 바꾼 전부다.

## 90일이라는 수명

발급일과 만료일을 다시 보자.

```
notBefore=Aug 30 12:01:03 2026 GMT
notAfter =Nov 28 13:01:00 2026 GMT      ← 90일
```

짧다. 이유가 있다.

인증서를 무효로 만드는 **폐기(revocation) 절차가 사실상 제대로 작동하지 않는다.** 개인키가 유출돼 CA가 폐기를 선언해도, 그 소식이 전 세계 브라우저에 제때 닿는다는 보장이 없다. 폐기 확인을 아예 건너뛰는 구현도 흔하다.

그래서 업계는 다른 쪽으로 갔다. **애초에 오래 안 살게 만든다.** 유출돼도 피해가 지속될 창이 그만큼 좁아진다. 상한도 계속 내려가는 중이다 — 한때 5년이던 것이 398일이 됐고, 2026년 3월부터 200일, 2027년 100일, 2029년 47일로 예정돼 있다.

여기서 따라오는 결론이 하나 있다. **수명이 짧아지면 손으로 갱신하는 건 불가능해진다.** 47일마다 사람이 챙기는 운영은 언젠가 반드시 만료 사고를 낸다. 그래서 ACME 같은 자동화가 선택이 아니라 전제가 됐다.

## 그래서 Cloudflare가 한 일

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 250" role="img" aria-label="Cloudflare는 CA가 아니라 사용자를 대신해 CA에서 인증서를 받아 설치하는 중개자다">
    <defs>
      <marker id="c7a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
    </defs>
    <rect x="16" y="88" width="130" height="76" rx="10" fill="var(--dgm-accent)"/>
    <text x="81" y="132" font-size="16" font-weight="700" fill="#fff" text-anchor="middle">나</text>
    <line x1="152" y1="126" x2="230" y2="126" stroke="currentColor" stroke-width="2" marker-end="url(#c7a)"/>
    <rect x="236" y="74" width="204" height="104" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="338" y="112" font-size="16" font-weight="700" fill="currentColor" text-anchor="middle">Cloudflare</text>
    <text x="338" y="136" font-size="12.5" fill="var(--secondary)" text-anchor="middle">DNS도 서버도 다 갖고 있다</text>
    <text x="338" y="156" font-size="12.5" fill="var(--secondary)" text-anchor="middle">그래서 검증을 대신 통과한다</text>
    <text x="612" y="44" font-size="13" font-weight="700" fill="var(--secondary)" text-anchor="middle">진짜 CA</text>
    <line x1="446" y1="110" x2="518" y2="88" stroke="currentColor" stroke-width="2" marker-end="url(#c7a)"/>
    <line x1="446" y1="146" x2="518" y2="168" stroke="currentColor" stroke-width="2" marker-end="url(#c7a)"/>
    <rect x="524" y="60" width="180" height="56" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="614" y="94" font-size="13" fill="currentColor" text-anchor="middle">Google Trust Services</text>
    <rect x="524" y="140" width="180" height="56" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="614" y="174" font-size="13" fill="currentColor" text-anchor="middle">Let's Encrypt</text>
    <text x="16" y="232" font-size="13.5" fill="var(--secondary)">Cloudflare는 CA가 아니다. 받아온 인증서를 깔고, 만료 전에 갈아 끼운다.</text>
  </svg>
  </div>
  <figcaption><p>앞 글의 그 1분 30초가 이 왕복에 걸린 시간이다.</p></figcaption>
</figure>

앞 글에서 겪은 것들이 여기서 다 설명된다.

**`handshake failure`가 404가 아니었던 이유.** 서버에 그 도메인으로 내밀 인증서가 아직 없으면 대화 자체가 시작되지 않는다. HTTPS는 HTTP를 TLS 위에 얹은 것이라, TLS 연결이 맺어진 다음에야 그 위로 HTTP 요청이 오간다. 인증서 교환에서 막히면 요청을 보내볼 기회조차 없다. 404는 "요청은 받았는데 그런 페이지가 없다"이고, `handshake failure`는 그보다 한 층 아래에서 끊긴 것이다.

**발급자가 Cloudflare가 아니었던 이유.** Cloudflare는 루트 저장소에 든 CA가 아니다. 자기 이름으로 서명해봐야 브라우저가 안 믿는다. 그래서 Google Trust Services나 Let's Encrypt에서 받아 온다.

**인증서 한 장으로 다 커버된 이유.** 그때 `*.byeorim-com.workers.dev` 와일드카드 한 장이 계정의 모든 Worker를 덮었다. SAN에 `*`를 넣으면 도메인의 그 자리 한 칸을 무엇으로든 채울 수 있다. 다만 별 하나는 딱 한 칸만 먹는다 — `*.example.com`은 `a.example.com`은 되지만 `a.b.example.com`은 안 되고, `example.com` 자기 자신도 안 된다. 그래서 실제 인증서에는 `byeorim.com`과 `www.byeorim.com`이 따로 적혀 있다.

## DNSSEC과는 뭐가 다른가

앞 글에서 DNSSEC도 켰다. 둘 다 "신뢰 사슬"이라는 말을 쓰는데, 서로 다른 사슬이다.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 400" role="img" aria-label="DNSSEC의 신뢰 사슬과 TLS 인증서의 신뢰 사슬은 서로 다른 두 개의 사슬이다">
    <defs>
      <marker id="c8a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
    </defs>
    <line x1="360" y1="12" x2="360" y2="352" stroke="var(--tertiary)" stroke-width="1" stroke-dasharray="4 4"/>
    <text x="176" y="30" font-size="16.5" font-weight="700" fill="currentColor" text-anchor="middle">DNSSEC</text>
    <text x="176" y="52" font-size="12.5" fill="var(--secondary)" text-anchor="middle">도메인 → IP 답이 진짜인가</text>
    <text x="544" y="30" font-size="16.5" font-weight="700" fill="currentColor" text-anchor="middle">TLS 인증서</text>
    <text x="544" y="52" font-size="12.5" fill="var(--secondary)" text-anchor="middle">연결된 상대가 진짜인가</text>
    <rect x="46" y="70" width="260" height="52" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="176" y="102" font-size="14" fill="currentColor" text-anchor="middle">루트 존</text>
    <line x1="176" y1="122" x2="176" y2="146" stroke="currentColor" stroke-width="2" marker-end="url(#c8a)"/>
    <rect x="46" y="150" width="260" height="52" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text class="m" x="176" y="182" font-size="14" fill="currentColor" text-anchor="middle">.com 존</text>
    <line x1="176" y1="202" x2="176" y2="226" stroke="currentColor" stroke-width="2" marker-end="url(#c8a)"/>
    <rect x="46" y="230" width="260" height="52" rx="10" fill="var(--dgm-accent)"/>
    <text class="m" x="176" y="262" font-size="14" font-weight="700" fill="#fff" text-anchor="middle">byeorim.com 존</text>
    <rect x="414" y="70" width="260" height="52" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="544" y="102" font-size="14" fill="currentColor" text-anchor="middle">루트 CA</text>
    <line x1="544" y1="122" x2="544" y2="146" stroke="currentColor" stroke-width="2" marker-end="url(#c8a)"/>
    <rect x="414" y="150" width="260" height="52" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="544" y="182" font-size="14" fill="currentColor" text-anchor="middle">중간 CA</text>
    <line x1="544" y1="202" x2="544" y2="226" stroke="currentColor" stroke-width="2" marker-end="url(#c8a)"/>
    <rect x="414" y="230" width="260" height="52" rx="10" fill="var(--dgm-accent)"/>
    <text class="m" x="544" y="262" font-size="14" font-weight="700" fill="#fff" text-anchor="middle">byeorim.com 인증서</text>
    <text x="176" y="312" font-size="12.5" fill="var(--secondary)" text-anchor="middle">하위 존을 상위 존이 보증</text>
    <text x="544" y="312" font-size="12.5" fill="var(--secondary)" text-anchor="middle">하위 인증서를 상위 CA가 보증</text>
    <text x="176" y="336" font-size="12.5" fill="var(--secondary)" text-anchor="middle">출발점은 전 세계가 아는 루트 키</text>
    <text x="544" y="336" font-size="12.5" fill="var(--secondary)" text-anchor="middle">출발점은 내 기기에 깔린 루트 목록</text>
    <text x="20" y="378" font-size="13.5" fill="var(--secondary)">겹치지 않는 두 사슬이다. 하나가 있다고 다른 하나가 되지는 않는다.</text>
  </svg>
  </div>
  <figcaption><p>DNSSEC은 주소를 제대로 찾아왔는지, 인증서는 거기 있는 게 진짜인지를 본다.</p></figcaption>
</figure>

DNSSEC이 지키는 건 **"주소를 제대로 찾아왔나"** 이고, 인증서가 지키는 건 **"그 주소에 있는 게 진짜인가"** 다. 순서상 DNSSEC이 먼저지만, DNSSEC 없이도 HTTPS는 성립한다. 답이 가짜 IP로 오더라도 그 서버는 `byeorim.com` 인증서를 못 내밀기 때문이다.

거꾸로 DNSSEC만 켜고 HTTPS를 안 쓰면 아무것도 지켜지지 않는다. 주소는 제대로 찾았지만 그 뒤 대화가 전부 평문이다.

## 첫 요청이 평문이면 다 소용없다

앞 글에서 `Always Use HTTPS`가 꺼져 있던 게 마지막 조각이다.

```
$ curl -sSI http://byeorim.com
HTTP/1.1 200 OK
                        ← Location 헤더가 없다
```

주소창에 `byeorim.com`만 치면 브라우저는 대개 `http://`로 먼저 간다. 그 요청에는 인증서가 개입하지 않는다. 검사할 카드 자체가 없다. 리다이렉트를 걸어도 **그 리다이렉트 응답부터가 평문**이라 중간에서 다른 곳으로 바꿔칠 수 있다.

`Always Use HTTPS`는 그 구멍을 완전히 막지는 못한다. 첫 왕복 한 번은 여전히 평문이다. 그걸 없애려면 `Strict-Transport-Security`(HSTS) 헤더를 붙여야 한다. 브라우저에게 **"이 도메인은 앞으로 무조건 https로 와라"** 를 기억시키는 헤더고, 한 번 기억하면 `http://`를 쳐도 브라우저가 요청을 보내기 전에 스스로 바꾼다.

## 이것만은 기억하기

- **자물쇠는 "안전한 사이트"가 아니라 "주소창의 그 도메인과 연결됐다"는 뜻이다.** 피싱 사이트도 자물쇠를 단다.
- **신뢰의 뿌리는 내 기기에 미리 깔린 루트 목록이다.** 거기에 뭘 추가할 수 있는 사람은 내 HTTPS를 다 열어볼 수 있다.
- **인증서는 짧게 살고 자동으로 갱신된다.** 자동화가 없으면 언젠가 만료로 사이트가 죽는다.
- **확인은 명령 한 줄이면 된다.** 도메인 이름·유효기간·발급자가 다 나온다.

```
$ echo | openssl s_client -connect <도메인>:443 -servername <도메인> 2>/dev/null \
    | openssl x509 -noout -subject -issuer -dates -ext subjectAltName
```
