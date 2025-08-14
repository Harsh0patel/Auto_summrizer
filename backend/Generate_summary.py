import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class Generate_summary():
    def __init__(self):
        model = "google/long-t5-tglobal-base"
        self.device = torch.device("cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model).to(self.device)

    def summury_generated(self, text):
        text = "summarize: " + text
        inputs = self.tokenizer(text, return_tensors="pt", max_length=4096, truncation=True).to(self.device)

        summary_ids = self.model.generate(inputs["input_ids"], max_length=256, num_beams=4, early_stopping=True)
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        return summary