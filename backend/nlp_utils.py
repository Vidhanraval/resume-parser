import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize

stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

def preprocess_text(text: str):
    # Lowercase
    text = text.lower()

    # Remove numbers & punctuation
    text = re.sub(r"[^a-z\s]", " ", text)

    # Tokenization
    tokens = word_tokenize(text)

    processed = []
    for token in tokens:
        if token not in stop_words and len(token) > 2:
            lemma = lemmatizer.lemmatize(token)
            stem = stemmer.stem(lemma)
            processed.append(stem)

    return processed
