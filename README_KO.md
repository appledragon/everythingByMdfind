# Everything by mdfind
<img alt="everything" src="https://github.com/user-attachments/assets/84dc4f48-201f-40f5-8b2b-9f8f6070a9b2" />

macOS 스포트라이트 엔진 기반의 초고속 파일 검색 도구

## 주요 기능

* **즉각 검색:** 스포트라이트 인덱스 활용, 밀리초 단위 검색
* **다중 검색 모드:** 파일명/내용 동시 검색 지원
* **고급 필터링:**
    * 파일 크기 범위 설정 (최소/최대 용량)
    * 확장자 필터 (예: `pdf`, `docx`)
    * 대소문자 구분
    * 완전 일치/부분 일치 전환
* **대상 폴더 지정:** 특정 디렉토리 범위 제한 검색
* **통합 미리보기:**
    * 텍스트 파일 (자동 인코딩 감지)
    * 이미지 (JPEG/PNG/움짤 GIF/BMP/WEBP/HEIC)
    * SVG 벡터 그래픽 (자동 확대/축소)
    * 동영상 (재생 컨트롤 지원)
    * 오디오 파일
* **미디어 플레이어 통합:**
    * 기본 재생 컨트롤 제공
    * 팝업 플레이어 창
    * 연속 재생 모드
    * 볼륨 조절 및 음소거
* **빠른 접근 북마크:**
    * 대용량 파일 (>50MB)
    * 동영상 파일
    * 음악 파일
    * 이미지 파일
    * 압축 파일
    * 애플리케이션
* **유연한 정렬:** 이름/크기/수정일/경로 기준 정렬
* **일괄 처리:**
    * Shift/⌘ 키 다중 선택
    * 일괄 작업 (열기/삭제/복사/이동/이름 변경)
    * 우클릭 컨텍스트 메뉴
* **멀티탭 검색:** 동시에 여러 검색 작업 진행:
    * 다른 검색 쿼리를 위한 독립 탭 생성
    * 우클릭으로 탭 관리: 닫기, 다른 탭 닫기, 왼쪽/오른쪽 탭 닫기
    * 탭별 독립적인 검색 결과와 설정
    * Chrome 스타일 탭 환경 (드래그 정렬, 스크롤 버튼 지원)
* **맞춤 설정:**
    * 라이트/다크 모드 전환
    * 미리보기 패널 표시 제어
    * 검색 기록 관리
    * 창 설정 자동 저장
* **데이터 내보내기:** CSV 형식으로 검색 결과 저장
* **대용량 처리:** 단계적 로딩으로 수백만 결과 처리
* **드래그 앤 드롭:** 파일 직접 드래그 지원
* **경로 관리:** 전체 경로/폴더 경로/파일명 즉시 복사

## 사용 방법

1. 검색창에 키워드 입력
2. (선택) 대상 폴더 지정 (공란 시 전체 검색)
3. 고급 필터로 조건 설정
4. 헤더 클릭으로 정렬 기준 변경
5. 보기 → 미리보기로 내용 확인
6. 북마크 메뉴로 자주 찾는 파일 유형 즉시 검색
7. 우클릭으로 상황별 메뉴 호출
8. 검색 결과를 앱에 직접 드래그
9. 내장 플레이어 또는 팝업 창으로 미디어 재생
10. 검색할 때마다 새 탭이 자동 생성되어 여러 검색을 동시 진행
11. 탭을 우클릭하여 관리: 탭 닫기, 다른 탭 닫기, 왼쪽/오른쪽 탭 닫기
12. 다크 모드로 야간 작업 편의성 향상

## 설치 가이드

1. **시스템 요구사항:**
    * Python 3.6 이상
    * PyQt6 라이브러리

2. **소스코드 다운로드:**
    ```bash
    git clone https://github.com/appledragon/everythingByMdfind
    cd everythingByMdfind
    ```

3. **의존성 설치:**
    ```bash
    pip install -r requirements.txt
    ```

4. **프로그램 실행:**
    ```bash
    python everything.py
    ```

## 사용자 설정

* **테마 변경:** 보기 메뉴에서 다크 모드 전환
* **검색 기록:**
  - 자동 저장 기능 (자동완성 지원)
  - 도움말 메뉴에서 기록 기능 해제 가능
* **미리보기 설정:**
  - 텍스트/이미지/동영상/앱 미리보기 지원
  - 미리보기 패널 표시 관리

## 독립 실행 파일 제작 (선택)

py2app으로 macOS용 배포 앱 생성:

1. **패키징 도구 설치:**
    ```bash
    pip install py2app
    ```

2. **설정 파일 생성:**
    ```bash
    cat > setup.py << 'EOF'
    from setuptools import setup

    APP = ['everything.py']
    DATA_FILES = [
        ('', ['LICENSE.md', 'README.md']),
    ]
    OPTIONS = {
        'argv_emulation': False,
        'packages': ['PyQt6'],
        'excludes': [],
        'plist': {
            'CFBundleName': 'Everything',
            'CFBundleDisplayName': 'Everything',
            'CFBundleVersion': '1.3.5',
            'CFBundleShortVersionString': '1.3.5',
            'CFBundleIdentifier': 'com.appledragon.everythingbymdfind',
            'LSMinimumSystemVersion': '10.14',
            'NSHighResolutionCapable': True,
        }
    }

    setup(
        app=APP,
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    )
    EOF
    ```

3. **애플리케이션 빌드:**
    ```bash
    python setup.py py2app
    ```
    `dist` 폴더에 macOS 앱이 생성됩니다

## 기여 안내

버그 리포트/기능 제안/코드 기여 환영!

## 라이선스

[MIT 라이선스](LICENSE.md) 적용

## 개발 팀

Apple Dragon

## 현재 버전

1.3.5

## 크레딧

* PyQt6 개발팀에 감사
* 오픈소스 커뮤니티에 존경을

