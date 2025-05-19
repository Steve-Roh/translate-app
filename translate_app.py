import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import easyocr
from googletrans import Translator
import numpy as np
import io
import zipfile
import os

# OCR 및 번역기 초기화
reader = easyocr.Reader(['ch_sim', 'en'])  # 중국어 간체 + 영어
translator = Translator()

# 앱 제목
st.title("🈶 중국어 → 한국어 이미지 자동 번역기")
st.write("이미지를 업로드하면 중국어를 한국어로 번역해서 다시 이미지로 저장해줘요!")

# 이미지 업로드 (최대 20장)
uploaded_files = st.file_uploader(
    "📤 이미지 업로드 (최대 20장)", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files and len(uploaded_files) > 20:
    st.warning("⚠️ 최대 20장까지만 업로드 가능합니다.")
    uploaded_files = uploaded_files[:20]

# 번역 시작 버튼
if uploaded_files and st.button("🔄 번역 시작하기"):
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for uploaded_file in uploaded_files:
            # 이미지 열고 NumPy로 변환
            image = Image.open(uploaded_file).convert("RGB")
            image_np = np.array(image)
            draw = ImageDraw.Draw(image)

            try:
                font = ImageFont.truetype("arial.ttf", size=16)
            except:
                font = ImageFont.load_default()

            # OCR로 텍스트 추출
            results = reader.readtext(image_np)

            for (bbox, text, prob) in results:
                try:
                    translated = translator.translate(text, src='zh-cn', dest='ko').text
                except:
                    translated = "[번역 실패]"

                top_left = bbox[0]
                draw.text(top_left, translated, font=font, fill=(255, 0, 0))

            # 이미지 저장
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            zip_file.writestr(f"translated_{uploaded_file.name}", img_bytes.getvalue())

    st.success("✅ 번역 완료! 아래 버튼을 눌러 이미지 ZIP을 다운로드하세요.")
    st.download_button(
        "📥 ZIP 파일 다운로드",
        zip_buffer.getvalue(),
        file_name="translated_images.zip"
    )

# 앱 종료 버튼
st.divider()
st.warning("번역이 완료되었다면 아래 '앱 종료' 버튼을 눌러주세요.")
if st.button("❌ 앱 종료"):
    st.info("앱을 종료합니다. 감사합니다.")
    os._exit(0)
