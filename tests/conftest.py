# tests/conftest.py
import pytest


@pytest.fixture(scope="session")
def celery_config():
    return {
        "task_always_eager": True,  # 비동기 대신 동기식 실행
        "task_eager_propagates": True,
    }


# tests/test_integration.py
def test_news_pipeline_integration(celery_session_app, celery_config):
    from src.apps.scheduler.master_task import master_collect_news

    # 실제 DB 대신 메모리 DB 등을 사용하도록 설정 후 실행
    # master_collect_news -> chord -> analyze_market_news_task 흐름이 한 번에 실행됨
    result = master_collect_news.apply()
    assert result.successful()