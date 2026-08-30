---
title: "도메인 등록, 그림으로 이해하기"
date: 2026-08-30T16:13:10+09:00
draft: false
slug: "how-domains-get-registered"
translationKey: "how-domains-get-registered"
categories: ["개발"]
tags: ["dns", "domain", "네트워크", "입문"]
summary: "도메인이 어떻게 내 것이 되고, 주소창에 친 이름이 어떻게 서버를 찾아가는지 — 그림 아홉 장으로 정리했다."
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

## 등록은 다섯 스텝

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

등록이 끝난 뒤, 누군가 주소창에 이름을 치면 0.1초 사이에 질문이 오간다. 단, 처음 한 번만이다.

### 처음 물어볼 때

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 596" role="img" aria-label="브라우저가 리졸버에 묻고, 캐시가 비어 있어 리졸버가 루트 서버와 닷컴 서버를 거쳐 권한 네임서버에서 IP를 받아 브라우저에 전달하고 그 답을 캐시에 저장한다">
    <defs>
      <marker id="d8a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
      <marker id="d8b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-accent)"/></marker>
      <marker id="d8c" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-go)"/></marker>
    </defs>
    <rect x="190" y="14" width="330" height="66" rx="10" fill="var(--dgm-accent)"/>
    <text x="212" y="43" font-size="16.5" font-weight="700" fill="#fff">브라우저</text>
    <text x="212" y="66" font-size="13" fill="rgba(255,255,255,.82)"><tspan class="m">mystore.com</tspan>&#160;열기</text>
    <line x1="355" y1="80" x2="355" y2="118" stroke="currentColor" stroke-width="2" marker-end="url(#d8a)"/>
    <text x="370" y="104" font-size="12.5" fill="var(--secondary)">이 이름 어디야?</text>
    <rect x="190" y="118" width="330" height="94" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="212" y="147" font-size="16.5" font-weight="700" fill="currentColor">리졸버 · 안내데스크</text>
    <text x="212" y="170" font-size="13" fill="var(--secondary)">통신사나 공용 DNS가 대신 물어봄</text>
    <text x="212" y="192" font-size="13" fill="var(--secondary)">먼저 캐시부터 확인한다</text>
    <line x1="520" y1="165" x2="538" y2="165" stroke="var(--tertiary)" stroke-width="1.5"/>
    <rect x="540" y="130" width="168" height="70" rx="10" fill="none" stroke="var(--tertiary)" stroke-width="1.5" stroke-dasharray="5 4"/>
    <text x="560" y="159" font-size="14" font-weight="700" fill="var(--secondary)">캐시</text>
    <text x="560" y="181" font-size="12.5" fill="var(--secondary)">지금은 비어 있음</text>
    <line x1="355" y1="212" x2="355" y2="254" stroke="currentColor" stroke-width="2" marker-end="url(#d8a)"/>
    <text x="370" y="237" font-size="12.5" fill="var(--secondary)">첫 번째 질문</text>
    <rect x="190" y="254" width="330" height="68" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="212" y="283" font-size="16.5" font-weight="700" fill="currentColor">루트 서버</text>
    <text x="212" y="306" font-size="13" fill="var(--secondary)">".com 담당은 저쪽이야"</text>
    <line x1="355" y1="322" x2="355" y2="364" stroke="currentColor" stroke-width="2" marker-end="url(#d8a)"/>
    <text x="370" y="347" font-size="12.5" fill="var(--secondary)">두 번째 질문</text>
    <rect x="190" y="364" width="330" height="68" rx="10" fill="var(--code-bg)" stroke="var(--tertiary)" stroke-width="1.5"/>
    <text x="212" y="393" font-size="16.5" font-weight="700" fill="currentColor">.com 서버 · 레지스트리</text>
    <text x="212" y="416" font-size="13" fill="var(--secondary)">담당 네임서버는&#160;<tspan class="m">ns1.host.com</tspan></text>
    <line x1="355" y1="432" x2="355" y2="474" stroke="currentColor" stroke-width="2" marker-end="url(#d8a)"/>
    <text x="370" y="457" font-size="12.5" fill="var(--secondary)">세 번째 질문</text>
    <rect x="190" y="474" width="330" height="72" rx="10" fill="var(--code-bg)" stroke="var(--dgm-go)" stroke-width="2"/>
    <text x="212" y="503" font-size="16.5" font-weight="700" fill="currentColor">권한 네임서버</text>
    <text x="212" y="526" font-size="13" fill="var(--secondary)">주소는&#160;<tspan class="m">203.0.113.42</tspan></text>
    <path d="M190,516 L82,516 L82,48 L184,48" fill="none" stroke="var(--dgm-accent)" stroke-width="2" marker-end="url(#d8b)"/>
    <text x="66" y="282" font-size="12.5" font-weight="700" fill="var(--dgm-accent)" text-anchor="middle" transform="rotate(-90 66 282)">찾은 IP를 돌려줌 → 접속</text>
    <path d="M520,505 L628,505 L628,206" fill="none" stroke="var(--dgm-go)" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#d8c)"/>
    <text x="650" y="356" font-size="12.5" font-weight="700" fill="var(--dgm-go)" text-anchor="middle" transform="rotate(-90 650 356)">이 답을 TTL 동안 캐시에 저장</text>
    <text x="190" y="576" font-size="13" fill="var(--secondary)">여기까지 보통 0.1초. 이렇게 묻는 건 처음 한 번뿐이다.</text>
  </svg>
  </div>
  <figcaption><p>루트와 .com 서버는 답을 모른다. "저쪽에 물어봐"라고 넘길 뿐이다. 실제 IP를 들고 있는 건 맨 아래 한 곳이고, 그 답은 돌아오는 길에 캐시에 담긴다.</p></figcaption>
</figure>

### 두 번째부터는 캐시

<figure class="dgm">
  <div class="dgm-scroll">
  <svg viewBox="0 0 720 272" role="img" aria-label="두 번째 요청은 리졸버 캐시에 답이 남아 있어 루트 서버, 닷컴 서버, 권한 네임서버까지 가지 않고 곧바로 응답한다">
    <defs>
      <marker id="d9a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
      <marker id="d9b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--dgm-go)"/></marker>
    </defs>
    <rect x="20" y="48" width="180" height="104" rx="10" fill="var(--dgm-accent)"/>
    <text x="110" y="92" font-size="16" font-weight="700" fill="#fff" text-anchor="middle">브라우저</text>
    <text class="m" x="110" y="117" font-size="13" fill="rgba(255,255,255,.82)" text-anchor="middle">mystore.com</text>
    <line x1="208" y1="80" x2="462" y2="80" stroke="currentColor" stroke-width="2" marker-end="url(#d9a)"/>
    <text x="335" y="68" font-size="12.5" fill="var(--secondary)" text-anchor="middle">이 이름 어디야?</text>
    <line x1="462" y1="122" x2="208" y2="122" stroke="var(--dgm-go)" stroke-width="2" marker-end="url(#d9b)"/>
    <text x="335" y="143" font-size="12.5" font-weight="700" fill="var(--dgm-go)" text-anchor="middle">캐시에 있음 → 바로 응답</text>
    <rect x="470" y="48" width="230" height="104" rx="10" fill="var(--code-bg)" stroke="var(--dgm-go)" stroke-width="2"/>
    <text x="585" y="82" font-size="16" font-weight="700" fill="currentColor" text-anchor="middle">리졸버</text>
    <text x="585" y="105" font-size="12.5" fill="var(--secondary)" text-anchor="middle">캐시에 답이 남아 있음</text>
    <text class="m" x="585" y="130" font-size="14" fill="var(--dgm-go)" text-anchor="middle">203.0.113.42</text>
    <text x="20" y="207" font-size="12.5" font-weight="700" fill="var(--secondary)">이번엔 여기까지 안 감</text>
    <rect x="190" y="182" width="150" height="40" rx="8" fill="none" stroke="var(--tertiary)" stroke-width="1.5" stroke-dasharray="5 4"/>
    <text x="265" y="207" font-size="13" fill="var(--secondary)" text-anchor="middle">루트 서버</text>
    <rect x="350" y="182" width="150" height="40" rx="8" fill="none" stroke="var(--tertiary)" stroke-width="1.5" stroke-dasharray="5 4"/>
    <text x="425" y="207" font-size="13" fill="var(--secondary)" text-anchor="middle">.com 서버</text>
    <rect x="510" y="182" width="190" height="40" rx="8" fill="none" stroke="var(--tertiary)" stroke-width="1.5" stroke-dasharray="5 4"/>
    <text x="605" y="207" font-size="13" fill="var(--secondary)" text-anchor="middle">권한 네임서버</text>
    <text x="20" y="254" font-size="13" fill="var(--secondary)">TTL이 끝나면 캐시에서 지워지고, 그다음 요청은 다시 처음처럼 세 번을 묻는다.</text>
  </svg>
  </div>
  <figcaption><p>질문 0회. 실제 인터넷 트래픽은 대부분 이쪽이다. 도메인 설정을 바꿔도 바로 안 보이는 이유이기도 하다.</p></figcaption>
</figure>

### 권한 네임서버가 하는 일

영어로는 **authoritative nameserver**다. "이 이름에 대한 답을 확정적으로 가진 서버"라는 뜻이고, 앞의 두 서버와 결정적으로 다른 점이 그거다.

루트 서버와 .com 서버는 `mystore.com`의 IP를 모른다. 각각 ".com은 저쪽", "그 도메인은 `ns1.host.com`이 안다"라고 **넘겨줄 뿐이다**. 실제 레코드를 보관하고 최종 답을 내놓는 건 맨 아래 한 곳이다. 5단계에서 NS로 지정한 바로 그 서버이고, 보통 창구나 호스팅 업체(또는 Cloudflare 같은 DNS 서비스)가 대신 운영해 준다.

여기 들어 있는 게 도메인 관리 화면에서 우리가 만지는 그 레코드들이다.

- `A` / `AAAA` — 이 이름의 IP 주소 (IPv4 / IPv6)
- `CNAME` — "이 이름은 저 이름과 같다"
- `MX` — 이 도메인으로 오는 메일을 받을 서버
- `TXT` — 소유 확인, 메일 인증(SPF·DKIM) 같은 메모

엄밀히 말하면 루트 서버도 루트 존(zone)의 권한 네임서버이고, .com 서버도 .com 존의 권한 네임서버다. 각자 자기 층의 답에는 권한이 있다. 다만 우리가 찾는 이름의 최종 답을 가진 건 맨 아래 한 곳이라, 보통 그쪽을 가리켜 부른다.

리졸버가 캐시에서 꺼내 주는 답은 원본이 아니라 사본이다. `dig`로 조회하면 응답 헤더의 `aa`(authoritative answer) 플래그로 구분된다.

```
$ dig mystore.com                   # 리졸버에게 묻기
;; flags: qr rd ra;                 ← aa 없음 = 캐시에서 온 사본

$ dig @ns1.host.com mystore.com     # 권한 네임서버에 직접 묻기
;; flags: qr aa rd;                 ← aa 있음 = 원본
```

레코드를 고칠 때 실제로 바뀌는 곳도 여기다. 원본은 즉시 바뀌지만 전 세계 리졸버 캐시에는 옛날 답이 TTL만큼 남아 있다. 바꾼 게 바로 안 보이는 이유가 이것이고, 그래서 서버 이사가 예정돼 있으면 며칠 전에 TTL을 300초쯤으로 줄여 두는 게 요령이다.

## 이것만은 기억하기

등록 자체보다 이 세 가지에서 사고가 난다.

- **사는 게 아니라 빌리는 것이다.** 등록은 소유권이 아니라 사용권이다. 갱신을 멈추는 순간 남이 가져갈 수 있다.
- **자동 갱신을 켜 둔다.** 만료 뒤 약 30일 유예, 그다음엔 비싼 복구비, 그다음엔 삭제되어 시장에 풀린다. 만료일 알림은 등록 당일에 걸어두는 게 좋다.
- **내 정보는 가릴 수 있다.** 등록자 이름·주소·전화는 WHOIS에 공개된다. 대부분의 창구가 개인정보 보호를 무료로 제공한다.

## 실전편

여기까지가 개념이다. 실제로 `byeorim.com`을 사서 페이지를 붙여보니 **순서가 달랐고, 이 그림들에 없던 것들이 나왔다.**

- **"그런 주소 없다"는 답도 캐시에 남는다.** 설정을 끝내기 전에 궁금해서 한 번 조회하면, 그 "없음"이 내 리졸버에 30분쯤 박힌다. "분명 설정했는데 왜 안 되지"의 가장 흔한 정체다.
- **apex 도메인(`byeorim.com`처럼 서브도메인 없는 루트)에는 CNAME을 달 수 없다.** 그래서 GitHub Pages는 고정 IP 네 개를 직접 박으라고 안내한다.
- **포함이라던 DNSSEC이 꺼져 있었다.**

→ [「도메인 사서 웹페이지 붙이기, 실제로 해봤다」](/posts/buying-a-domain-in-practice/) — 1시간 반, 연 $10.46짜리 기록.

---

예시에 쓴 `mystore.com`과 `203.0.113.42`는 설명용이다. `203.0.113.0/24` 대역은 [RFC 5737](https://datatracker.ietf.org/doc/html/rfc5737)에서 문서용으로 예약한 주소다.
