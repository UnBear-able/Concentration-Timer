history_open = False # 기록 창 열린 상태인지 여부, 열리면 Ture
editor_open = False # 타이머 수정창 열린 상태인지 채크하는 변수

idle_state = False
working_state = False

track_mode = None
idle_threshold_sec = None

window_list = []  # 현재 열린 창 이름 리스트 (LoopManiger → main_gui 공유용)