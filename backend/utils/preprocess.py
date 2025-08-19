import re
import spacy
import contractions

def preprocess_text(text):
    # Load small English model
    nlp = spacy.load("en_core_web_sm")
    # 1. Remove URLs and promotional lines
    text = re.sub(r"http\S+|www\S+|watch.*?»", "", text, flags=re.IGNORECASE)

    # 2. Remove boilerplate/copyright notices
    text = re.sub(r"Copyright.*?reserved\.", "", text, flags=re.IGNORECASE)
    text = re.sub(r"This material.*?redistributed", "", text, flags=re.IGNORECASE)

    # 3. Normalize quotes/apostrophes
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')

    # 4. Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Fix lowercase 'i' when it’s a pronoun
    text = re.sub(r"\bi\b", "I", text)

    # Remove trailing junk
    text = re.sub(r"E-mail to a friend\s*\.*", "", text, flags=re.IGNORECASE)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = re.sub(r"\.\.+", ".", text)
    text = re.sub(r"\b\w\b", "", text)  # Remove single-letter tokens (can hurt if text has acronyms)
    text = contractions.fix(text)

    # 5. Sentence segmentation using spaCy
    doc = nlp(text)
    sentences = [sent.text.strip().capitalize() for sent in doc.sents if sent.text.strip()]
    
    # 6. Join cleaned sentences
    clean_text = " ".join(sentences)

    return clean_text