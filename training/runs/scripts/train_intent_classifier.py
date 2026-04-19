import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report
import joblib

# 1. Cargar el dataset balanceado y asignar nombres a las columnas
DATASET_PATH = 'training/datasets/processed/intents_p99_balanced.csv'
df = pd.read_csv(DATASET_PATH, header=None, names=['intent', 'text'])

# 2. Asumimos que el dataset tiene columnas 'text' (frase) y 'intent' (etiqueta)
X = df['text']
y = df['intent']

# 3. Separar en train y test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Vectorizar el texto
vectorizer = TfidfVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# 5. Entrenar el clasificador
clf = MultinomialNB()
clf.fit(X_train_vec, y_train)

# 6. Evaluar
y_pred = clf.predict(X_test_vec)
print(classification_report(y_test, y_pred))

# 7. Guardar el modelo y el vectorizador (opcional)
joblib.dump(clf, 'models/intent_model.joblib')
joblib.dump(vectorizer, 'training/datasets/processed/intent_vectorizer.joblib')

print('Entrenamiento y guardado del modelo completados.')
