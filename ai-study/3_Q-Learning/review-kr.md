10,000 epoch를 실행해봤지만, 전체 평균이 1.7 정도에 머무는 정도로 그쳤다. 1.7에서 위로 조금 올라갔다가 내려왔다가 편차를 보이는 정도에서 머무는 걸 보면 에포크를 늘려도 크게 변화하진 않을 것이다.
- 개선 방향
  - 타겟과의 절대적인 셀 개수보다 -1 ~ 1 범위의 상대적인 거리 값으로 state에 적용
  - 입실론을 0.9부터 0.01까지 점차 낮아지도록 설정
  - 상태 변화 없는 이동에 대한 페널티 값 대폭 감소: -0.1 -> -0.001

코드 중간 수정 후 '상대값 적용 2천 에포크' 실행한 영상 보면, 중간중간 빙빙 도는 구간이 되게 많다.
- 개선 방향
  - 거리에 대한 피드백 추가
    - 거리 증가: -0.1
    - 거리 감소: +0.1
  - 죽는 수도 제약 없이 설정할 수 있도록 변경 + 4방위 collision 값도 state에 반영
    - 장기적으로 확장성 고려 및 학습 기반의 유연성을 키우기 위해 학습 과정에서 자연스럽게 죽는 수를 배제하도록 설정

-> 10,000 epoch

그닥 높은 점수는 받지 못하고 있음. 가끔 30점대의 점수가 나오긴 하지만 빈도가 매우 낮고, 평균 점수가 15점을 넘지 못하고 있음.
- 개선 방향
  - 입실론 최소 값을 0.1%로 설정해서 어느정도 학습이 된 다음엔 안정적으로 돌파하도록 설정

-> 10,000 epoch

평균 14+-점, 최고 32점. 아직 만족스러운 수치는 아니다.
- 개선 아이디어
  - state에 추가: head의 위치, tail의 위치, neck의 방향, body의 길이
- 변경점
  - 입실론 다시 1%로 돌려놓음

-> 15,000 epoch

평균 0.45점, 최고 2점. state에 너무 많이 우겨 넣은 거 같다.
- 개선 방향
  - state에서 제거: head의 위치, tail의 위치
  - state에 추가: 제일 가까운 벽과의 거리
- 촬영 방식 시도: 죽을 시 페널티 -1 / -5 두 창을 각각 동시에 켜놓고 동시에 녹화 중

-> 10,000 epoch

제일 가까운 벽과의 거리라는 개념은 넣으면 안될 거 같다. 벽 바로 옆에서 벽에 박지 말라고 추가한 건데, 생각해보니 그럴 거면 각 벽과의 거리를 했어야 했다.
- 개선 방향
  - 제일 가까운 벽과의 거리를 각 벽과의 거리로 변경

-> 50,000 epoch 이상

state가 많아져서 그런건지, 최근 100 epoch 평균 2.5 +- 에서 왔다갔다 하고, 최대 점수는 겨우 6점이다. 계속 자기 몸에 부딪혀서 죽는데, 입실론이 발동돼 새로운 탐험을 하다가 죽는 건지 아니면 아직도 자기 몸에 부딪히면 죽는다는 걸 학습을 못 한 건지 참 어이가 없을 정도로 답답하다.
이 글을 작성하는 현재 6만 epoch를 막 넘겼는데, 최근 100 에포크 평균 3.0까지 찍고 다시 내려가는 중이다. 이런 걸 보면 조금씩은 올라가고 있는 거 같긴 한데, 끝을 볼 수 있을지가 의문이다. 슬슬 그만두고 다음 단계로 넘어가야 될 거 같은 느낌이다.

=> DQN으로 전환