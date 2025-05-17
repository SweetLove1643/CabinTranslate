import openai
from dotenv import load_dotenv # type: ignore

load_dotenv(".env")
openai.api_key = load_dotenv("OPENAI_API_KEY")


def support_prompt(mood, last_reply, language="en"):
    if language == "vi":
    
        return f"""
Bạn tôi đang cảm thấy {mood}.
Tôi đã hỏi thăm và bạn ấy trả lời: "{last_reply}"

Hãy giúp tôi tạo chính xác 5 câu hỏi tốt nhất để hỗ trợ, khuyên nhủ, và giúp bạn ấy cảm thấy tốt hơn.
Các câu hỏi cần thể hiện sự thấu hiểu, nhẹ nhàng, đồng cảm và gợi mở giúp bạn ấy chia sẻ nhiều hơn.
Hãy liệt kê danh sách rõ ràng như sau:
1.
2.
3.
4.
5.
"""
    else:
        return f"""
My friend is in a {mood} mood.
I asked him some questions and he said: "{last_reply}"

Please give me exactly 5 of the best questions to support, advise, and help him.
Make sure the questions are empathetic, supportive, and help him feel better.
Reply only as a caring friend, list the questions as:
1.
2.
3.
4.
5.
"""

def get_support_questions(mood, last_reply, language="en"):
    prompt = support_prompt(mood, last_reply, language)

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a kind and empathetic friend."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )

    return response.choices[0].message.content

# ✅ Test thử
mood = "buồn"
last_reply = "Hôm qua mình rất vui nhưng vì trễ deadline nên hôm nay mình rất buồn"

# ✅ Test tiếng Việt
result_vi = get_support_questions(mood, last_reply, language="vi")
print("🎯 Câu hỏi động viên (VI):\n", result_vi)

# ✅ Test tiếng Anh
mood_en = "sad"
last_reply_en = "Yesterday I was very happy but because I missed the deadline I am very sad today"
result_en = get_support_questions(mood_en, last_reply_en, language="en")
print("\n🎯 Support Questions (EN):\n", result_en)
