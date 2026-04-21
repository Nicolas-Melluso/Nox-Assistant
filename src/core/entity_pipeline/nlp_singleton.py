import spacy
from spacy.pipeline import EntityRuler
from ..entity_patterns import patterns

nlp = spacy.load("es_core_news_sm")
if "entity_ruler" not in nlp.pipe_names:
    nlp.add_pipe("entity_ruler", before="ner", config={"phrase_matcher_attr": "LOWER"})
ruler = nlp.get_pipe("entity_ruler")
ruler.add_patterns(patterns)
