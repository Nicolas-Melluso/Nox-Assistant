import pandas as pd

# Cargar el dataset
DATASET_PATH = 'training/datasets/raw/intents_p99_template.csv'
df = pd.read_csv(DATASET_PATH, header=None, names=['intent', 'text'])

# Eliminar filas con intención 'intent' (error de encabezado)
df = df[df['intent'] != 'intent']

# Balancear: igualar todas las clases a 150 ejemplos (puedes ajustar este número)
N = 150
balanced = (
    df.groupby('intent', group_keys=False)
    .apply(lambda x: x.sample(N, replace=True) if len(x) < N else x.sample(N, replace=False))
)

# Guardar el dataset balanceado
balanced.to_csv('training/datasets/processed/intents_p99_balanced.csv', index=False, header=False)
print('Dataset balanceado y limpio guardado en training/datasets/processed/intents_p99_balanced.csv')
