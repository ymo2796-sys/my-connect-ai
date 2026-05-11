# 상담사 에이전트(Counselor Agent) 추가 구현 계획

아웃바운드 콜을 통한 고객 안내 및 카카오톡 수신 메시지/발주 내용을 전달하는 새로운 상담사 에이전트(Counselor Agent)를 시스템에 추가하기 위한 설계입니다.

## ⚠️ User Review Required

본 기능은 외부 API(전화 발신, 카카오톡 채널 연동)에 크게 의존합니다. 따라서 어떤 통신/솔루션 업체를 사용할지에 대한 결정이 필요합니다. 아래 **Open Questions**를 확인하시고 피드백을 부탁드립니다.

## ❓ Open Questions

1. **아웃바운드 콜 솔루션:** 현재 생각하고 계신 전화 발신 API 서비스가 있으신가요? (예: Vapi, Bland AI, Twilio, 알리고, 자체 구축 시스템 등)
2. **카카오톡 연동 방식:** 카카오톡 챗봇/알림톡 API를 직접 연동하여 웹훅(Webhook) 서버를 띄워 수신할까요? 아니면 이미 구성되어 있는 n8n/Zapier 등의 자동화 툴을 통해 데이터를 전달받을까요?
3. **데이터 전달 목적지:** 상담사가 수신한 고객 메시지나 발주 내용은 최종적으로 어디로 전달(알림)되어야 하나요? (예: 담당자 Slack, 이메일, Notion DB, 구글 시트 등)

## 🛠 Proposed Changes

### Counselor Agent (Core)
상담사 에이전트의 메인 로직과 상태 관리를 담당하는 모듈을 추가합니다.

#### [NEW] `agent/counselor_agent.py`
- 에이전트의 페르소나 및 프롬프트 관리
- 고객 리스트를 받아 아웃바운드 콜 캠페인 실행 지시
- 수신된 메시지와 발주 데이터를 파싱하여 최종 목적지로 전달하는 라우팅 로직

---

### Skills Layer (External Integrations)
상담사 에이전트가 외부 세계와 소통하기 위한 구체적인 스킬 모듈입니다.

#### [NEW] `agent/skills/outbound_call.py`
- 선택된 음성/전화 API(예: Vapi, Twilio 등)를 호출하여 타겟 고객에게 전화를 거는 스크립트
- 통화 성공 여부 및 통화 로그 기록

#### [NEW] `agent/skills/kakao_integration.py`
- 카카오톡 API (비즈메시지 / 카카오 챗봇 웹훅) 연동 처리
- 고객이 카카오톡으로 보낸 발주 내용이나 메시지 수신 및 파싱

---

### API Webhook Server (Optional)
카카오톡 등 외부로부터 실시간 응답을 받기 위해 필요시 간단한 웹훅 서버를 구성합니다. (FastAPI 활용 추천)

#### [NEW] `webhook_server.py`
- `/webhook/kakao` 엔드포인트를 노출하여 실시간 고객 메시지 수신
- 수신된 데이터를 `counselor_agent`에게 전달

## ✅ Verification Plan

### Automated Tests
- Mock API를 활용하여 아웃바운드 콜 요청이 올바른 포맷으로 전송되는지 테스트
- 가상의 카카오톡 웹훅 페이로드를 생성하여 발주 내용이 정확히 파싱되고 전달되는지 유닛 테스트 실행

### Manual Verification
- 실제 테스트용 번호로 아웃바운드 콜을 발생시켜 통화 품질 및 스크립트 연결 확인
- 샌드박스 또는 테스트용 카카오 채널을 통해 발주 메시지를 전송하고 정상 처리되는지 확인
