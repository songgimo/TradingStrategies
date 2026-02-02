# tests/test_worker_tasks.py
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src.apps.scheduler.worker_task import collect_stock_data_chunk
from src.backend.domain.reference_data import StockMarketType


@patch("src.backend.application.scheduler_services.CollectMarketDataService.execute", new_callable=AsyncMock)
@patch("src.backend.infrastructure.api.factory.MarketAPIFactory.get_port")
def test_collect_stock_data_chunk_logic(mock_get_port, mock_service_execute):
    # 1. 가짜 의존성 설정
    mock_port = MagicMock()
    mock_get_port.return_value = mock_port

    # 2. 태스크 실행 (bind=True이므로 첫 번째 인자로 mock_self 전달)
    mock_self = MagicMock()
    mock_self.request.id = "tests-task-id"
    codes = ["005930", "000660"]

    collect_stock_data_chunk(mock_self, StockMarketType.KOSPI, codes)

    # 3. 검증: 서비스의 execute가 쪼개진 심볼들로 잘 호출되었는가?
    mock_service_execute.assert_called_once()
    args, _ = mock_service_execute.call_args
    assert len(args[0]) == 2  # Symbol 객체 2개가 전달되었는지 확인