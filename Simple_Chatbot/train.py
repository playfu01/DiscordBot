import spacy
import json
import random
from spacy.util import minibatch
from intent_list import intents


nlp = spacy.blank("de")
textcat = nlp.add_pipe("textcat", config={"exclusive_classes": True})


for label in intents:
    textcat.add_label(label)
    print(label)


with open("train_data.jsoon", "r", encoding="utf-8") as f:
    TRAIN_DATA = json.load(f)

optimizer = nlp.initialize()
for epoch in range(5):
    random.shuffle(TRAIN_DATA)
    losses = {}
    batches = minibatch(TRAIN_DATA, size=2)
    for batch in batches:
        texts, annotations = zip(*batch)
        nlp.update(texts, annotations, sgd=optimizer, losses=losses)
    print(f"Epoch {epoch+1} Loss:", losses)

nlp.to_disk("chatbot_model")
print("✅ Modell gespeichert unter chatbot_model/")


