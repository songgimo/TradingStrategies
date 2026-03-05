# TradingStrategies (StockTrader) 프로젝트 개요

## 📖 소개
**StockTrader**는 AI 기반의 자동화된 주식/암호화폐 트레이딩 시스템입니다. **도메인 주도 설계(DDD)**와 **헥사고날 아키텍처(포트와 어댑터)**를 활용하여, 데이터베이스, 외부 API, 대형 언어 모델(LLM)과 같은 인프라 구성요소로부터 핵심 트레이딩 로직을 분리했습니다.

이 시스템은 시장 데이터 수집, 금융 뉴스 조회, 기술적 지표를 기반으로 한 종목 필터링, 그리고 최종적으로 LLM을 활용한 매매 전략 생성 과정을 자동화합니다.

---

## 🏗️ 아키텍처 및 프로젝트 구조
`src` 디렉토리 내의 코드는 엄격한 도메인 주도 설계(DDD) 레이아웃을 따릅니다:

- **`src/backend/domain/`**: 외부 프레임워크에 의존하지 않는 핵심 비즈니스 로직을 포함합니다.
  - **Entities & Value Objects (엔티티 및 값 객체)**: `TradeStrategy` 및 `MarketContext`와 같은 핵심 개념을 나타냅니다.
  - **Specifications (`specifications.py`)**: 매매 조건(예: `RsiOverSoldSpec`, `TrendAndPerfectOrderSpec`, `RsiFastCrossOverSlowSpec`)을 정의합니다. 이는 비용이 많이 드는 LLM 분석을 수행하기 전에 주식이 적절한 기술적 셋업을 갖추고 있는지 미리 판단하는 사전 필터 역할을 합니다.
  - **Services (`services.py`)**: SMA, EMA, RSI 등을 계산하기 위한 `IndicatorService`와 같은 순수 도메인 서비스입니다.

- **`src/backend/application/`**: 애플리케이션에 특화된 유스케이스 및 워크플로우 오케스트레이션을 포함합니다.
  - **Ports (`ports/`)**: 인프라 레이어에서 구현해야 할 인터페이스(`LLMOutputPort`, `DatabaseOutputPort`, `MarketOutputPort`)를 정의합니다.
  - **Services (`agent_services.py`)**: 멀티 에이전트 전략 워크플로우를 구성합니다. 후보 종목을 가져오고, 도메인의 기술적 필터링 규칙을 적용한 뒤, 필터링된 종목과 최신 뉴스를 LLM에 전송하여 매매 액션을 생성합니다.

- **`src/backend/infrastructure/`**: 출력 포트(Output Ports)의 구현체입니다.
  - **APIs & Crawlers**: 외부 서비스와의 연동을 위한 모듈.
  - **DB (`db/`)**: 데이터베이스 리포지토리 구현체 (설정에 따라 기본적으로 SQLite 사용).
  - **LLM (`llm/`)**: LangChain/LangGraph 및 외부 LLM과의 연동.
  - **Market Integrations**: **Upbit**(암호화폐) 및 **Open DART**(한국 전자공시시스템) 커넥터.

- **`src/apps/scheduler/`**: 태스크 스케줄링 컴포넌트입니다.
  - Redis/RabbitMQ와 함께 **Celery**를 사용하여 분산된 주기적 스케줄링 태스크(`beat_schedule.py`)를 실행합니다.

- **`src/config/`**: `pydantic-settings`를 사용한 설정 관리. DB, Upbit, DART, Google API, LangSmith를 위한 환경 변수를 로드합니다.

---

## ⚙️ 핵심 워크플로우

애플리케이션은 주로 예약된 Celery 태스크( `beat_schedule.py`에 정의됨)를 통해 작동합니다:

1. **일일 시장 업데이트 (`daily-market-update`)**: 
   - 매일 20:00(오후 8시)에 실행됩니다.
   - 대상 주식/티커에 대한 일마감(EOD) 또는 OHLCV(시가, 고가, 저가, 종가, 거래량) 데이터를 수집합니다.

2. **매일 뉴스 업데이트 (`hourly-news-update`)**:
   - 매일 오전 08:00에 실행됩니다.
   - LLM에 정성적인 컨텍스트를 제공하기 위해 관련 금융 뉴스나 기업 공시를 수집합니다.

3. **일일 전략 생성 (`daily-strategy-generation`)**:
   - 시장 업데이트 직후인 매일 21:00(오후 9시)에 실행됩니다.
   - **1단계:** `StrategyGenerationService`가 모든 후보 기호를 가져옵니다.
   - **2단계:** 최소 150일 이상의 과거 데이터가 필요한 기술적 지표(SMA, EMA, RSI)를 계산합니다.
   - **3단계 (필터링):** 도메인 Specifications(예: "RSI가 과매도 상태이거나 완벽한 상승 추세에 있음")를 사용하여 종목을 필터링합니다. 이 강력한 필터는 수백 개의 종목을 무분별하게 LLM에 보내는 것을 방지합니다.
   - **4단계 (LLM 분석):** 필터링을 통과한 후보들과 최신 뉴스를 LLM에 전달하여 최종 매매 전략을 생성합니다.

---

## 🚀 주요 기술 및 연동
- **언어**: Python
- **아키텍처**: 도메인 주도 설계(DDD), 헥사고날 아키텍처
- **태스크 큐 & 스케줄러**: Celery
- **데이터베이스**: SQLite (환경 변수를 통해 설정 가능)
- **금융 API / 데이터 소스**:
  - **Upbit API**: 암호화폐 시장 데이터 및 주문 실행.
  - **Open DART**: 한국 기업 공시 시스템 분석.
- **AI & LLM 연동**:
  - **LangChain / LangGraph**: 멀티 에이전트 추론 흐름 처리.
  - **LangSmith**: 관측성(Observability) 확보 및 LLM 요청 추적.
