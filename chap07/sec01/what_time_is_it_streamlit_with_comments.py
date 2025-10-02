# ================================== 주석 해설 시작 ==================================
# 이 파일은 OpenAI Chat Completions(API)와 (옵션) 함수 호출(tools)을 활용하여
# 현재 시간을 알려주는 간단한 챗봇/터미널/스트림릿 예제를 구현합니다.
# - 핵심 흐름: (1) 환경변수 로딩 → (2) OpenAI 클라이언트 준비 → (3) 메시지/도구 구성
#             (4) 모델 호출 → (5) (툴콜이면) 파라미터 파싱 및 실제 함수 실행 → (6) 응답 표시
# - 주의: 아래 주석은 이해를 돕기 위한 설명이며, 원본 코드의 동작을 변경하지 않습니다.
# ====================================================================================

from gpt_functions import get_current_time, tools 
from openai import OpenAI
# .env 파일을 읽어 환경 변수(예: OPENAI_API_KEY)를 로드하는 유틸리티
from dotenv import load_dotenv
import os
import json
# Streamlit: 웹 UI 렌더링 및 대화형 위젯 제공
import streamlit as st

# .env 로딩 실행: 프로세스 환경에 키/설정 주입
load_dotenv()
# 환경 변수에서 OpenAI API 키 읽기 – OpenAI SDK가 이를 사용
api_key = os.getenv("OPENAI_API_KEY")  # 환경 변수에서 API 키 가져오기

# OpenAI Chat Completions용 클라이언트 인스턴스 생성
client = OpenAI(api_key=api_key)  # 오픈AI 클라이언트의 인스턴스 생성

# ▶ 모델 호출 래퍼 함수: messages(+tools)를 받아 Chat Completions API 호출
# OpenAI 함수 호출 사양(tools)을 인자로 전달할 준비
def get_ai_response(messages, tools=None):
# Chat Completions 요청: model/messages/tools를 전달 (stream 옵션은 비활성일 수 있음)
    response = client.chat.completions.create(
        model="gpt-4o",  # 응답 생성에 사용할 모델 지정
        messages=messages,  # 대화 기록을 입력으로 전달
# OpenAI 함수 호출 사양(tools)을 인자로 전달할 준비
        tools=tools,  # 사용 가능한 도구 목록 전달
    )
    return response  # 생성된 응답 내용 반환

# 페이지 상단 타이틀 출력
st.title("💬 Chatbot")   

if "messages" not in st.session_state:
    st.session_state["messages"] = [
# System 프롬프트: 모델의 역할/톤/규칙을 지정
        {"role": "system", "content": "너는 사용자를 도와주는 상담사야."},  # 초기 시스템 메시지
    ] 

# 히스토리 순회하며 역할(role)에 맞게 말풍선 렌더링
for msg in st.session_state.messages:
    if msg["role"] == "assistant" or msg["role"] == "user": # assistant 혹은 user 메시지인 경우만
        st.chat_message(msg["role"]).write(msg["content"])


# 하단 입력창에서 사용자 프롬프트를 한 줄 입력받음
if user_input := st.chat_input():    # ① 사용자 입력 받기
# 사용자 발화를 히스토리에 추가하여 문맥 유지
    st.session_state.messages.append({"role": "user", "content": user_input})  # ① 사용자 메시지를 대화 기록에 추가
    st.chat_message("user").write(user_input)  # ① 사용자 메시지를 브라우저에서도 출력
    
# OpenAI 함수 호출 사양(tools)을 인자로 전달할 준비
# 현재 히스토리를 컨텍스트로 모델을 호출하여 응답 객체 획득
    ai_response = get_ai_response(st.session_state.messages, tools=tools)
# 첫 번째 선택지의 message 객체(콘텐츠/툴콜 메타 포함)를 추출
    ai_message = ai_response.choices[0].message
# 디버깅: 모델이 반환한 전체 message 객체를 콘솔에 출력(툴콜 구조 파악용)
    print(ai_message)  # ③ gpt에서 반환되는 값을 파악하기 위해 임시로 추가

# 모델이 함수 호출을 제안했는지 확인: tool_calls에 함수명/인자/ID가 담김
    tool_calls = ai_message.tool_calls  # AI 응답에 포함된 tool_calls를 가져옵니다.
    if tool_calls:  # tool_calls가 있는 경우
        for tool_call in tool_calls:
            tool_name = tool_call.function.name # 실행해야한다고 판단한 함수명 받기
            tool_call_id = tool_call.id         # tool_call 아이디 받기    
# 모델이 전달한 JSON 문자열 인자를 파이썬 딕셔너리로 역직렬화
            arguments = json.loads(tool_call.function.arguments) # (1) 문자열을 딕셔너리로 변환    
            
            if tool_name == "get_current_time":  # ⑤ 만약 tool_name이 "get_current_time"이라면
                st.session_state.messages.append({
                    "role": "function",  # role을 "function"으로 설정
                    "tool_call_id": tool_call_id,
                    "name": tool_name,
# 실제 파이썬 함수 실행: 타임존 지정 또는 기본값으로 현재 시각 문자열 생성
                    "content": get_current_time(timezone=arguments['timezone']),  # 타임존 추가
                })
# System 프롬프트: 모델의 역할/톤/규칙을 지정
# 모델에 '툴 결과를 반영하여 답하라'는 힌트를 주는 시스템 메시지
        st.session_state.messages.append({"role": "system", "content": "이제 주어진 결과를 바탕으로 답변할 차례다."}) 
# OpenAI 함수 호출 사양(tools)을 인자로 전달할 준비
# 현재 히스토리를 컨텍스트로 모델을 호출하여 응답 객체 획득
        ai_response = get_ai_response(st.session_state.messages, tools=tools) # 다시 GPT 응답 받기
# 첫 번째 선택지의 message 객체(콘텐츠/툴콜 메타 포함)를 추출
        ai_message = ai_response.choices[0].message

    st.session_state.messages.append({
        "role": "assistant",
        "content": ai_message.content
    })  # ③ AI 응답을 대화 기록에 추가합니다.

# 최종 텍스트 응답을 콘솔에 출력
    print("AI\t: " + ai_message.content)  # AI 응답 출력
# 어시스턴트(모델) 응답을 화면에 출력
    st.chat_message("assistant").write(ai_message.content)  # 브라우저에 메시지 출력
