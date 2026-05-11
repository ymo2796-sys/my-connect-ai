# 상담사 에이전트(Counselor Agent) 구현 요약

사용자님의 승인된 계획에 따라 아웃바운드 콜 및 카카오톡 연동 기능을 담당하는 **상담사 에이전트**의 기본 골격을 성공적으로 구현했습니다. 외부 서비스에 대한 확정된 내용이 아직 없으므로, 향후 어떤 API(Vapi, Twilio, 카카오 챗봇 등)를 사용하더라도 쉽게 교체할 수 있도록 모듈화된 플레이스홀더(Placeholder) 형태로 작성했습니다.

## 🌟 구현된 주요 기능

### 1. Counselor Agent Core
- **파일:** `agent/counselor_agent.py`
- 상담사의 페르소나를 관리하고, 고객 리스트를 받아 아웃바운드 전화를 순차적으로 발신하는 캠페인 실행 로직(`execute_outbound_campaign`)을 구현했습니다.
- 카카오톡으로 들어온 메시지의 의도(Intent)를 파악하고, 만약 발주(Order) 내용일 경우 내부 시스템으로 포워딩하는 로직(`handle_incoming_kakao_message`)을 구현했습니다.

### 2. External Integration Skills
- **아웃바운드 콜 스킬 (`agent/skills/outbound_call.py`):**
  - 고객 전화번호와 스크립트를 입력받아 외부 전화 발신 API를 호출하는 껍데기 함수를 만들었습니다. 추후 Vapi나 Twilio 등의 REST API 호출 코드로 대체할 수 있습니다.
- **카카오톡 스킬 (`agent/skills/kakao_integration.py`):**
  - 특정 유저 아이디에게 알림톡/챗봇 메시지를 발송하는 스킬 함수입니다. 향후 카카오 비즈메시지 API 등으로 연결할 수 있습니다.

### 3. 카카오 웹훅 서버 (Webhook Server)
- **파일:** `webhook_server.py`
- 카카오톡 비즈니스 채널이나 챗봇 시스템에서 유저의 메시지를 실시간으로 받기 위한 서버입니다.
- **FastAPI**를 사용하여 간단하게 `/webhook/kakao` POST 엔드포인트를 열어두었으며, 수신된 메시지는 바로 `CounselorAgent`로 전달되도록 파이프라인을 구성했습니다.

## 💡 다음 단계 (Next Steps)
실제 서비스를 붙이기 위해 다음 작업들을 진행할 수 있습니다.

> [!NOTE]
> 1. **실제 API 연동:** Vapi(혹은 Twilio) 및 카카오 비즈메시지의 실제 API Key를 발급받고, `agent/skills` 내부의 `TODO` 부분에 `requests.post(...)` 코드를 작성하여 연동합니다.
> 2. **LLM 프롬프트 적용:** 현재는 단순 키워드("발주", "주문")로 의도를 파악하고 있으나, 랭체인(Langchain) 혹은 OpenAI API를 붙여 실제 사람처럼 대화의 문맥을 이해하고 응답하도록 `counselor_agent.py` 안의 `_parse_intent` 함수를 고도화할 수 있습니다.
> 3. **서버 배포:** `webhook_server.py`를 AWS, Heroku, ngrok 등을 통해 외부에서 접속 가능한 도메인으로 배포한 뒤, 카카오톡 관리자 센터에 해당 웹훅 주소를 등록합니다.

관련 파일들을 한번 살펴보시고, 실제 API Key가 준비되시거나 구체적인 프롬프트 연동이 필요하시면 언제든 말씀해 주세요!
