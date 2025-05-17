# CabinTranslate

CabinTranslate là hệ thống hỗ trợ giao tiếp song ngữ (Anh - Việt) tích hợp nhận diện giọng nói, chatbot AI, dịch tự động, chuyển văn bản thành giọng nói (TTS), và nhận diện cảm xúc. Dự án cung cấp cả giao diện người dùng hiện đại bằng PyQt5 và ứng dụng web Streamlit.

## Tính năng chính
- **Nhận diện giọng nói real-time**: Sử dụng mô hình Whisper để chuyển đổi giọng nói thành văn bản (Anh/Việt).
- **Chatbot song ngữ**: Chatbot AI hỗ trợ tiếng Việt (SBERT + ChatterBot) và tiếng Anh (ChatterBot).
- **Dịch tự động & TTS**: Dịch văn bản và chuyển thành giọng nói tự nhiên (Edge TTS, Google Translate).
- **Nhận diện cảm xúc**: Phân tích cảm xúc từ văn bản bằng mô hình DistilBERT.
- **Giao diện người dùng**:
  - PyQt5: Giao diện desktop hiện đại, trực quan.
  - Streamlit: Ứng dụng web đơn giản, dễ sử dụng.
- **Gợi ý động viên thông minh**: Sử dụng GPT để sinh câu hỏi hỗ trợ tâm lý.

## Yêu cầu hệ thống
- Python >= 3.8
- Windows (khuyến nghị), Linux có thể cần chỉnh sửa nhỏ
- Card đồ họa (nếu muốn tăng tốc với CUDA)

## Cài đặt
1. Clone dự án:
   ```powershell
   git clone https://github.com/SweetLove1643/CabinTranslate.git
   cd CabinTranslate
   ```
2. Cài đặt thư viện:
   ```powershell
   pip install -r requirements.txt
   ```
3. (Tùy chọn) Tải/cài đặt các mô hình AI cần thiết (Whisper, DistilBERT, SBERT...)

## Hướng dẫn sử dụng
### Chạy giao diện desktop (PyQt5)
```powershell
python main_small.py
```

### Chạy ứng dụng web (Streamlit)
```powershell
streamlit run app.py
```

### Các file chính
- `main_small.py`, `main.py`, `test.py`: Chạy nhận diện giọng nói, giao diện PyQt5, tích hợp chatbot, cảm xúc, dịch, TTS.
- `app.py`, `views/tts_view.py`: Ứng dụng web Streamlit.
- `GUI.py`: Giao diện PyQt5.
- `combined_chatbot_console.py`: Chatbot song ngữ.
- `predict.py`: Nhận diện cảm xúc.
- `translate.py`, `controllers/tts_controller.py`, `models/tts_model.py`: Dịch và chuyển văn bản thành giọng nói.
- `GPT_Rec.py`: Gợi ý động viên bằng GPT.

### Cấu trúc thư mục
```
CabinTranslate/
├── main.py, main_small.py, test.py
├── app.py
├── GUI.py
├── combined_chatbot_console.py
├── predict.py
├── translate.py
├── GPT_Rec.py
├── requirements.txt
├── README.md
├── controllers/
│   └── tts_controller.py
├── models/
│   └── tts_model.py
├── utils/
│   └── config.py
├── views/
│   └── tts_view.py
├── corpus/, vietnamese_corpus/ (dữ liệu chatbot)
├── icon/ (icon giao diện)
```

## Thông tin kỹ thuật
- Nhận diện giọng nói: [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- Chatbot: [ChatterBot](https://github.com/gunthercox/ChatterBot), SBERT, Sentence Transformers
- Dịch: [deep-translator](https://github.com/nidhaloff/deep-translator)
- TTS: [Edge-TTS](https://github.com/ranyelhousieny/edge-tts)
- Nhận diện cảm xúc: [transformers](https://github.com/huggingface/transformers)
- Giao diện: PyQt5, Streamlit

## Đóng góp & bản quyền
- Tác giả: CabinTranslate Team
- License: MIT

---
*Vui lòng xem chi tiết từng file để biết thêm về cách mở rộng, huấn luyện chatbot, hoặc tích hợp thêm tính năng.*
