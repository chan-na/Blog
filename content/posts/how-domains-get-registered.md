---
title: "도메인 등록, 그림으로 이해하기"
date: 2026-08-30T16:13:10+09:00
draft: false
slug: "how-domains-get-registered"
translationKey: "how-domains-get-registered"
categories: ["개발"]
tags: ["dns", "domain", "네트워크", "입문"]
summary: "도메인이 어떻게 내 것이 되고, 주소창에 친 이름이 어떻게 서버를 찾아가는지 — 그림 여덟 장으로 정리했다."
---

<style>
.dgm { --dgm-accent: #14468C; --dgm-go: #1B7A54; --dgm-stop: #A8402A; margin: 0 0 var(--content-gap); }
:root[data-theme="dark"] .dgm { --dgm-accent: #2E6BC4; --dgm-go: #4FBE90; --dgm-stop: #E5876A; }
.dgm .dgm-scroll { overflow-x: auto; }
.dgm svg { display: block; width: 100%; height: auto; color: var(--content); }
.dgm svg text { font-family: inherit; }
.dgm svg .m { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
</style>

도메인은 인터넷에 다는 주소판이다. 사이트를 세상에 내놓으려면 먼저 주소를 하나 빌려야 하는데, 그 절차가 생각보다 여러 층으로 나뉘어 있다. 등록 버튼을 누르는 순간 뒤에서 무슨 일이 벌어지는지, 그리고 나중에 누군가 주소창에 그 이름을 쳤을 때 어떻게 내 서버까지 도달하는지를 그림으로 정리했다.

## 컴퓨터는 숫자, 사람은 이름

컴퓨터끼리는 숫자로 서로를 찾는다. 사람은 그 숫자를 못 외운다. 그래서 이름을 하나 붙였다.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 210" role="img" aria-label="사람이 쓰는 도메인 이름을 DNS가 컴퓨터가 쓰는 IP 주소로 바꿔준다">
    <defs>
      <marker id="d1a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
    </defs>
    <text x="10" y="42" font-size="13" font-weight="700" fill="var(--secondary)">사람이 기억하는 것</text>
    <rect x="10" y="58" width="250" height="88" rx="10" fill="var(--dgm-accent)"/>
    <text class="m" x="135" y="110" font-size="22" fill="#fff" text-anchor="middle">mystore.com</text>
    <line x1="286" y1="102" x2="414" y2="102" stroke="currentColor" stroke-width="2" marker-end="url(#d1a)"/>
    <text x="350" y="89" font-size="14" font-weight="700" fill="currentColor" text-anchor="middle">DNS가 바꿔줌</text>
    <text x="350" y="128" font-size="12" fill="var(--secondary)" text-anchor="middle">인터넷 전화번호부</text>
    <text x="440" y="42" font-size="13" font-weight="700" fill="var(--secondary)">컴퓨터가 쓰는 것</text>
    <rect x="440" y="58" width="270" height="88" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text class="m" x="575" y="110" font-size="22" fill="currentColor" text-anchor="middle">203.0.113.42</text>
    <text x="10" y="188" font-size="13.5" fill="var(--secondary)">이름이 없으면 우리는 매번 이 숫자를 외워서 쳐야 한다.</text>
  </svg>
  </div>
  <figcaption><p>도메인 이름을 IP 주소로 바꿔주는 일 — 그게 DNS가 하는 전부다.</p></figcaption>
</figure>

## 주소를 나눠주는 네 층

도메인은 한 곳에서 파는 게 아니다. 규칙을 만드는 곳, 장부를 가진 곳, 창구, 그리고 나. 네 층으로 나뉘어 있다.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 440" role="img" aria-label="ICANN이 레지스트리에 운영 권한을 위임하고, 레지스트리가 등록대행자에게 판매를 맡기고, 등록자는 등록대행자에 신청하며, 기록은 레지스트리 장부에 남는다">
    <defs>
      <marker id="d2a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
      <marker id="d2b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-accent)"/></marker>
    </defs>
    <rect x="170" y="12" width="380" height="72" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="192" y="42" font-size="16.5" font-weight="700" fill="currentColor">ICANN</text>
    <text x="192" y="66" font-size="13" fill="var(--secondary)">인터넷 이름 전체를 총괄하는 기구</text>
    <line x1="360" y1="84" x2="360" y2="118" stroke="currentColor" stroke-width="2" marker-end="url(#d2a)"/>
    <text x="562" y="106" font-size="12.5" fill="var(--secondary)">운영 권한 위임</text>
    <rect x="170" y="118" width="380" height="72" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="192" y="148" font-size="16.5" font-weight="700" fill="currentColor">레지스트리 · 장부 주인</text>
    <text x="192" y="172" font-size="13" fill="var(--secondary)">.com은 Verisign, .kr은 KISA</text>
    <line x1="360" y1="190" x2="360" y2="224" stroke="currentColor" stroke-width="2" marker-end="url(#d2a)"/>
    <text x="562" y="212" font-size="12.5" fill="var(--secondary)">판매 위탁</text>
    <rect x="170" y="224" width="380" height="72" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="192" y="254" font-size="16.5" font-weight="700" fill="currentColor">등록대행자 · 창구</text>
    <text x="192" y="278" font-size="13" fill="var(--secondary)">가비아, 후이즈, Cloudflare, GoDaddy…</text>
    <line x1="360" y1="296" x2="360" y2="330" stroke="currentColor" stroke-width="2" marker-end="url(#d2a)"/>
    <text x="562" y="318" font-size="12.5" fill="var(--secondary)">신청 · 결제</text>
    <rect x="170" y="330" width="380" height="72" rx="10" fill="var(--dgm-accent)"/>
    <text x="192" y="360" font-size="16.5" font-weight="700" fill="#fff">나 · 등록자</text>
    <text x="192" y="384" font-size="13" fill="rgba(255,255,255,.82)">1년 단위로 사용권을 빌리는 사람</text>
    <path d="M170,366 L96,366 L96,154 L164,154" fill="none" stroke="var(--dgm-accent)" stroke-width="2" marker-end="url(#d2b)"/>
    <text x="82" y="260" font-size="12.5" font-weight="700" fill="var(--dgm-accent)" text-anchor="middle" transform="rotate(-90 82 260)">내 이름이 장부에 올라감</text>
    <text x="10" y="428" font-size="13" fill="var(--secondary)">돈은 창구에 내지만, 기록은 레지스트리 장부에 남는다.</text>
  </svg>
  </div>
  <figcaption><p>창구는 바꿀 수 있다. 장부에 적힌 도메인은 그대로 내 것으로 따라온다.</p></figcaption>
</figure>

## 등록은 다섯 걸음

실제로 창구에 앉아서 하는 일은 이게 전부다.

### 1. 이름을 고른다

앞은 내가 짓고, 뒤는 골라 쓴다. 뒤에 붙는 `.com`, `.kr`, `.io` 같은 걸 TLD(Top-Level Domain)라고 부른다.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 175" role="img" aria-label="도메인은 내가 짓는 이름과 골라 쓰는 확장자 TLD로 나뉜다">
    <rect x="140" y="26" width="280" height="80" rx="10" fill="var(--dgm-accent)"/>
    <text class="m" x="280" y="76" font-size="26" fill="#fff" text-anchor="middle">mystore</text>
    <rect x="420" y="26" width="160" height="80" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text class="m" x="500" y="76" font-size="26" fill="currentColor" text-anchor="middle">.com</text>
    <line x1="280" y1="114" x2="280" y2="128" stroke="var(--tertiary)" stroke-width="1.5"/>
    <line x1="500" y1="114" x2="500" y2="128" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="280" y="150" font-size="14" font-weight="700" fill="var(--secondary)" text-anchor="middle">내가 짓는 이름</text>
    <text x="500" y="150" font-size="14" font-weight="700" fill="var(--secondary)" text-anchor="middle">골라 쓰는 TLD</text>
  </svg>
  </div>
  <figcaption><p>TLD마다 주인(레지스트리)이 다르고, 값도 정책도 다르다.</p></figcaption>
</figure>

### 2. 비어 있는지 확인한다

먼저 온 사람이 임자다. 이미 누가 쓰고 있으면 그 이름은 쓸 수 없고, 다른 TLD를 보거나 이름을 바꿔야 한다.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 185" role="img" aria-label="검색창에 이름을 넣으면 등록 가능한 것과 이미 사용 중인 것이 나뉘어 나온다">
    <rect x="30" y="16" width="660" height="50" rx="25" fill="none" stroke="var(--tertiary)" stroke-width="1.5"/>
    <circle cx="64" cy="41" r="9" fill="none" stroke="var(--secondary)" stroke-width="2"/>
    <line x1="71" y1="48" x2="78" y2="55" stroke="var(--secondary)" stroke-width="2" stroke-linecap="round"/>
    <text class="m" x="96" y="47" font-size="18" fill="currentColor">mystore</text>
    <polyline points="36,106 46,116 64,96" fill="none" stroke="var(--dgm-go)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    <text class="m" x="86" y="113" font-size="17" fill="currentColor">mystore.com</text>
    <text x="690" y="113" font-size="15" font-weight="700" fill="var(--dgm-go)" text-anchor="end">등록 가능</text>
    <line x1="37" y1="148" x2="56" y2="167" stroke="var(--dgm-stop)" stroke-width="3" stroke-linecap="round"/>
    <line x1="56" y1="148" x2="37" y2="167" stroke="var(--dgm-stop)" stroke-width="3" stroke-linecap="round"/>
    <text class="m" x="86" y="161" font-size="17" fill="var(--secondary)">mystore.io</text>
    <text x="690" y="161" font-size="15" font-weight="700" fill="var(--dgm-stop)" text-anchor="end">이미 사용 중</text>
  </svg>
  </div>
  <figcaption><p>검색 결과는 레지스트리 장부를 실시간으로 조회한 것이다.</p></figcaption>
</figure>

### 3. 창구에서 1년치를 낸다

도메인은 사는 게 아니라 **빌리는** 것이다. 보통 1년 단위, 길게는 10년까지 미리 낼 수 있다.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 180" role="img" aria-label="등록일부터 1년간 사용하고 만료 뒤에는 유예기간을 지나 삭제된다">
    <defs>
      <marker id="d5a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-accent)"/></marker>
    </defs>
    <path d="M520,84 C 520,26 40,26 40,78" fill="none" stroke="var(--dgm-accent)" stroke-width="2" marker-end="url(#d5a)"/>
    <text x="280" y="22" font-size="14" font-weight="700" fill="var(--dgm-accent)" text-anchor="middle">매년 갱신하면 계속 내 것</text>
    <rect x="40" y="94" width="480" height="32" rx="6" fill="var(--dgm-accent)"/>
    <text x="280" y="116" font-size="14" font-weight="700" fill="#fff" text-anchor="middle">사용 기간 1년</text>
    <rect x="524" y="94" width="120" height="32" rx="6" fill="none" stroke="var(--dgm-stop)" stroke-width="2" stroke-dasharray="5 4"/>
    <text x="584" y="116" font-size="13" font-weight="700" fill="var(--dgm-stop)" text-anchor="middle">유예 30일</text>
    <line x1="40" y1="132" x2="40" y2="144" stroke="var(--tertiary)" stroke-width="1.5"/>
    <line x1="520" y1="132" x2="520" y2="144" stroke="var(--tertiary)" stroke-width="1.5"/>
    <line x1="644" y1="132" x2="644" y2="144" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="40" y="164" font-size="13" fill="var(--secondary)">등록일</text>
    <text x="520" y="164" font-size="13" fill="var(--secondary)" text-anchor="middle">만료일</text>
    <text x="644" y="164" font-size="13" font-weight="700" fill="var(--dgm-stop)" text-anchor="middle">삭제</text>
  </svg>
  </div>
  <figcaption><p>유예기간이 지나면 삭제되어 시장에 다시 풀린다. 그 사이 복구는 가능하지만 비싸다.</p></figcaption>
</figure>

### 4. 이메일을 인증한다

등록자 연락처가 진짜인지 확인하는 절차다. 결제만 하고 끝난 게 아니다. **15일 안에 안 누르면 도메인이 잠긴다.**

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 175" role="img" aria-label="인증 메일을 받아 링크를 누르면 도메인이 활성 상태가 된다">
    <defs>
      <marker id="d6a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
    </defs>
    <rect x="40" y="42" width="150" height="86" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <polyline points="40,52 115,105 190,52" fill="none" stroke="var(--secondary)" stroke-width="2"/>
    <text x="115" y="152" font-size="13.5" fill="var(--secondary)" text-anchor="middle">인증 메일 도착</text>
    <line x1="204" y1="85" x2="244" y2="85" stroke="currentColor" stroke-width="2" marker-end="url(#d6a)"/>
    <rect x="256" y="42" width="170" height="86" rx="10" fill="var(--dgm-accent)"/>
    <text x="341" y="92" font-size="17" font-weight="700" fill="#fff" text-anchor="middle">링크 클릭</text>
    <text x="341" y="152" font-size="13.5" fill="var(--secondary)" text-anchor="middle">15일 이내</text>
    <line x1="440" y1="85" x2="480" y2="85" stroke="currentColor" stroke-width="2" marker-end="url(#d6a)"/>
    <rect x="492" y="42" width="188" height="86" rx="10" fill="none" stroke="var(--dgm-go)" stroke-width="2"/>
    <polyline points="556,86 570,100 624,62" fill="none" stroke="var(--dgm-go)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    <text x="586" y="152" font-size="13.5" font-weight="700" fill="var(--dgm-go)" text-anchor="middle">도메인 활성</text>
  </svg>
  </div>
  <figcaption><p>ICANN 규정상 필수 절차다. 창구가 아니라 ICANN이 요구하는 것이라 건너뛸 수 없다.</p></figcaption>
</figure>

### 5. 내 서버를 연결한다

이름표에 "내 서버는 여기"라고 적는 단계다. 이걸 안 하면 주소만 있고 열리는 건 없다.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 185" role="img" aria-label="도메인에 네임서버를 지정하고 네임서버가 서버 IP를 알려주도록 연결한다">
    <defs>
      <marker id="d7a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
    </defs>
    <rect x="20" y="56" width="205" height="82" rx="10" fill="var(--dgm-accent)"/>
    <text x="122" y="88" font-size="13" fill="rgba(255,255,255,.8)" text-anchor="middle">도메인</text>
    <text class="m" x="122" y="114" font-size="16" fill="#fff" text-anchor="middle">mystore.com</text>
    <line x1="233" y1="97" x2="265" y2="97" stroke="currentColor" stroke-width="2" marker-end="url(#d7a)"/>
    <text x="249" y="44" font-size="13" font-weight="700" fill="var(--secondary)" text-anchor="middle">NS 지정</text>
    <rect x="273" y="56" width="205" height="82" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="375" y="88" font-size="13" fill="var(--secondary)" text-anchor="middle">네임서버</text>
    <text class="m" x="375" y="114" font-size="16" fill="currentColor" text-anchor="middle">ns1.host.com</text>
    <line x1="486" y1="97" x2="518" y2="97" stroke="currentColor" stroke-width="2" marker-end="url(#d7a)"/>
    <text x="502" y="44" font-size="13" font-weight="700" fill="var(--secondary)" text-anchor="middle">A 레코드</text>
    <rect x="526" y="56" width="174" height="82" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="613" y="88" font-size="13" fill="var(--secondary)" text-anchor="middle">내 서버</text>
    <text class="m" x="613" y="114" font-size="16" fill="currentColor" text-anchor="middle">203.0.113.42</text>
    <text x="360" y="170" font-size="13.5" fill="var(--secondary)" text-anchor="middle">전 세계에 퍼지는 데 몇 분 ~ 몇 시간</text>
  </svg>
  </div>
  <figcaption><p>NS는 "누가 이 도메인의 답을 아는가", A 레코드는 "그 답이 무엇인가"에 해당한다.</p></figcaption>
</figure>

## 주소를 찾아가는 길

등록이 끝난 뒤, 누군가 주소창에 이름을 치면 0.1초 사이에 이런 심부름이 일어난다.

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 540" role="img" aria-label="브라우저가 리졸버에 묻고 리졸버가 루트 서버와 닷컴 서버를 거쳐 권한 네임서버에서 IP를 받아 브라우저에 전달한다">
    <defs>
      <marker id="d8a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
      <marker id="d8b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-accent)"/></marker>
      <marker id="d8c" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--secondary)"/></marker>
    </defs>
    <rect x="180" y="12" width="380" height="68" rx="10" fill="var(--dgm-accent)"/>
    <text x="202" y="41" font-size="16.5" font-weight="700" fill="#fff">브라우저</text>
    <text x="202" y="64" font-size="13" fill="rgba(255,255,255,.82)"><tspan class="m">mystore.com</tspan>&#160;열기</text>
    <line x1="370" y1="80" x2="370" y2="116" stroke="currentColor" stroke-width="2" marker-end="url(#d8a)"/>
    <text x="576" y="102" font-size="12.5" fill="var(--secondary)">이 이름 어디야?</text>
    <rect x="180" y="116" width="380" height="68" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="202" y="145" font-size="16.5" font-weight="700" fill="currentColor">리졸버 · 안내데스크</text>
    <text x="202" y="168" font-size="13" fill="var(--secondary)">통신사나 공용 DNS가 대신 물어봄</text>
    <path d="M180,134 C 140,128 140,172 174,170" fill="none" stroke="var(--secondary)" stroke-width="1.8" stroke-dasharray="4 4" marker-end="url(#d8c)"/>
    <text x="126" y="150" font-size="12" fill="var(--secondary)" text-anchor="middle" transform="rotate(-90 126 150)">한 번 찾으면 캐시</text>
    <line x1="370" y1="184" x2="370" y2="220" stroke="currentColor" stroke-width="2" marker-end="url(#d8a)"/>
    <text x="576" y="206" font-size="12.5" fill="var(--secondary)">첫 번째 심부름</text>
    <rect x="180" y="220" width="380" height="68" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="202" y="249" font-size="16.5" font-weight="700" fill="currentColor">루트 서버</text>
    <text x="202" y="272" font-size="13" fill="var(--secondary)">".com 담당은 저쪽이야"</text>
    <line x1="370" y1="288" x2="370" y2="324" stroke="currentColor" stroke-width="2" marker-end="url(#d8a)"/>
    <text x="576" y="310" font-size="12.5" fill="var(--secondary)">두 번째 심부름</text>
    <rect x="180" y="324" width="380" height="68" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="202" y="353" font-size="16.5" font-weight="700" fill="currentColor">.com 서버 · 레지스트리</text>
    <text x="202" y="376" font-size="13" fill="var(--secondary)">담당 네임서버는&#160;<tspan class="m">ns1.host.com</tspan></text>
    <line x1="370" y1="392" x2="370" y2="428" stroke="currentColor" stroke-width="2" marker-end="url(#d8a)"/>
    <text x="576" y="414" font-size="12.5" fill="var(--secondary)">세 번째 심부름</text>
    <rect x="180" y="428" width="380" height="68" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="202" y="457" font-size="16.5" font-weight="700" fill="currentColor">권한 네임서버</text>
    <text x="202" y="480" font-size="13" fill="var(--secondary)">주소는&#160;<tspan class="m">203.0.113.42</tspan></text>
    <path d="M180,470 L76,470 L76,46 L174,46" fill="none" stroke="var(--dgm-accent)" stroke-width="2" marker-end="url(#d8b)"/>
    <text x="62" y="258" font-size="12.5" font-weight="700" fill="var(--dgm-accent)" text-anchor="middle" transform="rotate(-90 62 258)">찾은 IP를 돌려줌 → 접속</text>
    <text x="180" y="524" font-size="13" fill="var(--secondary)">여기까지 보통 0.1초</text>
  </svg>
  </div>
  <figcaption><p>한 번 찾은 답은 리졸버가 TTL만큼 기억해 둔다. 그래서 두 번째부터는 심부름 없이 바로 열린다.</p></figcaption>
</figure>

## 이것만은 기억하기

등록 자체보다 이 세 가지에서 사고가 난다.

- **사는 게 아니라 빌리는 것이다.** 등록은 소유권이 아니라 사용권이다. 갱신을 멈추는 순간 남이 가져갈 수 있다.
- **자동 갱신을 켜 둔다.** 만료 뒤 약 30일 유예, 그다음엔 비싼 복구비, 그다음엔 삭제되어 시장에 풀린다. 만료일 알림은 등록 당일에 걸어두는 게 좋다.
- **내 정보는 가릴 수 있다.** 등록자 이름·주소·전화는 WHOIS에 공개된다. 대부분의 창구가 개인정보 보호를 무료로 제공한다.

---

예시에 쓴 `mystore.com`과 `203.0.113.42`는 설명용이다. `203.0.113.0/24` 대역은 [RFC 5737](https://datatracker.ietf.org/doc/html/rfc5737)에서 문서용으로 예약한 주소다.
