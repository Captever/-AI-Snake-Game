# 한계 1: AI가 자신의 몸으로 생성된 닫힌 방에 스스로를 가두는 상황

## 해결을 위한 방안: `Flood Fill`
- `Flood Fill`을 이용해 다음 이동의 안전 점수*를 판별, 사용자가 설정한 특정 안전 점수 기준을 충족하는 이동에 대해서만 이동함.

**안전 점수\***란, 해당 지점을 기준으로 얼만큼의 영역 수가 확보되어 있는지를 말함.

### 방안 검토
- 안전한 공간만을 찾아 이동한다고 하더라도 게임 중후반의 경우 비슷한 상황에서의 돌파구를 마련해야 되는 건 매한가지임.
- 게임 진행 정도에 따라 안전 점수 기준을 동적으로 정해야 하며, 기본적으로 랜덤 요소가 많은 'Snake' 게임에서 **Rule-based AI**를 향상시키는 방법에 소요되는 시간이 차선 모델을 사용하는 것보다 비효율적임.

---

# 결론

현재의 **Rule-based AI**를 향상시키는 것보다 **Greedy-Algorithm** 기반의 AI로 전환해 추가 연구를 진행하는 것이 더 현명함.