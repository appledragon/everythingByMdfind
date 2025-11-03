# Everything by mdfind
[English](README.md) | [中文](README_CN.md) | [한국어](README_KO.md) | [日本語](README_JP.md) | [Français](README_FR.md) | [Deutsch](README_DE.md) | [Español](README_ES.md)

<img width="3836" height="2026" alt="image" src="https://github.com/user-attachments/assets/d86c3d6b-6fd4-4cfe-b64f-67c465bb3d3c" /><img width="3832" height="2024" alt="image" src="https://github.com/user-attachments/assets/a91d2b13-07ac-4cae-ab33-506f1fa3bca6" />

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
    * 6가지 아름다운 테마 선택:
        * 라이트/다크 (시스템 기본)
        * Tokyo Night/Tokyo Night Storm (도쿄 나이트)
        * Chinolor Dark/Chinolor Light (중국 전통색)
    * 선택한 테마와 어울리는 시스템 타이틀바
    * 미리보기 패널 표시 제어
    * 검색 기록 관리
    * 창 설정 자동 저장
* **다중 형식 내보내기:** 여러 형식으로 검색 결과 저장:
    * JSON - 구조화된 데이터 형식
    * Excel (.xlsx) - 서식이 있는 스프레드시트
    * HTML - 웹 준비 테이블 형식
    * Markdown - 문서 친화적 형식
    * CSV - 전통적인 쉼표 구분 형식
* **대용량 처리:** 단계적 로딩으로 수백만 결과 처리
* **드래그 앤 드롭:** 파일 직접 드래그 지원
* **경로 관리:** 전체 경로/폴더 경로/파일명 즉시 복사

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

## 설치 버전 다운로드

[GitHub Releases](https://github.com/appledragon/everythingByMdfind/releases) 페이지에서 바로 사용 가능한 macOS 애플리케이션(.dmg)을 직접 다운로드할 수 있습니다.

## 기여 안내

버그 리포트/기능 제안/코드 기여 환영!

## 라이선스

[Apache License 2.0](LICENSE.md) 적용

## 개발 팀

Apple Dragon

## 현재 버전

1.3.7

## 크레딧

* PyQt6 개발팀에 감사
* 오픈소스 커뮤니티에 존경을

