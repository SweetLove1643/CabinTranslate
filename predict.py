from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import torch
from pathlib import Path

# ✅ Biến toàn cục để cache model khi load lần đầu
clf_pipeline = None

def predict_emotion(text: str, model_dir: Path = Path('./emotion_model_distilbert')) -> dict:
    """
    Predict emotion from input text using DistilBERT emotion classifier.

    Args:
        text (str): Input text to classify.
        model_dir (Path): Path to the saved model directory. Default is './emotion_model_distilbert'.

    Returns:
        dict: Prediction result with 'label' and 'score'.
    """
    global clf_pipeline

    if clf_pipeline is None:
        print(f"Loading model from: {model_dir.resolve()}")

        model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        tokenizer = AutoTokenizer.from_pretrained(model_dir)

        device_id = 0 if torch.cuda.is_available() else -1

        clf_pipeline = pipeline('text-classification', model=model, tokenizer=tokenizer, device=device_id)

    result = clf_pipeline(text)

    # Trả về kết quả đơn giản chỉ chứa label & score
    return {'label': result[0]['label'], 'score': result[0]['score']}

# ✅ Test thử
if __name__ == "__main__":
    text_input = "I am not happy and excited today!"
    output = predict_emotion(text_input)
    print('Prediction:', output)
