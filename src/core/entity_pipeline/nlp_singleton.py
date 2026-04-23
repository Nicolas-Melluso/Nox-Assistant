
import spacy
from spacy.pipeline import EntityRuler
from ..entity_patterns import patterns
import subprocess
import sys

def get_spacy_model(model_name):
    try:
        return spacy.load(model_name)
    except OSError:
        print(f"Modelo spaCy '{model_name}' no encontrado. Instalando automáticamente...")
        subprocess.run([sys.executable, "-m", "spacy", "download", model_name], check=True)
        return spacy.load(model_name)

nlp = get_spacy_model("es_core_news_sm")
if "entity_ruler" not in nlp.pipe_names:
    nlp.add_pipe("entity_ruler", before="ner", config={"phrase_matcher_attr": "LOWER"})
ruler = nlp.get_pipe("entity_ruler")
ruler.add_patterns(patterns)
