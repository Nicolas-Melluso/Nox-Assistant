
from ..utils import limpiar_y_normalizar
import nltk
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def limpieza_avanzada(text):
    """
    Limpieza avanzada usando NLTK: tokenización, remoción de stopwords, etc.
    """
    from nltk.corpus import stopwords
    try:
        stopwords.words('spanish')
    except LookupError:
        nltk.download('stopwords')
    tokens = nltk.word_tokenize(text, language='spanish')
    stop_words = set(stopwords.words('spanish'))
    tokens_limpios = [w for w in tokens if w.isalnum() and w not in stop_words]
    return ' '.join(tokens_limpios)

def analizar_sentimiento(text):
    """
    Analiza el sentimiento del texto usando VADER (mejor para inglés, pero útil para ejemplos rápidos).
    Devuelve un diccionario con scores de positividad, negatividad y neutralidad.
    """
    analyzer = SentimentIntensityAnalyzer()
    return analyzer.polarity_scores(text)

def limpiar_texto(text):
    """
    Etapa 1: Limpieza y normalización del texto.
    """
    return limpiar_y_normalizar(text)

# Ejemplo de uso:
# texto = "¡No me gusta nada este dispositivo!"
# print(limpieza_avanzada(texto))
# print(analizar_sentimiento(texto))
