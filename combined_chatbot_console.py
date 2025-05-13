from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.comparisons import LevenshteinDistance
from chatterbot.response_selection import get_first_response
from chatterbot.languages import ENG
import numpy as np
from sentence_transformers import SentenceTransformer
from chatterbot.conversation import Statement

# Initialize Vietnamese model
vietnamese_model = SentenceTransformer('keepitreal/vietnamese-sbert')

class VietnameseEmbeddingComparison:
    def __init__(self, model):
        self.model = model
        
    def compare(self, statement_a, statement_b):
        embedding_a = self.model.encode(statement_a.text)
        embedding_b = self.model.encode(statement_b.text)
        similarity = np.dot(embedding_a, embedding_b) / (np.linalg.norm(embedding_a) * np.linalg.norm(embedding_b))
        return similarity

# Initialize Vietnamese bot
vietnamese_bot = ChatBot(
    "VietnameseBot",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'Xin lỗi, tôi không hiểu ý bạn. Bạn có thể diễn đạt theo cách khác được không?',
            'maximum_similarity_threshold': 0.7,
            'statement_comparison': VietnameseEmbeddingComparison(vietnamese_model),
            'response_selection': get_first_response
        },
        'chatterbot.logic.MathematicalEvaluation',
        'chatterbot.logic.TimeLogicAdapter'
    ],
    database_uri='sqlite:///vietnamese_bot.db'
)

# Train Vietnamese bot
trainer_vn = ChatterBotCorpusTrainer(vietnamese_bot)
try:
    # trainer_vn.train("./vietnamese_corpus")
    print("Vietnamese bot training completed.")
except Exception as e:
    print(f"Error training Vietnamese bot: {str(e)}")

# Initialize English bot
english_bot = ChatBot(
    "EnglishBot",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'Sorry, I don’t understand. Can you rephrase?',
            'maximum_similarity_threshold': 0.7,
            'statement_comparison': LevenshteinDistance(language=ENG),
            'response_selection': get_first_response
        }
    ],
    database_uri='sqlite:///english_bot.db'
)

# Train English bot
trainer_en = ChatterBotCorpusTrainer(english_bot)
try:
    # trainer_en.train("./corpus/")
    print("English bot training completed.")
except Exception as e:
    print(f"Error training English bot: {str(e)}")

def chatbot_reply(text: str, lang: str = 'vi') -> str:
    """
    Trả về câu trả lời từ chatbot dựa trên ngôn ngữ đầu vào.
    Args:
        text (str): Câu hỏi của người dùng.
        lang (str): 'vn' (tiếng Việt) hoặc 'en' (tiếng Anh).
    Returns:
        str: Câu trả lời từ chatbot.
    """
    # Tiền xử lý text (xóa khoảng trắng thừa)
    text = ' '.join(str(text).strip().split())
    
    # Chọn chatbot tương ứng
    if lang.lower() == 'vi':
        bot = vietnamese_bot
    elif lang.lower() == 'en':
        bot = english_bot
    else:
        return "Invalid language code. Use 'vi' or 'en'." + str(lang)
    
    # Lấy câu trả lời từ bot
    try:
        response = bot.get_response(text)
        return str(response)
    except Exception as e:
        print(f"Error processing input: {str(e)}")
        return "Error processing request."


if __name__ == "__main__":
    print("Test Chatbot Function")

    # Vietnamese test
    input_text = "Cuối tuần này bạn có đi chơi không?"
    reply = chatbot_reply(input_text, lang='vi')
    print(f"Vietnamese Bot: {reply}")

    # English test
    input_text = "Hello"
    reply = chatbot_reply(input_text, lang='en')
    print(f"English Bot: {reply}")
