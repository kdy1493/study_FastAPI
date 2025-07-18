# study_FastAPI

이 프로젝트는 FastAPI를 학습하고 간단한 API 서버를 구축하는 예제입니다.

## 시작하기

이 프로젝트를 로컬 컴퓨터에서 설정하고 실행하려면 아래 단계를 따르세요.

### 사전 요구 사항

이 프로젝트는 [uv](https://github.com/astral-sh/uv)를 사용하여 파이썬 패키지와 가상 환경을 관리합니다. `uv`가 설치되어 있어야 합니다.

### 설치

1.  **Git 저장소 복제(Clone):**
    ```bash
    git clone https://github.com/kdy1493/study_FastAPI.git
    cd study_FastAPI
    ```

2.  **가상 환경 생성 및 활성화:**
    `uv`를 사용하여 가상 환경을 생성합니다. `.venv`라는 폴더에 생성됩니다.
    ```bash
    uv venv
    ```
    생성된 가상 환경을 활성화하세요.
    *   **Windows (PowerShell):**
        ```powershell
        .venv\Scripts\Activate.ps1
        ```
    *   **Windows (CMD):**
        ```bash
        .venv\Scripts\activate
        ```
    *   **macOS / Linux:**
        ```bash
        source .venv/bin/activate
        ```

3.  **의존성 패키지 설치:**
    `uv sync` 명령어를 사용하여 `uv.lock` 파일에 명시된 버전과 정확히 일치하는 패키지들을 설치합니다.
    ```bash
    uv sync
    ```

### 실행

Uvicorn 서버를 사용하여 FastAPI 애플리케이션을 실행합니다.
```bash
uvicorn example_1:app --reload
```
`