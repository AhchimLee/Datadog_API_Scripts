# Datadog API Python Script

## Python 스크립트 사용 방법

1. Org 생성
  - `01_create_org.py` 스크립트 실행 후 org 이름을 입력하여 생성 가능(Org 변수 갯수는 상관 없음)

  1. Org 이름 변경
     - `01-1_change_org_name.py` 스크립트 실행 후 기존 Org 이름, 변경할 Org 이름을 입력하여 생성 가능
       (Org 변수 갯수는 상관 없음)

2. User 추가
  - `02_add_user_to_org.py` 스크립트 실행 후 org 이름 및 email을 입력하여 생성 가능(Email 변수 갯수는 상관 없음)

3. 기본 Monitor 추가
  - `03_default_monitors_to_org.py` 스크립트 실행 후 org 이름을 입력 후 Cloud 환경 선택하여 생성 가능

4. 기본 Dashboard 추가
  - `04_default_dashboards_to_org.py` 스크립트 실행 후 org 이름을 입력 후 Cloud 환경 선택하여 생성 가능

5. Slack Integration 추가 및 Slack 채널 추가 (Webhook URL로 추가 가능)
   - `05_create_slack_intergration_to_org.py`
   - 고객사에서 받은 Slack Webhook URL 혹은 Slack에 직접 앱 연동한 URL로 ORG에 Slack 연동 가능
   - 지원 가능 Slack App List
     - Datadog (Legacy)
     - Incoming Webhooks

   1. 기존 Slack Integration에 Slack 채널 추가
      - `05-1_add_slack_channel_to_slack_integration.py`
      - 기존에 연동된 slack integration에 채널 추가 가능
        (채널별로 App을 연동하는 Webhook Integration 설치했을 시 1개 인테그레이션 당 1개 채널만 연동 가능.)

6. 전체 Monitor 수신 변경
  - `06_add_or_remove_a_notification_in_all_monitors.py` 스크립트 실행
  - 전체 모니터 대상으로 알람 수신 추가/삭제/변경 가능
  - email, slack, webhook 에 대한 전체 모니터 수신 추가/삭제/변경 수행

  1. 전체 Monitor 말머리 추가
    - `06-1_add_prefix_to_name_in_all_monitors.py` 스크립트 실행
    - 전체 모니터 대상으로 이름 말머리 추가 가능 (ex. [SKTELINK] ~~~)


## 사용 시 주의사항
- Datadog Org는 생성 후 임의 삭제가 불가능합니다.(DataDog Support에 삭제요청 필요) 생성 시 신중하게 이름 기입 부탁드립니다.
- Datadog 유저 추가 시 disable은 가능하지만 삭제는 불가능하므로, 유저 원복은 담당자에 연락 부탁드립니다. (담당자: SRE 8팀_SK그룹파트 이아침)

## 향후 Release
