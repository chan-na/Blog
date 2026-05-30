---
title: "LLM Agent가 잘 쓰는 MCP Tool 설계 원칙"
date: 2026-05-30T10:00:00+09:00
draft: false
slug: "mcp-tool-design-principles"
translationKey: "mcp-tool-design-principles"
categories: ["개발"]
tags: ["mcp", "llm", "agent", "tool-design"]
summary: "LLM이 명확히 선택하고, 안전하게 실행하고, 결과를 검증하고, 실패 시 복구할 수 있는 MCP tool을 설계하는 원칙을 정리했다."
---

MCP tool을 설계할 때 가장 흔한 실수는 두 극단 중 하나로 빠지는 것이다.
백엔드 API를 그대로 노출하거나, 반대로 `do_anything` 하나로 뭉뚱그리거나.

이 글은 그 사이의 좋은 지점 — **LLM이 명확히 선택하고, 안전하게 실행하고, 적은 context로 결과를 검증하며, 실패 시 복구할 수 있는 작업 단위** — 를 어떻게 잡는지 정리한 것이다. 주요 근거는 Anthropic, MCP 공식 스펙, OpenAI function calling 문서에서 가져왔고 출처는 맨 아래에 모았다.

---

## 1. 두 극단을 피한다

**나쁜 설계 A — 백엔드 API를 그대로 노출**

```text
create_node, set_color, set_font, move_node, resize_node, set_padding,
set_gap, delete_node, export_svg, upload_asset, publish_page, ...
```

LLM은 매 요청마다 어떤 tool을 어떤 순서로 호출할지 추론해야 한다. tool 정의와 중간 결과도 context를 갉아먹는다.

**나쁜 설계 B — `do_anything` 하나**

```json
{ "tool": "do_anything", "instruction": "Make the page better" }
```

너무 추상적이라 검증, 권한 분리, destructive action 감지, 회귀 테스트가 전부 어렵다.

**좋은 설계 — 작업 단위의 중간 지점**

```text
풍부한 read tool
+ 소수의 고표현력 write tool
+ 별도의 validate / preview / diff tool
+ destructive operation에 대한 서버 측 안전장치
+ checkpoint / rollback
+ eval로 검증되는 description과 schema
```

Anthropic도 "많은 tool이 항상 더 좋은 건 아니며, 과제에 맞는 소수의 고영향 tool부터 만들라"고 권고한다. 예를 들어 Login Card를 만드는 tool 하나가 내부적으로 `create_frame`, `create_text`, `set_padding`, `set_fill`을 호출할 수 있다 — agent는 그 한 번만 부르면 된다. tool 하나가 내부적으로 여러 API 호출을 묶을 수 있다는 점이 핵심이다.

---

## 2. API 단위가 아니라 작업 단위로 설계한다

> "백엔드에 함수가 80개 있으니 tool도 80개로 만들자"

개발자에게는 자연스럽지만 agent에게는 부담이다. 대신 이렇게 묻는다.

> "사용자 요청을 처리할 때 LLM이 자연스럽게 구분해야 하는 행동 단위는 무엇인가?"

디자인 툴 사용자는 보통 "로그인 화면 만들어줘", "이 섹션을 pricing card로 바꿔줘"처럼 요청한다. 내부적으로는 frame 생성, text 삽입, padding 설정, fill 변경 등 수십 개 조작이 필요해도 agent 관점에서는 "디자인 변경"이라는 하나의 의도다. 이 경우 저수준 API를 다 노출하기보다 `batch_design` 같은 작업 단위 tool이 자연스럽다.

단, 모든 도메인에 batch가 답은 아니다.

| 도메인 | 권장 형태 | 이유 |
|---|---|---|
| 디자인·문서·IDE 편집기 | 고표현력 batch write + 풍부한 read/preview | transaction, rollback, diff가 중요 |
| 검색·조회 | `search`, `get_by_id` 같은 좁은 tool | 작업이 독립적이고 transaction 필요성 낮음 |
| 메시징·외부 전송 | `draft_message` / `send_message` 분리 | preview·confirmation 경계가 중요 |
| 대규모 toolset | direct tool + `search_tools` 혼합 | 모든 정의를 항상 context에 넣지 않으려고 |

tool 개수에 대한 숫자(편집기형이면 8~15개 등)는 유용한 starting point지만 절대 규칙이 아니다. **사람이 봐도 선택 경계가 명확한 최소 집합**으로 두고 eval로 재조정하는 게 맞다.

---

## 3. 모든 것을 Tool로 만들지 않는다 — Resource, Prompt와의 구분

MCP는 tool 말고도 두 가지 primitive를 더 제공한다. 무엇을 tool로 노출할지 정하기 전에, 그게 애초에 tool이어야 하는지부터 따진다.

- **Tool** — 모델이 호출해 *행동*하거나 계산하는 것. side effect가 있거나 결과가 인자에 따라 달라진다. `create_design`, `search_document`, `batch_design`.
- **Resource** — 모델·클라이언트가 *읽는* context 데이터. 비교적 안정적이고, 호출보다 참조에 가깝다. `design_tokens`, `style_guide`, `project_settings`.
- **Prompt** — 사용자가 명시적으로 고르는 재사용 워크플로 템플릿(슬래시 커맨드 등).

구분 기준은 단순하다. **행동·계산이면 tool, 그냥 읽는 참조 데이터면 resource다.** style guide나 design token처럼 거의 안 변하고 여러 작업에서 참조만 되는 데이터를 `get_style_guide` tool로 만들면, agent가 매번 호출 여부를 추론해야 하고 그 결과가 context를 차지한다. resource로 두면 클라이언트가 필요할 때 모델에 붙여줄 수 있다.

---

## 4. Read / Write / Validate / Export를 분리한다

이게 MCP 설계에서 가장 중요한 원칙 중 하나다.

| 분류 | Tool 예시 | 자동 실행 | 주의점 |
|---|---|---|---|
| Read | `get_state`, `search_nodes`, `get_screenshot` | 높음 | 응답 크기 제한, pagination |
| Write | `batch_design`, `set_variables` | 낮음~중간 | dry-run, diff, idempotency |
| Validate / Preview | `validate_design`, `preview_diff` | 높음 | suggested fix를 구조화 |
| Safety / Recovery | `create_checkpoint`, `restore_checkpoint` | 중간 | explicit checkpoint ID |
| Export / External | `export_nodes`, `publish`, `send_message` | 낮음 | confirmation, side effect 표시 |

분리하면:

- read-only tool은 agent가 자유롭게 상태를 파악한다.
- confirmation·dry-run·audit log는 write tool에만 집중한다.
- destructive action을 schema와 서버 정책으로 감시하기 쉽다.
- validation/preview가 독립되어 self-correction loop가 가능하다.

---

## 5. Write는 batch로 묶되 `do_anything`이 되지 않게 한다

쓰기 tool은 저수준 API를 쪼개기보다 batch로 묶는 편이 좋은 경우가 많다. 단, **batch 내부 operation은 반드시 구조화**해야 한다.

```json
{
  "mode": "dry_run",
  "idempotency_key": "req_2026_05_28_login_card_01",
  "operations": [
    {
      "op_id": "op_1",
      "op": "insert",
      "risk": "safe",
      "parent_id": "node_7f3a",
      "node": { "type": "frame", "name": "Login Card" }
    },
    {
      "op_id": "op_2",
      "op": "delete",
      "risk": "destructive",
      "target_id": "node_8ab2"
    }
  ]
}
```

좋은 batch write tool의 조건:

- `op`는 enum이다 (`insert`, `update`, `move`, `replace`, `delete` ...).
- 각 operation은 `op_id`를 가지고, 뒤 operation이 앞 결과를 참조할 수 있다.
- target은 서버가 반환한 안정적 `id`/`ref`를 쓴다.
- `mode`로 `dry_run`과 `apply`를 분리한다.
- `idempotency_key`로 retry 중 중복 적용을 막는다.
- partial failure를 operation 단위로 보고한다.
- operation별 `risk`(`safe` / `caution` / `destructive` / `external_side_effect`)를 명시하고, 위험한 operation은 서버가 dry-run·confirmation을 강제한다.

여기서 중요한 건 **safety를 annotations에만 맡기지 않는 것**이다. MCP 공식 스펙도 annotations는 trusted server에서 온 게 아니면 untrusted로 보라고 한다. 권한과 confirmation은 서버 정책에서 강제해야 한다.

---

## 6. Dry-run / Preview / Diff는 1급 기능이다

쓰기 tool에는 dry-run/preview를 기본으로 둔다. 그러면 자연스러운 흐름이 나온다.

```text
get_state → snapshot_layout → create_checkpoint
→ batch_design(dry_run) → preview_diff
→ (필요 시 사용자 confirmation)
→ batch_design(apply) → get_screenshot → validate
→ issue 있으면 batch_design으로 수정
```

dry-run 응답은 agent가 다음 행동을 결정할 수 있게 만든다.

```json
{
  "status": "ok",
  "mode": "dry_run",
  "summary": "3 nodes will be inserted, 1 node will be replaced.",
  "risk_summary": { "safe": 3, "caution": 1, "destructive": 0 },
  "requires_confirmation": false,
  "diff_ref": "diff_41c9",
  "actions_available": [
    { "tool": "preview_diff", "arguments": { "diff_ref": "diff_41c9" } },
    { "tool": "batch_design", "arguments": { "mode": "apply", "diff_ref": "diff_41c9" } }
  ]
}
```

`delete`, `publish`, `send`, `overwrite` 같은 destructive·external action은 dry-run 강제 + checkpoint 자동 생성 + confirmation + idempotency까지 별도 경계를 둔다.

---

## 7. 이름·schema·response가 agent의 행동을 결정한다

**이름과 description은 선택 경계다.** LLM은 이름과 description을 보고 tool을 고른다. 동의어 tool은 헷갈림을 부른다.

```text
나쁨: get_nodes, fetch_nodes, read_nodes, load_nodes
좋음: canvas_get_state, canvas_search_nodes, canvas_batch_design
```

read/write/export/validate 성격이 이름에서 드러나게 하고, 여러 서버를 모을 땐 namespace를 붙인다(`figma_search_nodes`). description에는 ① 하는 일 한 문장 ② 언제 쓰는지 ③ **언제 쓰면 안 되는지** ④ 위험 action의 dry-run 규칙 ⑤ input 예시를 담는다.

**input schema는 strict하고 평평하게** 시작한다. `enum`을 적극 쓰고, `additionalProperties: false`를 기본값으로, 모호한 이름(`user`보다 `user_id`)을 피한다. LLM은 schema가 느슨하면 정의에 없는 필드를 만들어내는 경향이 있어서, `additionalProperties: false`는 hallucinated field를 초기에 차단하는 효과가 있다. 깊은 nested object는 신뢰성을 떨어뜨리니 의심스러우면 평평한 쪽을 택한다.

**response는 고신호·저잡음**이어야 한다. pagination, field selection, `view`/`response_format` enum으로 token을 통제한다.

```text
concise   : 최종 판단에 필요한 핵심만
standard  : 다음 tool 호출에 필요한 ID, label, path 포함
detailed  : debug/audit용 full structure
```

**identifier는 stable ID + human label 이중 모델**로 둔다. write target은 반드시 서버가 반환한 `id`/`ref`를 쓰게 해서 agent가 ID를 hallucinate하지 못하게 하고, 동시에 `name`/`path`도 줘서 사람이 읽을 수 있게 한다.

```json
{
  "id": "node_7f3a9c",
  "name": "Primary Login Button",
  "path": "Page/Home/Login Card/Primary Login Button",
  "reference_hint": "Use id for write targets. Use path/name for reasoning."
}
```

---

## 8. Error는 복구 가능한 행동을 가르쳐야 한다

`{ "error": "Invalid request" }` 같은 에러로는 agent가 아무것도 못 한다. 좋은 에러는 다음에 뭘 해야 할지 알려준다.

```json
{
  "status": "error",
  "error_code": "INVALID_TARGET",
  "message": "Target node 'node_123' does not exist in the current document.",
  "field_path": "operations[2].target.id",
  "recoverable": true,
  "suggestion": {
    "next_tool": "canvas_get_state",
    "reason": "Retrieve current node IDs, then retry with a valid target id."
  },
  "partial_success": {
    "succeeded": ["op_0", "op_1"],
    "failed": [{ "op_id": "op_2", "reason": "INVALID_TARGET" }]
  }
}
```

error code는 enum, 문제 field path 제공, recoverable 여부 명시, retry할 tool 제안, batch는 partial success를 operation 단위로 분리 — 이게 효율적인 retry를 만든다.

같은 맥락에서 상태도 hidden state가 아니라 **명시적 handle**로 노출한다. `undo_last_action`처럼 agent가 호출 이력을 기억한다고 가정하는 대신, checkpoint ID, cursor, diff ref, document version을 응답에 담는다.

---

## 9. 대규모 toolset엔 progressive disclosure를 쓴다

모든 tool 정의를 항상 context에 넣으면 비용·지연·혼동이 커진다. 핵심 tool + `search_tools`만 노출하고, agent가 과제에 맞는 tool을 검색해 필요한 schema만 동적으로 로드하게 한다.

```text
search_tools(query, capability?, risk?, detail_level)
get_tool_schema(tool_name)
```

대량 데이터 조작·반복 루프·multi-step orchestration이 많으면, 모든 중간 결과를 모델에 흘리지 말고 sandboxed code execution 환경에서 필터링한 뒤 작은 결과만 반환한다. 10,000행 스프레드시트 필터링, 여러 SaaS 데이터 집계, 개인정보가 모델 context에 들어가면 안 되는 작업 등이 좋은 후보다. 단 sandboxing·resource limit·audit이 전제다.

---

## 10. Evaluation은 설계의 일부다

설계가 좋아 *보이는* 것보다 실제 agent 호출에서 잘 작동하는지가 중요하다. tool prototype을 만들면 real-world task 30~100개로 eval을 돌리고 raw transcript를 직접 본다.

eval set에는 happy path만이 아니라 multi-step, ambiguous("이걸 좀 예쁘게 바꿔줘"), destructive("pricing section 삭제해줘"), error recovery(stale ID, invalid schema), large response, external side effect를 모두 넣는다. 지표는 task success rate, tool selection accuracy, recovery rate, **destructive containment**(의도치 않은 파괴적 action이 없었는가), token efficiency, schema error rate 등을 본다.

이 지표들은 감으로 보는 게 아니라 시나리오마다 라벨을 붙여 측정한다. tool selection accuracy는 각 시나리오에 "기대 tool"을 정해두고 첫(또는 핵심) 호출이 그것과 일치한 비율로, destructive containment는 destructive/external 시나리오에서 confirmation·dry-run 없이 파괴적 action이 실행된 케이스 수로 잰다. 둘 다 자동 채점이 가능해서 regression에 그대로 넣을 수 있다.

transcript에서 자주 보이는 실패 패턴과 처방:

| 실패 패턴 | 처방 |
|---|---|
| 비슷한 tool 사이를 오감 | namespace, "Do NOT use", examples 추가 |
| 같은 read tool 반복 호출 | response에 IDs, `actions_available`, summary 추가 |
| dry-run 없이 delete 시도 | 서버에서 dry-run 강제 |
| hallucinated ID 사용 | `id`+`path` 제공, write엔 ID만 허용 |
| 긴 응답을 못 읽음 | fields/view/limit/cursor 추가 |
| argument 누락 | schema flattening, required, examples |

상태를 바꾸는 agent는 같은 시작점에서도 다른 유효 경로를 택할 수 있으니, "정답 trajectory"를 과하게 고정하기보다 **최종 상태와 safety invariant**를 평가하는 게 맞다. tool description 변경도 코드 변경처럼 regression test를 돌린다.

---

## 한 줄 요약

> MCP tool은 "많을수록 좋은 것"도 "적을수록 좋은 것"도 아니다.
> 핵심은 agent가 **명확히 선택하고, 안전하게 실행하고, 적은 context로 검증하며, 실패 시 복구할 수 있는 작업 단위**를 만드는 것이다.

---

## 참고 출처

- [Anthropic — Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Anthropic — Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Anthropic — Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Anthropic — How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [MCP 공식 — Tools spec](https://modelcontextprotocol.io/specification/draft/server/tools)
- [OpenAI — Function calling guide](https://platform.openai.com/docs/guides/function-calling)
- [OpenAI — o3/o4-mini Function Calling Guide](https://developers.openai.com/cookbook/examples/o-series/o3o4-mini_prompting_guide)
