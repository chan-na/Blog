# DNSSEC은 "없다"를 어떻게 증명하나 — NSEC, 존 워킹, black lies

**상태:** 글감
**만든 날:** 2026-09-01
**예상 slug:** `dnssec-negative-proof`

## 왜 별도 글인가

[「DNS와 네임서버, 그림으로 이해하기」](/posts/dns-and-nameservers/)의 ""없다"는 답도 답이다" 절 끝에
Cloudflare의 black lies를 붙여 뒀다가 덜어냈다. 제대로 설명하려면 DNSSEC의 서명 모델부터 깔아야 하는데,
그 글의 주제(리졸버 대 권한 네임서버, 위임, 캐시)와 결이 다르고 분량도 절 하나로는 감당이 안 된다.

## 다뤄야 할 것

1. **DNSSEC은 왜 미리 서명하나** — 개인키를 온라인에 두지 않으려고 존을 사전 서명한다. 그래서 질의마다 새 답을 만들어 낼 수 없다.
2. **없음을 증명하는 문제** — 존재하지 않는 이름은 무한하다. 그 하나하나에 서명을 미리 만들어 둘 수는 없다.
3. **NSEC** — 대신 이름과 이름 사이의 빈 구간을 서명한다. "A 다음 존재하는 이름은 B, 사이엔 없음."
4. **존 워킹(zone walking)** — NSEC 구간의 양 끝이 실존 이름이라 사슬을 따라가면 존 전체를 열거할 수 있다.
5. **NSEC3** — 이름을 해시해 사슬을 감춘다. 그래도 오프라인 사전 공격으로 상당수 복원 가능(nsec3walker 등).
6. **온라인 서명** — Cloudflare는 질의가 올 때마다 서명한다. 그래서 진짜 이웃 이름을 내줄 이유가 없다.
7. **white lies / black lies** — 최소 범위만 답하는 기법. NSEC3 기반이 white lies, 이름 존재 자체를 감추는 쪽이 black lies.
8. **거짓말인데 검증은 통과한다** — 없는 이름을 NODATA로 답하므로 NXDOMAIN이 사라진다. 서명이 유효해 리졸버는 받아들인다. 부작용도 짚을 것(NXDOMAIN을 기대하는 쪽, 캐시 동작).

곁들일 것: `ad` 플래그(리졸버가 검증에 성공했다는 표시)는 [「도메인 사서 웹페이지 붙이기, 실제로 해봤다」](/posts/buying-a-domain-in-practice/)에서 이미 다뤘다. 이어 붙이면 자연스럽다.

## 확인용 명령

```
$ dig @david.ns.cloudflare.com nope.byeorim.com A        # black lies (NOERROR + NSEC)
$ dig @1.1.1.1 nope-xyz.google.com A                     # 평범한 NXDOMAIN
$ dig @1.1.1.1 byeorim.com A +dnssec | grep "^;; flags:" # ad 플래그
```

## 덜어낸 초안 (한글)

아래는 DNS 글에서 통째로 들어냈던 대목이다. 새 글에 그대로 쓰거나 출발점으로 삼는다.

---

재미있는 예외가 하나 있다. Cloudflare는 없는 이름에도 NXDOMAIN을 주지 않는다.

```
$ dig @david.ns.cloudflare.com nope.byeorim.com A
;; ->>HEADER<<- status: NOERROR         ← NXDOMAIN이 아니다
;; AUTHORITY SECTION:
nope.byeorim.com.  1800  IN  NSEC  \000.nope.byeorim.com. RRSIG NSEC TYPE128
```

"이 이름은 있는데 A 타입만 없다"고 답한다. DNSSEC 때문이다.

DNSSEC에서는 "없다"는 답에도 서명이 붙어야 한다. 그런데 서명은 보통 미리 만들어 두기 때문에, 존재하지 않는 이름 하나하나에 대한 답을 미리 준비해 둘 수는 없다. 없는 이름은 무한히 많다. 그래서 원래 방식은 **이름과 이름 사이의 빈 구간**을 서명해 둔다. "`blog.byeorim.com` 다음에 실제로 존재하는 이름은 `www.byeorim.com`이고 그 사이에는 아무것도 없다"는 식이고, 이것이 **NSEC 레코드**다. `nope.byeorim.com`을 물으면 이 구간을 돌려주는 것으로 "그 이름은 빈 구간 안에 있으니 존재하지 않는다"가 증명된다.

문제는 구간의 양 끝이 **실제로 존재하는 이름**이라는 점이다. 아무 이름이나 물어 NSEC을 하나 받고, 거기 적힌 다음 이름을 또 물으면 그다음 이름이 나온다. 이 사슬을 계속 따라가면 **존에 있는 이름을 전부 훑어낼 수 있다.**

Cloudflare는 서명을 미리 만들어 두지 않고 질의가 올 때마다 즉석에서 만든다. 그래서 진짜 이웃 이름을 알려줄 이유가 없다. 위 출력에서 다음 이름 자리에 적힌 `\000.nope.byeorim.com`은 존재하는 이름이 아니라, 방금 물어본 `nope.byeorim.com` 앞에 값이 0인 바이트 하나짜리 라벨을 덧붙여 만든 것이다. 이름 정렬 순서에서 `nope.byeorim.com` 바로 다음이라 그 사이에는 어떤 이름도 들어갈 수 없다. 가장 좁은 구간만 답으로 준 셈이고, 따라갈 사슬이 애초에 없다. 이 방식의 별명이 **black lies**다.

별명이 그렇게 붙은 것은 이 답이 실제로 거짓말이기 때문이다. `nope.byeorim.com`은 존재하지 않는데도 서버는 "그 이름은 있고 A 타입만 없다"고 답한다. 사실과 다르지만 DNSSEC 서명이 제대로 붙어 있어서 리졸버의 검증은 통과한다. 게다가 실제로 존재하는 이름과 존재하지 않는 이름이 똑같은 모양의 답을 받으므로 밖에서는 둘을 구분할 수 없다. NSEC3로 범위만 좁히던 기존 기법을 white lies라 부른 데 빗대어 Cloudflare가 붙인 이름이다.

---

## 덜어낸 초안 (영문)

There's one entertaining exception. Cloudflare doesn't hand back NXDOMAIN even for names that don't exist.

```
$ dig @david.ns.cloudflare.com nope.byeorim.com A
;; ->>HEADER<<- status: NOERROR         ← not NXDOMAIN
;; AUTHORITY SECTION:
nope.byeorim.com.  1800  IN  NSEC  \000.nope.byeorim.com. RRSIG NSEC TYPE128
```

It answers "this name exists, there's just no A record for it." The reason is DNSSEC.

Under DNSSEC even a "doesn't exist" answer has to carry a signature. But signatures are normally produced ahead of time, and you cannot pre-sign an answer for every name that doesn't exist — there are infinitely many. So the original design signs **the gaps between names** instead: "the next name that really exists after `blog.byeorim.com` is `www.byeorim.com`, and there is nothing in between." That is an **NSEC record**. Ask for `nope.byeorim.com` and handing back that gap proves the name doesn't exist, because it falls inside it.

The catch is that both ends of the gap are **names that really do exist**. Ask for anything, get one NSEC, then ask for the next name it points at, and out comes the name after that. Follow the chain far enough and you can **scrape every name in the zone.**

Cloudflare doesn't pre-sign; it signs on the spot for each query. Which means it has no reason to reveal a real neighbour. The next name in the output above, `\000.nope.byeorim.com`, is not a name that exists — it is `nope.byeorim.com` with a single zero-byte label glued onto the front. In DNS name ordering it comes immediately after `nope.byeorim.com`, so no name can possibly sit between the two. The gap handed back is the narrowest one there is, and there is no chain to follow. The nickname for this is **black lies**.

The nickname fits because the answer really is a lie. `nope.byeorim.com` does not exist, and the server says "that name is there, it just has no A record." Untrue — but properly DNSSEC-signed, so the resolver's validation passes. And because a name that does exist and a name that doesn't get answers of exactly the same shape, an outsider can't tell them apart. Cloudflare coined it playing on white lies, the older technique that only narrowed the range with NSEC3.
