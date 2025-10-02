# ================================== 주석 해설 시작 ==================================
# 이 파일은 Streamlit + OpenAI Chat Completions(API) + (선택)도구 호출을 활용하는 예제입니다.
# - 핵심 흐름: (1) 환경변수 로딩 → (2) OpenAI 클라이언트 준비 → (3) Streamlit UI 구성
#             (4) 세션 메시지 관리 → (5) 모델 호출/스트리밍 처리 → (6) (옵션) tool_calls 처리
# - 주의: 아래 주석은 이해를 돕기 위한 설명이며, 원본 코드의 동작을 변경하지 않습니다.
# ====================================================================================

from datetime import datetime
import pytz
import yfinance as yf

def get_current_time(timezone: str = 'Asia/Seoul'):
    tz = pytz.timezone(timezone) # 타임존 설정
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    now_timezone = f'{now} {timezone}'
    print(now_timezone)
    return now_timezone

def get_yf_stock_info(ticker: str):
    stock = yf.Ticker(ticker)
    info = stock.info
    print(info)
    return str(info)



# 도구(함수 호출) 스펙 또는 실제 도구 함수 임포트
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
    {
        "type": "function",
        "function": {
            "name": "get_yf_stock_info",
            "description": "해당 종목의 Yahoo Finance 정보를 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    'ticker': {
                        'type': 'string',
                        'description': 'Yahoo Finance 정보를 반환할 종목의 티커를 입력하세요. (예: AAPL)',
                    },
                },
                "required": ['ticker'],
            },        
        }
    }
]


if __name__ == '__main__':
    # get_current_time('America/New_York')
    info = get_yf_stock_info('AAPL')    
