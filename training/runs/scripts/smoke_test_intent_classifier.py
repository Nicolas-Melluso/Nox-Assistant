import joblib

# Cargar el modelo y el vectorizador
clf = joblib.load('models/intent_model.joblib')
vectorizer = joblib.load('training/datasets/processed/intent_vectorizer.joblib')

# Frases de prueba para el smoke test
frases = [
    "Mandá un mensaje a mamá",
    "¿Qué clima hace hoy?",
    "Poné una alarma para las 7",
    "Reproducí música de Queen",
    "Cerrá la aplicación de Spotify",
    "¿Hay tráfico en el centro?",
    "Dame las noticias",
    "¿Qué hora es?",
    "Abrí WhatsApp"
]

# Vectorizar y predecir
X_vec = vectorizer.transform(frases)
preds = clf.predict(X_vec)

# Mostrar resultados
for frase, pred in zip(frases, preds):
    print(f"Frase: '{frase}' => Intento predicho: {pred}")
