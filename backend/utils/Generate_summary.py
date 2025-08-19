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
    
class changelang():
    def __init__(self):
        lang_model = "facebook/nllb-200-distilled-600M"  # or your specific model
        self.device = torch.device("cpu")
        self.lang_tokenizer = AutoTokenizer.from_pretrained(lang_model)
        self.lang_model = AutoModelForSeq2SeqLM.from_pretrained(lang_model).to(self.device)

    def change_language(self, text, language):
        inputs = self.lang_tokenizer(text, return_tensors="pt")
        target_lang = language
        forced_bos_token_id=self.lang_tokenizer.convert_tokens_to_ids(target_lang)
        translated = self.lang_model.generate(
        **inputs,
        forced_bos_token_id=forced_bos_token_id,
        max_length = 512,
        num_beams = 4,
        early_stopping = True,
        do_sample = False
        )
        translated_text = self.lang_tokenizer.decode(translated[0], skip_special_tokens=True)
        return translated_text