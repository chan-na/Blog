---
title: "도메인 사서 웹페이지 붙이기, 실제로 해봤다"
date: 2026-08-31T00:50:19+09:00
draft: false
slug: "buying-a-domain-in-practice"
translationKey: "buying-a-domain-in-practice"
categories: ["개발"]
tags: ["dns", "domain", "cloudflare", "workers", "네트워크"]
summary: "byeorim.com을 사서 Cloudflare Workers에 붙이기까지 1시간 반. 개념편 그림에는 없던 것들 — 없다는 답까지 캐싱된다는 것, apex의 CNAME 제약, 포함이라더니 꺼져 있던 DNSSEC — 을 실제로 만난 기록."
---

지난 글 [「도메인 등록, 그림으로 이해하기」](/posts/how-domains-get-registered/)에서 등록 절차를 다섯 스텝으로 정리했다. 도메인을 고르고, 비어 있는지 확인하고, 창구에서 1년치를 내고, 이메일을 인증하고, 내 서버를 연결한다.

그림은 맞았다. 그런데 실제로 `byeorim.com`을 사서 페이지를 붙여보니 **순서가 달랐고, 그림에 없던 것들이 나왔다.** 걸린 시간은 1시간 반, 비용은 연 $10.46.

이 글은 그 기록이다. 개념편에서 그림으로 그렸던 것들이 실제 화면과 터미널에서 어떻게 나타나는지를 따라간다.

만든 것은 Cloudflare Registrar에서 산 도메인 + GitHub organization 랜딩페이지 + Cloudflare Workers 배포다.

## 창구부터 고른다

개념편에서 "창구"라고 부른 레지스트라는 한 곳이 아니다. 국내에는 가비아·후이즈, 해외에는 Namecheap·Porkbun·AWS Route 53 같은 곳들이 있다.

어디서 사든 **등록되는 도메인 자체는 똑같다.** `.com`의 레지스트리는 Verisign 하나뿐이고, 레지스트라는 그 앞에 늘어선 창구들일 뿐이다. 최종적으로 `.com` 존에 기록되는 내용은 같다. 창구마다 다른 건 가격, DNS 관리 화면, 끼워주는 부가 기능이다.

이번엔 Cloudflare Registrar를 골랐다. 이유는 두 가지다.

- **도메인·DNS·인증서·배포가 한 계정에서 끝난다.** 뒤에서 보겠지만 이게 DNSSEC을 켤 때 실제로 차이를 만든다.
- **가격 정책이 특이하다.** 바로 다음 절의 내용이다.

미리 밝혀두면, **아래 가격 얘기는 Cloudflare의 정책이지 레지스트라 일반의 얘기가 아니다.** 오히려 업계에서는 예외에 가깝다.

## "비어 있는지 확인한다"를 제대로 하는 법

레지스트라 검색창에 치면 알려준다. 그런데 그건 그 회사의 대답이다. 원본에 직접 물어보는 게 확실하다.

먼저 `whois`. **도메인의 등록 장부를 조회하는 도구**다. 누가 언제 등록했고 언제 만료되는지를 답한다.

```
$ whois byeorim.com | head
% IANA WHOIS server
refer:        whois.verisign-grs.com
domain:       COM
organisation: VeriSign Global Registry Services
```

첫 조회는 답을 주지 않는다. **IANA는 "그건 내 담당이 아니고 Verisign한테 물어봐"라고 안내(refer)만 한다.** whois는 2단계다. 루트(IANA)에 어느 레지스트리 소관인지 묻고, 그 레지스트리에 다시 묻는다.

```
$ whois -h whois.verisign-grs.com byeorim.com
No match for domain "BYEORIM.COM".
```

이제 진짜 답이다. 그리고 더 간단한 확인법이 하나 더 있다.

`dig`는 **DNS에 직접 질의하는 도구**다. 등록 장부가 아니라, 그 도메인이 지금 어떤 IP로 풀리고 어느 네임서버가 담당인지를 답한다.

```
$ dig +short byeorim.com NS
                              ← 아무것도 안 나온다
```

**NS 레코드가 비어 있으면 미등록이다.** 등록된 도메인은 A 레코드가 없어도 NS는 반드시 있다. 레지스트리가 상위 존에 "이 도메인은 저 네임서버에게 물어봐"라는 위임 정보를 박아두기 때문이다. NS가 없다는 건 `.com` 존에 이 도메인 자체가 없다는 뜻이다.

## 창구에서 1년치를 낸다 — 첫해 가격 = 갱신 가격

검색 결과 화면의 부제가 이 서비스의 전부를 요약한다.

![도메인 검색 결과와 가격](/images/domain-setup/04-search-results.jpg)

> Find and register a new domain **at cost, with no markup.**

| 도메인 | 첫해 | 갱신 |
|---|---|---|
| **byeorim.com** | **$10.46** | **$10.46/year** |
| byeorim.com.mx | $16.75 | $16.75/year |
| byeorim.com.ai | $160.00 | $80.00/year |
| byeorim.computer | $30.20 | $30.20/year |

**첫해 가격과 갱신 가격이 같다.** 이게 핵심이다.

보통 레지스트라는 첫해를 $0.99~$2로 후려치고 갱신 때 $18~20을 받는다. 도메인은 한 번 정하면 바꾸기가 지독하게 어렵다. 메일 주소, 배포한 링크, 검색 순위가 전부 그 도메인에 묶인다. 갱신 시점에 우리는 사실상 인질이 된다.

$10.46의 내역은 Verisign이 `.com` 레지스트리로 받는 도매가와 ICANN 수수료 $0.18이다. 레지스트라 몫이 0이다.

여담으로, 같은 도메인을 두 번 검색했더니 `byeorim.com.co` 가격이 $10.00에서 $15.00으로 바뀌어 있었다. 이 화면의 숫자는 도매가를 그대로 실어나르는 값이라 그 시점의 값일 뿐이다.

## 집 주소를 왜 내야 하나

결제 직전에 등록자 정보를 요구한다. 이름, 이메일, 전화번호, 국가, 주소, 도시, 우편번호. 전부 필수다.

![등록자 정보 폼과 WHOIS 고지](/images/domain-setup/06-checkout-whois-notice.jpg)

Cloudflare가 원해서가 아니다. 개념편에서 말한 **"사는 게 아니라 빌리는 것"** 이 여기서 실물로 나타난다. 도메인은 연 단위 임대고, ICANN은 임차인이 누군지 기록에 남기도록 레지스트라에게 의무를 지운다.

폼 하단의 고지가 정직하다.

> Cloudflare Registrar redacts registrant personal information from its public WHOIS service; however, it cannot control whether **the registry** redacts personal information from its own WHOIS service.

WHOIS는 레지스트라와 레지스트리 두 군데에 따로 있다. 자기 쪽은 가려주지만 레지스트리 쪽까지는 통제하지 못한다는 뜻이다. 이 말이 실제로 무슨 의미인지는 뒤에서 직접 조회해 확인한다.

결제 화면에는 이런 게 붙어 있었다.

![결제 화면의 무료 포함 항목](/images/domain-setup/11-payment-screen.jpg)

> **Included at no extra cost**
>
> - WHOIS Privacy — Hide your personal information
> - DNSSEC — DNS security extensions
> - Email Forwarding — Create email aliases

셋 다 다른 곳에서는 파는 물건이다. WHOIS privacy만 해도 보통 연 $8~15짜리 애드온이다. 마진 0으로 팔면서 유료 옵션까지 얹어주는 이유는 하나다. 도메인으로 돈을 벌 생각이 없고, 그 도메인의 트래픽이 자기 네트워크를 지나가는 게 목적이다.

(이 "포함"이라는 표현에는 함정이 있다. 뒤에서 다룬다.)

## 결제했는데 세상은 아직 모른다

결제가 끝나자 화면은 이렇게 말했다.

![등록 완료 화면](/images/domain-setup/12-registration-success.jpg)

그런데 바로 whois를 쳤더니:

```
$ whois -h whois.verisign-grs.com byeorim.com
No match for domain "BYEORIM.COM".
```

**내 화면에는 샀다고 나오는데 레지스트리는 아직 모른다.** 결제 완료는 레지스트라의 장부에 기록된 사건이고, 레지스트리 등재는 `.com` 존의 진실이 바뀌는 사건이다. 둘은 다른 일이고 사이에 시차가 있다.

20초 간격으로 찔러보니 약 1분 뒤에 올라왔다.

```
Domain Name: BYEORIM.COM
Creation Date: 2026-08-30T12:55:42Z
Registry Expiry Date: 2027-08-30T12:55:42Z
Registrar: Cloudflare, Inc.
Domain Status: clientTransferProhibited
Name Server: DAVID.NS.CLOUDFLARE.COM
Name Server: KAMI.NS.CLOUDFLARE.COM
```

만료일이 등록일 + 정확히 1년. `clientTransferProhibited`는 레지스트라가 걸어둔 이전 잠금으로, 누가 몰래 다른 레지스트라로 옮겨가는 걸 막는다. 네임서버 이름이 `david`와 `kami`인 건 Cloudflare가 계정마다 사람 이름 같은 쌍을 배정하기 때문이다. 기능적 의미는 없다.

## WHOIS 가림은 어디까지인가

개념편에서 "내 정보는 가릴 수 있다"고 썼다. 방금 입력한 정보로 실제로 확인했다.

그런데 **어디에 물어보느냐가 중요하다.** `.com` 레지스트리에 직접 물으면 등록자 정보가 아예 안 나온다.

```
$ whois -h whois.verisign-grs.com byeorim.com
Domain Name: BYEORIM.COM
Registrar: Cloudflare, Inc.
Registrar WHOIS Server: whois.cloudflare.com
Creation Date: 2026-08-30T12:55:42Z
...
                                      ← Registrant 필드가 하나도 없다
```

`.com`은 **thin registry**다. 레지스트리는 도메인명·날짜·레지스트라·네임서버·상태만 들고 있고, **등록자 연락처는 보관하지 않는다.** 대신 `Registrar WHOIS Server`로 "그건 저기 가서 물어봐"라고 안내한다. 등록자 정보는 레지스트라가 갖고 있다.

그래서 앞의 검색 때처럼 한 번 더 물어야 한다.

```
$ whois -h whois.cloudflare.com byeorim.com

Registrant Name:           DATA REDACTED
Registrant Organization:   DATA REDACTED
Registrant Street:         DATA REDACTED
Registrant City:           DATA REDACTED
Registrant Postal Code:    DATA REDACTED
Registrant Email:          (빈 값)

Registrant State/Province: <시/도>          ← 가려지지 않는다
Registrant Country:        KR               ← 가려지지 않는다
Registrant Phone:          +1.4153197517    ← 다른 번호로 치환된다
```

(그냥 `whois byeorim.com` 으로도 이 결과가 나오는 경우가 있다. `whois` 클라이언트가 레지스트리 응답의 `Registrar WHOIS Server` 안내를 자동으로 한 번 더 따라가느냐에 달렸고, 구현마다 다르다. macOS 기본 `whois`는 따라간다. 안 나온다면 위처럼 `-h`로 레지스트라를 직접 지정하면 된다.)

세 가지가 읽힌다.

**이름·주소·이메일은 정말로 가려진다.** "이걸 왜 내야 하나" 했던 정보들이 실제로는 공개되지 않는다.

**그런데 시/도와 국가는 가려지지 않는다.** ICANN이 이 두 필드는 공개 유지를 요구한다. 분쟁이 생겼을 때 어느 나라 법이 적용되는지 판단할 근거가 필요하다는 논리다. 프라이버시 서비스가 전부를 가려주지는 않는다.

**전화번호는 빈칸이 아니라 다른 번호로 바뀐다.** `+1.415`는 샌프란시스코 지역번호, Cloudflare 자기 번호다. 법적 통지가 오면 받을 창구는 남기되 실제 번호는 숨기는 방식이다.

그리고 체크아웃 폼 하단에 있던 고지 — *"레지스트리 쪽 WHOIS까지는 통제하지 못한다"* — 가 여기서 해소된다. `.com`은 thin registry라 **레지스트리가 애초에 등록자 정보를 갖고 있지 않다. 흘릴 것이 없다.** 다만 `.org`처럼 레지스트리가 연락처를 직접 보관하는 **thick registry**도 있다. 그런 TLD에서는 레지스트라의 가림이 닿지 않는 영역이 실제로 존재한다. 그 고지는 빈말이 아니라 TLD에 따라 달라지는 조건이었던 셈이다.

## 사이트가 도메인보다 먼저 살았다

개념편에서 "내 서버를 연결한다"는 **마지막** 스텝이었다. 실제로는 순서를 지킬 필요가 없었다.

결제를 기다리는 동안 랜딩페이지를 먼저 배포했다. 그전에 어디에 올릴지부터 정해야 했다. 후보는 셋이었다.

| | 방식 | 커스텀 도메인 | 서버 로직 |
|---|---|---|---|
| **GitHub Pages** | 레포에 푸시하면 배포 | apex에 고정 IP 4개를 A 레코드로 직접 입력 | 없음 (정적 전용) |
| **Cloudflare Pages** | git 연동 빌드 | Cloudflare DNS면 클릭 몇 번 | Functions |
| **Cloudflare Workers** | `wrangler`로 업로드 | 설정 파일에 한 줄, DNS 레코드 자동 생성 | 처음부터 가능 |

이 블로그 자체는 GitHub Pages에서 돌아간다. 정적 사이트에는 충분하고 무료다. 그런데 이번엔 두 가지가 걸렸다. **apex 도메인을 붙이려면 GitHub의 IP 네 개를 직접 박아야 하고**(뒤에서 왜 그런지 다룬다), 나중에 서버 쪽 처리를 붙이려면 아예 다른 데로 옮겨야 한다.

남은 건 Cloudflare의 Pages와 Workers인데, 이건 Cloudflare가 직접 답을 준다. Pages 공식 문서 첫머리에 이렇게 적혀 있다 — "Start new projects with Workers." Workers가 Pages의 기능을 대부분 포함하고 더 넓으며, Cloudflare의 주력 플랫폼이라는 것이다.

**결정적인 건 도메인이 이미 Cloudflare에 있다는 점이었다.** 레지스트라·DNS·인증서·호스팅이 한 계정에 모이면 붙이는 단계가 통째로 사라진다. 실제로 뒤에서 보겠지만, DNS 레코드를 손으로 만들 일이 없었다.

그래서 Workers로 갔다. Cloudflare Workers 설정 파일 `wrangler.jsonc` 는 이게 전부다.

```jsonc
{
  "name": "byeorim-landing",
  "compatibility_date": "2026-08-30",
  "assets": { "directory": "./public" }
}
```

`main` 필드가 없다는 게 눈여겨볼 지점이다. 보통 Worker는 `main: "src/index.ts"`로 진입점 스크립트를 지정하고, 요청이 오면 그 스크립트가 응답을 만든다. `assets`만 있고 `main`이 없으면 **JavaScript가 한 줄도 없는 Worker**가 된다. Cloudflare가 엣지에서 정적 파일을 바로 꽂아주고, 이런 요청은 Worker 실행 횟수로 계산되지도 않는다.

배포는 `wrangler`로 한다. **Cloudflare Workers를 다루는 공식 CLI**다. 설정 파일을 읽어 코드와 정적 파일을 Cloudflare에 올리고, 로컬 실행(`wrangler dev`)과 배포(`wrangler deploy`)를 담당한다. `npx`를 붙이면 따로 설치하지 않고 바로 쓸 수 있다.

```
$ npx wrangler deploy
✨ Read 1 file from the assets directory ./public
+ /index.html
Total Upload: 0.34 KiB / gzip: 0.25 KiB
  https://byeorim-landing.byeorim-com.workers.dev
```

8초 만에 사이트가 인터넷에 올라갔다. **도메인은 아직 사지도 않았는데.**

이 순서가 우연히 중요한 걸 보여줬다. **사이트와 도메인은 원래 별개다.** 사이트는 도메인 없이도 존재할 수 있고(지금 상태), 도메인은 가리킬 곳 없이도 존재할 수 있다. 둘을 잇는 건 마지막의 DNS 레코드 한 줄이다.

## DNS는 됐는데 HTTPS가 안 된다

배포 직후에 확인해보니 이상한 상태였다.

```
$ dig +short byeorim-landing.byeorim-com.workers.dev
104.21.63.79
172.67.144.54                    ← 도메인은 이미 IP로 풀린다

$ curl https://byeorim-landing.byeorim-com.workers.dev
curl: (35) SSL routines:ST_CONNECT:sslv3 alert handshake failure
                                 ← 그런데 TLS는 거절당한다
```

**도메인이 IP로 풀리는 것과, 그 IP가 이 도메인으로 HTTPS를 받을 준비가 된 것은 다른 일이다.** DNS 레코드는 즉시 반영되지만 인증서는 CA에 발급을 요청하고 받아와야 한다. "사이트는 떴는데 브라우저가 경고를 띄운다"의 정체가 대부분 이거다.

15초 간격으로 찔러봤다.

```
[21:23:46] 시도 1 → handshake failure
[21:24:01] 시도 2 → handshake failure
[21:24:16] 시도 3 → handshake failure
[21:24:31] 시도 4 → handshake failure
[21:24:47] 시도 5 → 200          ← 발급 완료
```

배포부터 약 1분 30초. 발급된 인증서를 뜯어보면 왜 이게 한 번뿐인지도 보인다.

```
issuer=C=US, O=Google Trust Services, CN=WE1
subject=CN=byeorim-com.workers.dev
X509v3 Subject Alternative Name:
    DNS:byeorim-com.workers.dev, DNS:*.byeorim-com.workers.dev
```

발급자가 Cloudflare가 아니라 Google Trust Services다. Cloudflare는 CA가 아니라 여러 CA에서 인증서를 받아다 자동으로 깔아주는 중개자다. 그리고 **와일드카드**라서 이 계정의 모든 Worker가 이 한 장으로 커버된다. 우리가 기다린 1분 30초는 이 계정의 첫 배포라서 치른 값이다.

인증서는 누가 발급하고, 브라우저는 그걸 왜 믿나. 여기서 한 줄로 지나간 CA·서명·신뢰 사슬은 [「인증서와 CA, 그림으로 이해하기」](/posts/certificates-and-cas/)에서 그림으로 폈다.

## apex에는 CNAME을 못 다는데

이제 도메인을 붙인다. 앞에서 본 Cloudflare Workers 설정 파일 `wrangler.jsonc` 에 세 줄을 더했다.

```jsonc
"routes": [
  { "pattern": "byeorim.com",     "custom_domain": true },
  { "pattern": "www.byeorim.com", "custom_domain": true }
]
```

`custom_domain: true`가 있으면 wrangler가 **DNS 레코드까지 대신 만든다.** 대시보드에서 손으로 찍을 게 없다. 그런데 만들어진 레코드가 예상 밖이었다.

![DNS 레코드 타입이 Worker다](/images/domain-setup/13-dns-records-worker.jpg)

| Name | Type | Content | Proxy status |
|---|---|---|---|
| byeorim.com | **Worker** | byeorim-landing | 🟠 Proxied |
| www.byeorim.com | **Worker** | byeorim-landing | 🟠 Proxied |

타입이 `A`도 `CNAME`도 아닌 **`Worker`** 다. DNS 표준에 그런 레코드 타입은 없다. Cloudflare 내부의 가상 레코드고, 자물쇠가 붙어 손으로 수정할 수도 없다.

**이게 apex 문제의 해법이다.**

DNS 표준상 apex — `byeorim.com`처럼 서브도메인 없는 루트 — 에는 CNAME을 달 수 없다.

CNAME은 "이 DNS 이름에 딸린 모든 레코드를 저쪽으로 넘겨라"라는 뜻이다. 그래서 **CNAME이 있는 이름에는 다른 레코드가 함께 있을 수 없다.** 그런데 apex에는 반드시 있어야 하는 레코드가 둘 있다.

- **NS** (Name Server) — 이 존을 담당하는 네임서버 목록. 앞에서 도메인이 비어 있는지 확인할 때 조회했던 그 레코드다.
- **SOA** (Start of Authority) — 존의 관리 정보를 담은 레코드. 대표 네임서버, 관리자 메일 주소, 일련번호, 그리고 각종 TTL이 한 줄에 들어 있다. 뒤에서 만날 negative TTL도 여기서 읽는다.

둘 다 apex에서 뺄 수 없다. 그러니 apex에 CNAME을 놓는 순간 "다른 레코드가 없어야 한다"는 조건과 정면으로 부딪친다. 그래서 GitHub Pages 같은 서비스는 apex에 고정 IP 네 개를 A 레코드로 직접 박으라고 안내한다. 그 IP가 바뀌면 사용자가 직접 고쳐야 한다.

Cloudflare는 아예 다른 길로 간다. 자기가 **권한 네임서버**(authoritative nameserver) — 이 도메인에 대해 최종적으로 답할 자격이 있는 서버 — 이기 때문에, 질의가 오는 순간 **A/AAAA 응답을 즉석에서 합성해** 돌려준다. 밖에서 보면 평범한 A 레코드다.

```
$ dig @david.ns.cloudflare.com +short byeorim.com A
172.67.192.105
104.21.81.254
```

이 IP는 이 도메인 전용이 아니라 Cloudflare 애니캐스트 대역이다. 요청이 도착하면 `Host` 헤더와 TLS SNI를 보고 어느 Worker로 보낼지 판단한다. `Proxied`(주황 구름)가 그 뜻이다.

## 함정: routes를 넣으면 workers.dev가 꺼진다

배포 로그에 경고가 하나 있었다.

```
▲ WARNING  Because 'workers_dev' is not in your Wrangler file,
           it will be disabled for this deployment by default.
```

무시하고 넘어갔다가 확인해보니:

```
$ curl -o /dev/null -w "%{http_code}" https://byeorim-landing.byeorim-com.workers.dev
404
```

잘 돌던 URL이 죽었다. `routes`가 없을 때는 workers.dev가 기본 ON인데, `routes`를 명시하는 순간 기본값이 OFF로 뒤집힌다. 커스텀 도메인을 붙였으니 workers.dev는 안 쓰겠거니 하는 것이다.

둘 다 살리려면 `"workers_dev": true`를 명시해야 한다. 개발 중에 workers.dev URL을 팀에 공유하고 있었다면 이 배포 한 번에 링크가 전부 깨진다.

## dig는 되는데 curl은 안 된다

이 글에서 제일 오래 붙잡은 대목이다. 커스텀 도메인 배포 직후 상태가 이랬다.

| 확인 방법 | 결과 |
|---|---|
| Chrome에서 `https://byeorim.com` | ✅ 정상 |
| `dig byeorim.com A` | ✅ `172.67.192.105`, `104.21.81.254` |
| `curl https://byeorim.com` | ❌ Could not resolve host |
| `getaddrinfo()` (파이썬) | ❌ gaierror |

**같은 컴퓨터에서 동시에.** 흔히 겪는 "dig는 되는데 브라우저가 안 돼"의 정반대였다.

셋이 서로 다른 경로를 쓰기 때문이다.

- **`dig`** 는 리졸버에 **직접 DNS 패킷을 쏜다.** OS 캐시를 안 거친다.
- **`curl`을 비롯한 대부분의 프로그램**은 `getaddrinfo()`로 **OS에 물어본다.** macOS에서는 `mDNSResponder`가 받아서 자체 캐시를 먼저 본다.
- **Chrome**은 자체 DNS 스택을 갖고 있고, Secure DNS(DoH)를 쓰면 OS를 아예 건너뛴다.

`mDNSResponder`가 뭘 붙들고 있었는지도 보였다.

```
$ dscacheutil -q host -a name byeorim.com
name: byeorim.com
ipv6_address: 2606:4700:3030::ac43:c069
ipv6_address: 2606:4700:3034::6815:51fe
```

AAAA(IPv6)만 있고 A(IPv4)가 없다. A 질의에 대한 **"없음" 응답을 캐싱 중**이었던 것이다. 그 수명은 SOA 레코드의 마지막 필드에 적혀 있다.

```
$ dig +short byeorim.com SOA
david.ns.cloudflare.com. dns.cloudflare.com. 2413580434 10000 2400 604800 1800
                                                                        ^^^^
                                                          negative TTL = 1800초 = 30분
```

**없다는 답도 캐싱된다.** 도메인을 설정하기 *전에* 궁금해서 한 번 조회해봤다면, 설정을 마쳐도 최대 30분간 "그런 도메인 없음"이 돌아온다. "분명 설정했는데 왜 안 되지"의 가장 흔한 정체다.

교훈은 단순하다. **설정을 끝내기 전에는 그 도메인을 조회하지 마라.** 미리 쳐본 그 한 번이 자기 리졸버에 30분짜리 "없음"을 심는다.

기다리기 싫으면 로컬 캐시를 우회해서 서버 쪽만 먼저 검증할 수 있다.

```
$ curl -sS --resolve byeorim.com:443:172.67.192.105 \
    -o /dev/null -w "status=%{http_code} ip=%{remote_ip}\n" https://byeorim.com
status=200  ip=172.67.192.105
```

`--resolve`로 IP를 직접 지정하면 DNS를 아예 건너뛴다. 이게 200이면 서버·라우팅·인증서는 전부 정상이고 남은 문제는 순수하게 내 컴퓨터라는 뜻이다. 실제로 캐시를 비우니 즉시 풀렸다.

```
$ sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder
$ curl -o /dev/null -w "%{http_code}\n" https://byeorim.com
200
```

디버깅 순서로 정리하면 이렇다.

1. `curl --resolve <도메인>:443:<IP>` → 200이면 서버는 정상. 문제는 DNS다.
2. `dig @<권한NS> <도메인>` → 값이 나오면 레코드는 존재한다. 문제는 캐시다.
3. `dig <도메인>` 은 되는데 `curl`이 안 되면 → **OS 캐시**다.
4. 캐시를 비운다.

## "포함"과 "켜짐"은 다른 얘기다

`byeorim.com`이 Worker로 연결되고 HTTPS까지 붙은 것을 확인한 뒤, Cloudflare 대시보드의 보안 설정을 처음부터 훑어봤다. 기본값 두 개가 예상과 달랐다.

**첫째, 평문 HTTP가 그대로 열려 있었다.**

```
$ curl -sSI http://byeorim.com
HTTP/1.1 200 OK
Server: cloudflare
                        ← Location 헤더가 없다
```

리다이렉트 없이 그냥 200이다. HTTPS 응답에 `Strict-Transport-Security` 헤더도 없었다. 정적 페이지라 훔칠 정보야 없지만, 경로상의 누군가가 내용을 보거나 **바꿔치기할 수 있다**는 뜻이다.

Cloudflare 대시보드에서 해당 도메인을 열고 **SSL/TLS → Edge Certificates** 로 들어가면 `Always Use HTTPS` 토글이 있다. 켜니:

```
$ curl -sSI http://byeorim.com
HTTP/1.1 301 Moved Permanently
Location: https://byeorim.com/
```

**둘째, DNSSEC이 꺼져 있었다.** 결제 화면에는 "무료 포함"으로 찍혀 있던 항목이다.

DNSSEC은 DNS 응답에 전자서명을 붙이는 규격이다. 원래 DNS는 응답의 진위를 검증하지 않는다. 리졸버는 돌아온 답이 진짜 그 도메인의 주인이 준 것인지, 중간에서 누가 바꿔치기한 것인지 구별할 방법이 없다. DNSSEC은 각 레코드에 서명을 달아 리졸버가 그걸 확인할 수 있게 한다.

실제로 켜져 있는지 세 가지로 확인했다.

```
$ dig +short byeorim.com DS
                                  ← 부모 존에 DS 없음
$ dig @david.ns.cloudflare.com +short byeorim.com DNSKEY
                                  ← 존에 키도 없음
$ dig @1.1.1.1 byeorim.com A +dnssec | grep "^;; flags:"
;; flags: qr rd ra;               ← ad 플래그 없음
```

전부 비어 있었다. **요금제에 포함되어 있다는 것과 활성화되어 있다는 것은 다른 얘기다.** 같은 대시보드의 **DNS → Settings** 에 있는 `Enable DNSSEC` 버튼을 눌러야 켜진다.

누르자 존에 키가 생겼다.

```
$ dig @david.ns.cloudflare.com +short byeorim.com DNSKEY
257 3 13 mdsswUyr3DPW132mOi8V9xESWE8jTo0dxCjjnopKl+Gq...
256 3 13 oJMRESz5E4gYzS/q6XDrvU1qMPYIjCWzJaOau8XNEZeq...
```

`257`은 KSK(Key Signing Key), `256`은 ZSK(Zone Signing Key), `13`은 ECDSA P-256 알고리즘이다.

**키가 생겼다는 건 존에 서명이 걸렸다는 뜻이다.** Cloudflare가 `byeorim.com` 존의 키 쌍을 만들고, 이 존의 모든 레코드에 개인키로 서명을 붙였다. 공개키는 위처럼 `DNSKEY` 레코드로 공개한다. 이제 이 존이 주는 응답에는 서명이 따라오고, 리졸버는 그 `DNSKEY`로 서명을 검증할 수 있다.

그런데 문제가 하나 남는다. **그 `DNSKEY` 자체가 진짜라는 건 누가 보증하나?** 공격자가 존을 통째로 위조하면서 자기 키까지 같이 심으면, 검증은 통과하지만 내용은 가짜다.

그래서 부모 존이 나선다. 부모 존(`.com`)에 **DS 레코드**(Delegation Signer)를 등록한다. 자식 존 키의 해시값, 즉 **지문**(fingerprint)이다. 리졸버는 `.com`에게 "byeorim.com의 키 지문이 뭐냐"고 묻고, 돌아온 지문이 실제로 받은 `DNSKEY`와 맞는지 대조한다. 맞으면 그 키를 믿어도 된다.

같은 논리가 위로 계속 이어진다. `.com`의 키는 루트가 보증하고, 루트의 키는 전 세계가 미리 알고 있다. 루트 → `.com` → `byeorim.com`으로 이어지는 이 연결이 **신뢰 사슬**(chain of trust)이다.

**그런데 DS 레코드가 한동안 올라오지 않았다.** 존에는 키가 있는데 부모는 아직 모르는 상태다. 이 중간 상태가 구조를 정확히 보여준다 — 서명만으로는 아무것도 증명되지 않는다. 부모의 보증이 붙어야 비로소 검증이 가능해진다.

그리고 DS는 레지스트리에 등록해야 하는 값이라 **레지스트라만 넣을 수 있다.** 여기서 레지스트라와 DNS를 같은 회사에 둔 이득이 나온다. 둘이 다르면 Cloudflare에서 DS 값을 복사해 레지스트라 관리 화면에 손으로 붙여넣어야 한다.

몇 분 뒤 DS 레코드가 올라오면서 사슬이 이어졌다.

```
$ dig +short byeorim.com DS
2371 13 2 F2DA3F181BBB3FB515DD197B7BC511539CD374BF23D1B328A47730E240CC4212

$ dig @1.1.1.1 byeorim.com A +dnssec | grep "^;; flags:"
;; flags: qr rd ra ad;
                  ^^
```

**`ad` = Authenticated Data.** 처음엔 `qr rd ra` 뿐이었다. 이제 1.1.1.1이 루트부터 이어지는 서명 사슬을 실제로 검증하고 "이 응답은 위조가 아니다"라고 표시해준다. 플래그 두 글자가 늘어난 것뿐이지만, 그 두 글자가 DNSSEC의 전부다.

## 최종 상태

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

개념편에서 남긴 세 가지 당부를 실제로 겪은 관점에서 다시 쓰면 이렇다.

- **사는 게 아니라 빌리는 것이다.** 체크아웃 화면이 이걸 계속 상기시킨다. 만료일이 등록일 + 1년으로 박히고, 등록자 정보를 요구하고, "non-refundable"이라고 적혀 있다.
- **자동 갱신은 켜둔다.** 기본으로 켜져 있었다. 끄지 않는 게 유일한 할 일이다.
- **내 정보는 가릴 수 있다. 단, 전부는 아니다.** 이름·주소·이메일은 가려지지만 시/도와 국가는 남는다.

여기에 하나 더 붙이자면, **기본값을 믿지 말고 직접 조회해봐야 한다.** "포함"이라고 적힌 DNSSEC은 꺼져 있었고, HTTPS 강제도 꺼져 있었다. `dig`와 `curl` 몇 줄이면 확인된다.

→ [「인증서와 CA, 그림으로 이해하기」](/posts/certificates-and-cas/) — 주소창에 자물쇠 하나가 뜨기까지 몇 명의 손을 거치나.
