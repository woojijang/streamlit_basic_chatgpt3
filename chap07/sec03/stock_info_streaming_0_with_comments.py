# ================================== 주석 해설 시작 ==================================
# 이 파일은 Streamlit + OpenAI Chat Completions(API) + (선택)도구 호출을 활용해
# 주가/시간 등 정보를 스트리밍 출력하는 예제입니다.
# - 핵심 흐름: (1) 환경변수 로딩 → (2) OpenAI 클라이언트 준비 → (3) Streamlit UI 구성
#             (4) 세션 메시지 관리 → (5) 스트리밍 응답 처리 → (6) (옵션) tool_calls 처리
# - 주의: 아래 주석은 이해를 돕기 위한 것으로, 원본 코드의 동작을 변경하지 않습니다.
# ====================================================================================

from gpt_functions import get_current_time, tools, get_yf_stock_info, get_yf_stock_history, get_yf_stock_recommendations
from openai import OpenAI
# .env 파일에서 OPENAI_API_KEY 등을 환경 변수로 로드하기 위한 모듈
from dotenv import load_dotenv
import os
import json
# Streamlit: 웹 UI 렌더링과 입력/출력 처리
import streamlit as st

# .env로부터 환경 변수를 실제 프로세스 환경으로 주입
load_dotenv()
# 환경변수에서 OpenAI API 키 읽기 – client나 SDK가 이를 사용
api_key = os.getenv("OPENAI_API_KEY")  # 환경 변수에서 API 키 가져오기

# OpenAI Chat Completions 엔드포인트를 쓰기 위한 클라이언트 인스턴스
client = OpenAI(api_key=api_key)  # 오픈AI 클라이언트의 인스턴스 생성

# ▶ 모델 호출 함수: messages(대화 히스토리)와 tools(도구 스펙)를 받아
#   Chat Completions API를 호출하고, stream=True일 때는 청크를 yield로 반환
def get_ai_response(messages, tools=None, stream=True):
# OpenAI Chat Completions 호출: model/stream/messages/tools를 전달
    response = client.chat.completions.create(
        model="gpt-4o",  # 응답 생성에 사용할 모델을 지정합니다.
        stream=stream, # (1) 스트리밍 출력을 위해 설정
        messages=messages,  # 대화 기록을 입력으로 전달합니다.
        tools=tools,  # 사용 가능한 도구 목록을 전달합니다.
    )

    if stream: 
        for chunk in response:
            yield chunk  # 생성된 응답의 내용을 yield로 순차적으로 반환합니다.
    else:
        return response  # 생성된 응답의 내용을 반환합니다.


# Streamlit 앱 상단 타이틀/헤더 출력
st.title("💬 Chatbot")   

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "너는 사용자를 도와주는 상담사야."},  # 초기 시스템 메시지
    ] 

# 기존 히스토리의 메시지를 역할(role)에 맞게 화면 말풍선으로 렌더링
for msg in st.session_state.messages:
    if msg["role"] == "assistant" or msg["role"] == "user": # assistant 혹은 user 메시지인 경우만
        st.chat_message(msg["role"]).write(msg["content"])


# 사용자 입력창: 프롬프트를 한 줄 받아서 다음 턴 대화를 진행
if user_input := st.chat_input():    # 사용자 입력 받기
    st.session_state.messages.append({"role": "user", "content": user_input})  # 사용자 메시지를 대화 기록에 추가
    st.chat_message("user").write(user_input)  # 사용자 메시지를 브라우저에서도 출력
    
    ai_response = get_ai_response(st.session_state.messages, tools=tools)
    # print(ai_message) 

    content = ''
    for chunk in ai_response:
# 스트리밍 청크의 증분 토큰(content) 접근하여 누적 표시
        content_chunk = chunk.choices[0].delta.content # ② 청크 속 content 추출
        if content_chunk: # ③ 만약 content_chunk가 있다면, 
            print(content_chunk, end="")	 # ④ 터미널에 줄바꿈 없이 이어서 출력
            content += content_chunk # ⑤ content에 덧붙이기
        
    print('\n===========')
    print(content)

    ai_message = ai_response.choices[0].message
    tool_calls = ai_message.tool_calls  # AI 응답에 포함된 tool_calls를 가져옵니다.
    if tool_calls:  # tool_calls가 있는 경우
        for tool_call in tool_calls:
            tool_name = tool_call.function.name # 실행해야한다고 판단한 함수명 받기
            tool_call_id = tool_call.id         # tool_call 아이디 받기    
# 모델이 전달한 함수 인자(JSON 문자열)를 딕셔너리로 역직렬화
            arguments = json.loads(tool_call.function.arguments) # 문자열을 딕셔너리로 변환    
            
            if tool_name == "get_current_time":  
# 실제 파이썬 함수(도구)를 실행하여 외부 데이터/연산 결과를 획득
                func_result = get_current_time(timezone=arguments['timezone'])
            elif tool_name == "get_yf_stock_info":
# 실제 파이썬 함수(도구)를 실행하여 외부 데이터/연산 결과를 획득
                func_result = get_yf_stock_info(ticker=arguments['ticker'])
            elif tool_name == "get_yf_stock_history":  # get_yf_stock_history 함수 호출
# 실제 파이썬 함수(도구)를 실행하여 외부 데이터/연산 결과를 획득
                func_result = get_yf_stock_history(
                    ticker=arguments['ticker'], 
                    period=arguments['period']
                )
            elif tool_name == "get_yf_stock_recommendations":  # get_yf_stock_recommendations 함수 호출
# 실제 파이썬 함수(도구)를 실행하여 외부 데이터/연산 결과를 획득
                func_result = get_yf_stock_recommendations(
                    ticker=arguments['ticker']
                )

            st.session_state.messages.append({
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

# 모델의 최종 응답을 콘솔/화면에 출력
    print("AI\t: " + ai_message.content)  # AI 응답 출력
# 모델의 최종 응답을 콘솔/화면에 출력
    st.chat_message("assistant").write(ai_message.content)  # 브라우저에 메시지 출력
