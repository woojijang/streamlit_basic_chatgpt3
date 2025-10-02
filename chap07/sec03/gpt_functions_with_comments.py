# ================================== 주석 해설 시작 ==================================
# 이 파일은 OpenAI 함수 호출(도구 호출)과 연동할 수 있는 헬퍼 함수들을 모아두고,
# 각 함수를 Chat Completions의 tools 사양(JSON 스키마)로 노출하기 위한 예제입니다.
# - 핵심 구성:
#   (1) 시간 조회(get_current_time)
#   (2) Yahoo Finance 티커 정보(get_yf_stock_info)
#   (3) Yahoo Finance 히스토리 시세(get_yf_stock_history)
#   (4) Yahoo Finance 애널리스트 추천(get_yf_stock_recommendations)
#   (5) 위 함수를 OpenAI 함수호출용 tools 리스트로 공개(JSON 스키마 포함)
# - 주의: 아래 주석은 이해를 돕기 위한 설명이며, 원본 코드의 동작을 변경하지 않습니다.
# ====================================================================================

# 표준 datetime 모듈에서 현재 시각을 얻고 포맷하기 위해 import
from datetime import datetime
# pytz: IANA 타임존(예: 'Asia/Seoul') 처리용 라이브러리
import pytz
# yfinance: 야후 파이낸스 비공식 API. 티커 정보/시세/추천 등을 조회
import yfinance as yf

# ------------------------------------------------------------------
# get_current_time(timezone: str = 'Asia/Seoul')
#  - 입력: timezone(IANA 타임존 문자열)
#  - 처리: pytz로 타임존 객체 생성 → 현재 시각을 해당 타임존 기준으로 포맷
#  - 반환: 'YYYY-MM-DD HH:MM:SS Asia/Seoul' 형태의 문자열
#  - 활용: LLM의 함수 호출(tool_calls)로 현재 시각을 실시간 제공할 때 사용
# ------------------------------------------------------------------
def get_current_time(timezone: str = 'Asia/Seoul'):
# 주의: 잘못된 타임존이면 예외 발생 가능(실무에선 예외 처리 권장)
    tz = pytz.timezone(timezone) # 타임존 설정
# strftime으로 사람이 읽기 쉬운 문자열 포맷으로 변환
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    now_timezone = f'{now} {timezone}'
    print(now_timezone)
    return now_timezone

# ------------------------------------------------------------------
# get_yf_stock_info(ticker: str)
#  - 입력: ticker(예: 'AAPL', 'MSFT')
#  - 처리: yf.Ticker(ticker).info로 야후 파이낸스 티커 메타정보 조회
#  - 반환: info 딕셔너리를 문자열로 변환하여 리턴(LLM이 그대로 읽기 쉬움)
#  - 주의: yfinance의 .info는 비동기 변경/차단 가능; 키가 가끔 다를 수 있음
# ------------------------------------------------------------------
def get_yf_stock_info(ticker: str):
    stock = yf.Ticker(ticker)
# info는 dict 구조. 키/값은 종목과 시점에 따라 상이
    info = stock.info
    print(info)
    return str(info)

# ------------------------------------------------------------------
# get_yf_stock_history(ticker: str, period: str)
#  - 입력: ticker(종목 코드), period('1d','5d','1mo','1y','5y' 등)
#  - 처리: yf.Ticker(ticker).history(period=period)로 시세 데이터프레임 조회
#  - 반환: DataFrame을 Markdown 표 형식 문자열로 변환(.to_markdown())
#  - 장점: LLM에 표 형태로 전달하면 답변/요약/차트 지시가 수월
# ------------------------------------------------------------------
def get_yf_stock_history(ticker: str, period: str):
    stock = yf.Ticker(ticker)
# history는 pandas.DataFrame. 인덱스는 날짜/시간, 컬럼은 Open/High/Low/Close/Volume 등
    history = stock.history(period=period)
# 스트리밍/프롬프트 내 표시가 용이하도록 Markdown 테이블로 직렬화
    history_md = history.to_markdown() # 데이터프레임을 마크다운 형식으로 변환
    print(history_md)
    return history_md

# ------------------------------------------------------------------
# get_yf_stock_recommendations(ticker: str)
#  - 입력: ticker(종목 코드)
#  - 처리: yf.Ticker(ticker).recommendations로 애널리스트 추천표 조회
#  - 반환: 추천표(DataFrame)를 Markdown 표 문자열로 변환하여 리턴
#  - 주의: 일부 티커는 추천 데이터가 없을 수 있으며 None이 될 수 있음
# ------------------------------------------------------------------
def get_yf_stock_recommendations(ticker: str):
    stock = yf.Ticker(ticker)
# 추천 데이터가 없으면 None 반환 가능 → .to_markdown() 호출 전 None 체크 필요(실무 권장)
    recommendations = stock.recommendations
    recommendations_md = recommendations.to_markdown() # 데이터프레임을 마크다운 형식으로 변환
    print(recommendations_md)
    return recommendations_md


# ------------------------------------------------------------------
# OpenAI Chat Completions의 함수 호출(=Tools) 스키마 정의
#  - 각 항목은 {'type': 'function', 'function': {...}} 형태의 사양
#  - 'parameters'는 JSON 스키마 규약을 따름(type/properties/required)
#  - 모델이 이 스키마를 참고해 함수명을 선택하고 인자를 JSON으로 제공
#  - 서버(파이썬)는 해당 JSON을 파싱하여 실제 함수를 실행한 뒤 결과를 답변에 반영
# ------------------------------------------------------------------
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
    },
    {
        "type": "function",
        "function": {
            "name": "get_yf_stock_history",
            "description": "해당 종목의 Yahoo Finance 주가 정보를 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    'ticker': {
                        'type': 'string',
                        'description': 'Yahoo Finance 주가 정보를 반환할 종목의 티커를 입력하세요. (예: AAPL)',
                    },
                    'period': {
                        'type': 'string',
                        'description': '주가 정보를 조회할 기간을 입력하세요. (예: 1d, 5d, 1mo, 1y, 5y)',
                    },
                },
                "required": ['ticker', 'period'],
            },        
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_yf_stock_recommendations",
            "description": "해당 종목의 Yahoo Finance 추천 정보를 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    'ticker': {
                        'type': 'string',
                        'description': 'Yahoo Finance 추천 정보를 반환할 종목의 티커를 입력하세요. (예: AAPL)',
                    },
                },
                "required": ['ticker'],
            },        
        }
    },
]


# ------------------------------------------------------------------
# 모듈 단독 실행 시 간단 테스트 구간
#  - 아래 호출 예시는 실제 API 요청을 발생시키므로 네트워크 환경 필요
#  - yfinance는 속도/안정성이 티커/시점/지역에 따라 달라질 수 있음
# ------------------------------------------------------------------
if __name__ == '__main__':
    # get_current_time('America/New_York')
    # info = get_yf_stock_info('AAPL')  

    get_yf_stock_history('AAPL', '5d')
    print('----')
    get_yf_stock_recommendations('AAPL')
  
