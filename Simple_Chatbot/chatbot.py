import spacy
from intents import intents

nlp = spacy.load("chatbot_model")


answers = {}


def recognize_intent(text):
    doc = nlp(text)
    intent = max(doc.cats, key=doc.cats.get)
    confidence = doc.cats[intent]
    return intent, confidence

def answer(text):
    intent, conf = recognize_intent(text)
    if conf < 0.5:
        return "didn't understand this "
    return answers.get(intent, f"intent recognize: {intent}")



#Chat start
print("🤖 chatbot startet (exit to finish)")
while True:
    user = input("Du: ")
    if user.lower() in ["exit", "ende"]:
        break
    print("Bot:", answer(user))
