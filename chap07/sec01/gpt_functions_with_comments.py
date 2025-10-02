# ================================== 주석 해설 시작 ==================================
# 이 파일은 OpenAI Chat Completions(API)와 (옵션) 함수 호출(tools)을 활용하여
# 현재 시간을 알려주는 간단한 챗봇/터미널/스트림릿 예제를 구현합니다.
# - 핵심 흐름: (1) 환경변수 로딩 → (2) OpenAI 클라이언트 준비 → (3) 메시지/도구 구성
#             (4) 모델 호출 → (5) (툴콜이면) 파라미터 파싱 및 실제 함수 실행 → (6) 응답 표시
# - 주의: 아래 주석은 이해를 돕기 위한 설명이며, 원본 코드의 동작을 변경하지 않습니다.
# ====================================================================================

from datetime import datetime
import pytz

def get_current_time(timezone: str = 'Asia/Seoul'):
    tz = pytz.timezone(timezone) # 타임존 설정
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    now_timezone = f'{now} {timezone}'
    print(now_timezone)
    return now_timezone


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "해당 타임존의 날짜와 시간을 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    'timezone': {
                        'type': 'string',
                        'description': '현재 날짜와 시간을 반환할 타임존을 입력하세요. (예: Asia/Seoul)',
                    },
                },
                "required": ['timezone'],
            },        
        }
    },
]


if __name__ == '__main__':
    get_current_time('America/New_York')
