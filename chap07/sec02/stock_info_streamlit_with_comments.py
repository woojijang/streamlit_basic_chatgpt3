# ================================== 주석 해설 시작 ==================================
# 이 파일은 Streamlit + OpenAI Chat Completions(API) + (선택)도구 호출을 활용하는 예제입니다.
# - 핵심 흐름: (1) 환경변수 로딩 → (2) OpenAI 클라이언트 준비 → (3) Streamlit UI 구성
#             (4) 세션 메시지 관리 → (5) 모델 호출/스트리밍 처리 → (6) (옵션) tool_calls 처리
# - 주의: 아래 주석은 이해를 돕기 위한 설명이며, 원본 코드의 동작을 변경하지 않습니다.
# ====================================================================================

# 도구(함수 호출) 스펙 또는 실제 도구 함수 임포트
from gpt_functions import get_current_time, tools, get_yf_stock_info, get_yf_stock_history, get_yf_stock_recommendations
from openai import OpenAI
# .env 파일에서 OPENAI_API_KEY 등 환경 변수를 로드하기 위한 모듈
from dotenv import load_dotenv
import os
import json
# Streamlit: 대화형 웹 UI 구성/렌더링 라이브러리
import streamlit as st

# .env 로딩: 실행 환경에 환경 변수 주입
load_dotenv()
# 환경 변수에서 OpenAI API 키 읽기 – OpenAI SDK에서 사용
api_key = os.getenv("OPENAI_API_KEY")  # 환경 변수에서 API 키 가져오기

# OpenAI Chat Completions용 클라이언트 인스턴스 생성
client = OpenAI(api_key=api_key)  # 오픈AI 클라이언트의 인스턴스 생성

# ▶ 모델 호출 함수: (messages, tools)를 받아 Chat Completions API를 호출
def get_ai_response(messages, tools=None):
# Chat Completions 요청: model/messages/tools 전달(필요시 stream=True 가능)
    response = client.chat.completions.create(
        model="gpt-4o",  # 응답 생성에 사용할 모델 지정
        messages=messages,  # 대화 기록을 입력으로 전달
        tools=tools,  # 사용 가능한 도구 목록 전달
    )
    return response  # 생성된 응답 내용 반환

# Streamlit 페이지 타이틀 표시
st.title("💬 Chatbot")   

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "너는 사용자를 도와주는 상담사야."},  # 초기 시스템 메시지
    ] 

# 기존 히스토리를 역할(role)에 따라 UI에 렌더링
for msg in st.session_state.messages:
    if msg["role"] == "assistant" or msg["role"] == "user": # assistant 혹은 user 메시지인 경우만
        st.chat_message(msg["role"]).write(msg["content"])


# 사용자 입력창: 프롬프트를 한 줄 받아 대화 흐름 진행
if user_input := st.chat_input():    # 사용자 입력 받기
    st.session_state.messages.append({"role": "user", "content": user_input})  # 사용자 메시지를 대화 기록에 추가
    st.chat_message("user").write(user_input)  # 사용자 메시지를 브라우저에서도 출력
    
    ai_response = get_ai_response(st.session_state.messages, tools=tools)
    ai_message = ai_response.choices[0].message
    print(ai_message)  # gpt에서 반환되는 값을 파악하기 위해 임시로 추가

# tool_calls 처리: 모델이 선택한 함수 이름/인자(JSON)를 파싱해 실제 함수 실행
    tool_calls = ai_message.tool_calls  # AI 응답에 포함된 tool_calls를 가져옵니다.
# tool_calls 처리: 모델이 선택한 함수 이름/인자(JSON)를 파싱해 실제 함수 실행
    if tool_calls:  # tool_calls가 있는 경우
# tool_calls 처리: 모델이 선택한 함수 이름/인자(JSON)를 파싱해 실제 함수 실행
        for tool_call in tool_calls:
            tool_name = tool_call.function.name # 실행해야한다고 판단한 함수명 받기
            tool_call_id = tool_call.id         # tool_call 아이디 받기    
            arguments = json.loads(tool_call.function.arguments) # 문자열을 딕셔너리로 변환    
            
            if tool_name == "get_current_time":  
                func_result = get_current_time(timezone=arguments['timezone'])
            elif tool_name == "get_yf_stock_info":
                func_result = get_yf_stock_info(ticker=arguments['ticker'])
            elif tool_name == "get_yf_stock_history":  # get_yf_stock_history 함수 호출
                func_result = get_yf_stock_history(
                    ticker=arguments['ticker'], 
                    period=arguments['period']
                )
            elif tool_name == "get_yf_stock_recommendations":  # get_yf_stock_recommendations 함수 호출
                func_result = get_yf_stock_recommendations(
                    ticker=arguments['ticker']
                )

            st.session_state.messages.append({
# tool_calls 처리: 모델이 선택한 함수 이름/인자(JSON)를 파싱해 실제 함수 실행
                "role": "function",
                "tool_call_id": tool_call_id,
                "name": tool_name,
                "content": func_result,
            })


        st.session_state.messages.append({"role": "system", "content": "이제 주어진 결과를 바탕으로 답변할 차례다."}) 
        ai_response = get_ai_response(st.session_state.messages, tools=tools) # 다시 GPT 응답 받기
        ai_message = ai_response.choices[0].message

    st.session_state.messages.append({
        "role": "assistant",
        "content": ai_message.content
    })  # ③ AI 응답을 대화 기록에 추가합니다.

# 모델 응답을 화면/콘솔에 출력
    print("AI\t: " + ai_message.content)  # AI 응답 출력
# 모델 응답을 화면/콘솔에 출력
    st.chat_message("assistant").write(ai_message.content)  # 브라우저에 메시지 출력
