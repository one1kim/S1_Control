import streamlit as st
import pandas as pd
import time
from datetime import datetime
import os



DATA_FILE = "data.csv"
COMPLETE_FILE = "completed.csv"


# 파일 로딩
if os.path.exists(DATA_FILE):
    data = pd.read_csv(DATA_FILE)
else:
    data = pd.DataFrame(columns=['설비명', 'Unit명', '등록일시'])

if os.path.exists(COMPLETE_FILE):
    completed = pd.read_csv(COMPLETE_FILE)
else:
    completed = pd.DataFrame(columns=['설비명', 'Unit명', '등록일시', '완료일시'])

st.title("S1L Unit Control 관리 앱")

def register_and_reset():
    if st.session_state["설비명"] and st.session_state["Unit명"]:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = pd.DataFrame([[st.session_state["설비명"], st.session_state["Unit명"], now]],
                               columns=['설비명', 'Unit명', '등록일시'])
        updated = pd.concat([data, new_row], ignore_index=True)
        updated.to_csv(DATA_FILE, index=False)

        # 입력 초기화 후 리렌더링
        st.session_state["설비명"] = ""
        st.session_state["Unit명"] = ""
        st.toast("Control 등록 완료!", icon="✅")

    else:
        st.toast("설비명과 Unit을 모두 입력해주세요.", icon="❌")

# 입력 폼
with st.form("입력폼"):
    st.text_input("설비명 입력", placeholder="설비호기를 입력해주세요", key="설비명")
    st.text_input("Unit 입력", placeholder="Unit을 입력해주세요", key="Unit명")
    st.form_submit_button("등록하기", on_click=register_and_reset)


# 현재 등록된 데이터 표시
st.subheader("📋 현재 Control 중인 설비")

if data.empty:
    st.info("현재 Control 중인 설비가 없습니다")
else:
    for idx, row in data.iterrows():
        col1, col2, col3, col4, col5 = st.columns([3, 3, 6, 2.5, 2.5])
        with col1:
            st.markdown(f"**설비명:** {row['설비명']}")
        with col2:
            st.markdown(f"**Unit명:** {row['Unit명']}")
        with col3:
            # ✅ 초 없이 출력
            try:
                등록일시 = pd.to_datetime(row['등록일시'], errors='coerce').strftime("%Y-%m-%d %H:%M")
            except:
                등록일시 = row['등록일시']
            st.markdown(f"**등록일시:** {등록일시}")
        with col4:
            if st.button("✅ 완료", key=f"complete_{idx}"):
                # 완료 처리 코드
                done_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_row = pd.DataFrame([[row['설비명'], row['Unit명'], row['등록일시'], done_time]],
                                       columns=['설비명', 'Unit명', '등록일시', '완료일시'])
                completed = pd.concat([completed, new_row], ignore_index=True)
                completed.to_csv(COMPLETE_FILE, index=False)

                data.drop(index=idx, inplace=True)
                data.reset_index(drop=True, inplace=True)
                data.to_csv(DATA_FILE, index=False)
                st.toast("Control 확인 완료!", icon="✅")
                time.sleep(1)
                st.rerun()

        with col5:
            if st.button("🗑 삭제", key=f"delete_{idx}"):
                data.drop(index=idx, inplace=True)
                data.reset_index(drop=True, inplace=True)
                data.to_csv(DATA_FILE, index=False)
                st.toast("삭제 완료!", icon="🗑")
                time.sleep(1)
                st.rerun()

# 완료 항목 보기
st.subheader("✅ Control 완료 항목")

if completed.empty:
    st.info("완료된 항목이 없습니다.")
else:
    # 날짜 선택 (기본은 오늘)
    completed['등록일'] = pd.to_datetime(completed['등록일시'], errors='coerce').dt.date
    all_dates = completed['등록일'].dropna().unique()
    all_dates.sort()

    default_date = datetime.today().date() if datetime.today().date() in all_dates else all_dates[-1]
    selected_date = st.date_input("날짜 선택", value=default_date, min_value=min(all_dates), max_value=max(all_dates))

    # 날짜 기준 필터링
    filtered = completed[completed['등록일'] == selected_date].copy()

    if filtered.empty:
        st.warning(f"{selected_date}에 완료된 항목이 없습니다.")
    else:
        # 초 제거
        filtered['등록일시'] = pd.to_datetime(filtered['등록일시'], errors='coerce').dt.strftime("%Y-%m-%d %H:%M")
        filtered['완료일시'] = pd.to_datetime(filtered['완료일시'], errors='coerce').dt.strftime("%Y-%m-%d %H:%M")

        # ✅ Pandas 인덱스를 1부터 시작하도록 설정
        filtered.index = range(1, len(filtered) + 1)

        # ✅ 표시
        st.dataframe(filtered.drop(columns=["등록일"]), use_container_width=True)