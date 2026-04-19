import pandas as pd

# Cargar el dataset
DATASET_PATH = 'training/datasets/raw/intents_p99_template.csv'
df = pd.read_csv(DATASET_PATH, header=None, names=['intent', 'text'])

# Analizar el balance de clases
conteo = df['intent'].value_counts()
print('Cantidad de ejemplos por intención:')
print(conteo)
print('\nTotal de ejemplos:', len(df))
print('\nIntenciones con menos de 50 ejemplos:')
print(conteo[conteo < 50])
