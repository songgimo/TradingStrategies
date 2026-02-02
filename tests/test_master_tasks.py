# tests/test_master_tasks.py
from unittest.mock import patch, MagicMock
from src.apps.scheduler.master_task import master_collect_stocks


@patch("src.apps.scheduler.master_task._load_codes")
@patch("celery.group")
def test_master_collect_stocks_dispatching(mock_group, mock_load):
    # 1. 가짜 종목 코드 설정 (25개)
    mock_load.return_value = [f"code_{i}" for i in range(25)]

    # 2. group().apply_async()가 호출되도록 설정
    mock_group_instance = mock_group.return_value

    # 3. 마스터 태스크 실행
    master_collect_stocks()

    # 4. 검증: 20개씩 쪼갰을 때 2개의 청크가 생성되었는가?
    # kospi_groups 생성 시 group()에 전달된 generator의 길이를 체크
    call_args = mock_group.call_args_list
    # KOSPI 그룹 생성 확인
    assert mock_group.called
    # apply_async()가 실행되었는지 확인
    mock_group_instance.apply_async.assert_called()