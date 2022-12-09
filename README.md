# VoiceConverterWeb2022
# AVOTAR: 가상공간에서의 페르소나를 위한 목소리 커스터마이징 시스템

맞춤형 목소리 서비스 AVOTAR(아보타)는 부자연스러운 기계음으로 합성한 음성이 아니라 실제 자신의 목소리를 개선하여 변조된 음성을 제공하는 시스템입니다. 이 프로젝트는 이후 2023 CHI Conference late breaking session에 논문 투고할 계획입니다.

### **개발 환경**

시스템 구현에 파이썬 라이브러리 praat-parselmouth를 참조하였고, 파이썬에서는 다음 코드로 다운받을 수 있습니다:

```python
pip install praat-parselmouth
```

목소리 변조 시스템에 대한 코드는 [링크](https://github.com/hyeonJeongByeon/VoiceConverterWeb2022)에서 확인할 수 있습니다. 웹 구현은 django와 Amazon S3 bucket을 활용하였습니다.

### **********************************목소리 변조 모델 구조**********************************

![Untitled](AVOTAR%20%E1%84%80%E1%85%A1%E1%84%89%E1%85%A1%E1%86%BC%E1%84%80%E1%85%A9%E1%86%BC%E1%84%80%E1%85%A1%E1%86%AB%E1%84%8B%E1%85%A6%E1%84%89%E1%85%A5%E1%84%8B%E1%85%B4%20%E1%84%91%E1%85%A6%E1%84%85%E1%85%B3%E1%84%89%E1%85%A9%E1%84%82%E1%85%A1%E1%84%85%E1%85%B3%E1%86%AF%20%E1%84%8B%E1%85%B1%E1%84%92%E1%85%A1%E1%86%AB%20%E1%84%86%E1%85%A9%E1%86%A8%E1%84%89%E1%85%A9%E1%84%85%E1%85%B5%20e5525cd5882545978101010dd62d3813/Untitled.png)

AVOTAR는 타겟 목소리와 원본 목소리를 입력값으로 사용합니다. 사용자가 반영도 수치를 설정한 후 원본 목소리를 타겟 목소리처럼 조절하고, pitch(목소리 높낮이), formant(주파수가 울리는 정도), duration(빠르기)를 조절하여 결과 목소리를 만들어냅니다.

### **********************************Web 데모**********************************

목소리 변조에 대한 Web 데모는 [링크](http://ec2-3-39-23-78.ap-northeast-2.compute.amazonaws.com/case4/)에서 확인할 수 있습니다.

([http://ec2-3-39-23-78.ap-northeast-2.compute.amazonaws.com/case4/](http://ec2-3-39-23-78.ap-northeast-2.compute.amazonaws.com/case4/))

![Untitled](AVOTAR%20%E1%84%80%E1%85%A1%E1%84%89%E1%85%A1%E1%86%BC%E1%84%80%E1%85%A9%E1%86%BC%E1%84%80%E1%85%A1%E1%86%AB%E1%84%8B%E1%85%A6%E1%84%89%E1%85%A5%E1%84%8B%E1%85%B4%20%E1%84%91%E1%85%A6%E1%84%85%E1%85%B3%E1%84%89%E1%85%A9%E1%84%82%E1%85%A1%E1%84%85%E1%85%B3%E1%86%AF%20%E1%84%8B%E1%85%B1%E1%84%92%E1%85%A1%E1%86%AB%20%E1%84%86%E1%85%A9%E1%86%A8%E1%84%89%E1%85%A9%E1%84%85%E1%85%B5%20e5525cd5882545978101010dd62d3813/Untitled%201.png)

![Untitled](AVOTAR%20%E1%84%80%E1%85%A1%E1%84%89%E1%85%A1%E1%86%BC%E1%84%80%E1%85%A9%E1%86%BC%E1%84%80%E1%85%A1%E1%86%AB%E1%84%8B%E1%85%A6%E1%84%89%E1%85%A5%E1%84%8B%E1%85%B4%20%E1%84%91%E1%85%A6%E1%84%85%E1%85%B3%E1%84%89%E1%85%A9%E1%84%82%E1%85%A1%E1%84%85%E1%85%B3%E1%86%AF%20%E1%84%8B%E1%85%B1%E1%84%92%E1%85%A1%E1%86%AB%20%E1%84%86%E1%85%A9%E1%86%A8%E1%84%89%E1%85%A9%E1%84%85%E1%85%B5%20e5525cd5882545978101010dd62d3813/Untitled%202.png)

### **AVOTAR 사용법**

위의 웹 사이트에 접속하면 AVOTAR를 직접 체험해볼 수 있습니다. 웹 사이트를 사용하기 전, 본인의 목소리를 녹음한 음성 파일과 닮고 싶은 사람의 목소리가 담긴 음성 파일을 준비해주세요. 두 음성 파일 모두 5초 분량의 짧은 데이터여도 웹 사이트가 동작하는 데에는 문제가 전혀 없습니다. 만약, 닮고 싶은 사람의 목소리가 없다면 해당 칸은 비워두셔도 좋습니다.

1. 먼저, ‘원본 목소리’ 칸에는 자신의 목소리를 녹음한 음성 파일을 업로드 합니다.
2. 그 후, 닮고 싶은 목소리가 있다면, 그 사람의 목소리를 녹음한 음성 파일을 업로드 합니다.
3. ‘반영도’ 속성을 조절한 후 작은 초기화 버튼을 누릅니다. 여기서 ‘반영도’란, 자신의 목소리를 닮고 싶은 목소리와 얼만큼 닮게 만들고 싶은지를 조절하는 속성에 해당합니다. 슬라이더를 오른쪽으로 움직일수록 닮고 싶은 목소리에 가까운 목소리를 만들어냅니다.
4. 만약 닮고 싶은 목소리가 없다면 ‘닮고 싶은 목소리’ 칸을 무시하고 ‘목소리 속성 조절’ 칸의 큰 초기화 버튼을 누릅니다.
5. 작은 초기화 버튼을 누르거나 큰 초기화 버튼을 누르고 나면, ‘목소리 속성 조절’ 칸의 슬라이더들이 자동으로 조정됨과 동시에 ‘커스터마이징 된 음성’ 칸에 반영도만을 조절한 음성 파일이 생성됩니다.
6. 이 목소리를 들어본 후 세부적인 커스터마이징이 필요하다고 느끼는 경우, ‘목소리 속성 조절’ 칸의 슬라이더를 움직여 세밀한 속성들을 커스터마이징 합니다. ‘음의 높낮이’ 속성은 목소리의 높고 낮음을 조절하는 속성입니다. ‘f1’, ‘f2’, ‘f3’, ‘f4’는 formant (공명 주파수) 속성을 주파수 구간별로 나눈 것으로, 주파수가 높으면 목소리가 높은 주파수에서 공명하여 날카로운 목소리를 만들어내고 주파수가 낮으면 목소리가 낮은 주파수에서 공명하여 마치 동굴에서 말하듯이 울리는 목소리를 만들어냅니다. ‘느려짐’ 속성은 말하는 속도를 조절합니다. 모든 목소리 입력값에 대해 조절하기 전까지는 ‘느려짐’ 속성의 값이 1로 설정되어 있습니다. ‘느려짐’ 속성을 1보다 크게 조절하면 그만큼 말하는 소리가 느려집니다. 예를 들어, ‘느려짐’을 2로 설정한 경우, 초기의 목소리에 비해 2배 느려진 목소리가 생성됩니다.
