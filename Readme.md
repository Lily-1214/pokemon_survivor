# Pokemon Survivor
Pokemon Survivor는 Vampire Survivors와 같은 뱀서라이크 게임입니다.
![image](images/gameplay1.png)

## 뱀서라이크 게임이란?
로그라이크 장르의 특징을 가지고 있는 탑뷰 또는 쿼터뷰 시점의 게임으로서
슈팅 요소를 포함한 여러 무기를 조합해 적을 쓰러트려야 합니다. (예 : Vampire Survivors)
![image](images/vampire_survivors.png)

## 시작하기

### pip install

```python
pip install pygame
```
![image](images/.png)
## 프로그램 시작
필요한 모듈과 위 파일들을 모두 다운로드 받았다면
pokemon_survivor_main.py 파일을 IDLE로 열어 F5를 눌러 실행합니다

## 게임 설명
Pokemon Survivor는 가여운 파이리가 아주 흉악한 캐터피와 피죤투들이 몰려오는 것을 막는 게임입니다.
WASD로 파이리를 움직일 수 있으며, 파이리의 모든 공격은 가장 가까운 대상을 향해 발사합니다.
3분이 지나면 게임에서 승리한것으로 간주합니다.
![image](images/gameplay2.png)

## 화면 설명

### 세이브 슬롯 화면
비어있는 슬롯을 선택해 새로 게임을 플레이할 수 있습니다.
데이터가 남아있는 슬롯을 선택해 이어서 게임을 플레이할 수 있습니다.
json 파일을 삭제해 세이브파일을 삭제할 수 있습니다.
![image](images/save_slot_screen.png)

### 메인 화면
시작 버튼을 눌러 게임을 시작합니다.
강화 버튼을 눌러 초기 능력을 강화합니다
저장 버튼을 눌러 현재 상황을 세이브 슬롯에 저장합니다.
종료 버튼을 눌러 세이브 슬롯 화면으로 돌아갑니다.
![image](images/main_screen.png)

#### 메인-강화 화면
게임이 종료되면 스코어의 10%에 해당하는 골드를 획득합니다.
강화를 눌러 골드를 소모하고 능력을 강화할 수 있습니다.
![image](images/upgrade_screen.png)

### 게임 화면
상단 좌측엔 점수, 중앙엔 경과 시간이 나타납니다.
초록색/빨간색으로 현재/최대체력을, 노란색/연갈색으로 경험치 현황을 나타나며 위에는 레벨이 표시됩니다.
![image](images/score_time_health_exp.png)

#### 게임-강화 선택 화면
파이리의 경험치가 가득 차면 레벨업을 합니다.
아쉽게도 리자드나 리자몽으로 진화하진 않습니다.
//리자드 리자몽 이미지
랜덤으로 주어지는 3개의 선택지 중 하나를 30초 내로 골라 이번 게임동안 능력을 강화합니다.
![image](images/upgrade_select_screen.png)

## 핵심 코드 및 기능 설명

### 1.파이리의 이동과 공격
유저가 마지막으로 누른 키보드 A/D에 따라 파이리가 왼쪽/오른쪽을 바라봅니다.
//파이리 좌우반전 관련 코드
불꽃세례(Ember)는 가장 가까운 적의 방향으로 부채꼴 형태의 공격을 합니다.
![image](images/ember_implementation.png)
화염구(Fireball)는 첫번째로, 두번재로... 가까운 적의 방향으로 화면 가장자리에서 사라지는 투사체를 발사합니다.
투사체의 개수는 투사체 개수 증가 레벨에 따라 증가합니다.
![image](images/fireball_implementation.png)
//가장 가까운 적 추적 코드

### 2.적의 이동과 공격
적은 맵 좌우 가장자리에서 랜덤하게 스폰되며, 스폰되는 순간부터 파이리를 위협하러 다가옵니다.
//적 스폰 및 플레이어 추적 코드
30초마다 체력이 증가되며, 1분 30초에는 캐터피가 피죤투로 대체되며 배경이 바뀝니다.
//체력 증가 및 배경, 적 이미지 변경 코드
파이리에게 닿으면 데미지를 입히고 사라집니다.
//데미지 입히는 코드

### 3.파이리의 레벨업과 능력 강화
파이리는 1레벨부터 시작해서 30레벨까지 레벨업을 할 수 있으며, 간단한 수식으로 경험치 테이블을 생성했습니다.
//레벨업 테이블 및 경험치 획득 코드
파이리가 레벨업하면 8개의 능력치중 랜덤으로 나오는 3개의 선택지에서 하나를 고를 수 있습니다.
//강화 선택 화면 출력 코드
현재 능력 강화 상태는 좌측 하단에 아이콘으로 표시됩니다.
//현재 능력 상태 출력 코드

## 개발환경 및 실행환경
Python 3.12(Window 10), Python IDLE 사용
