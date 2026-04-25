import spacy

from ..entity_patterns import patterns

_NLP = None


def get_spacy_model(model_name: str = "es_core_news_sm"):
    """Load spaCy once, lazily.

    The old implementation attempted to download the model at import time.
    That made imports slow and unpredictable. Missing models now fail with a
    clear runtime error so tests can inject lightweight extractors.
    """
    global _NLP
    if _NLP is not None:
        return _NLP

    try:
        nlp = spacy.load(model_name)
    except OSError as exc:
        raise RuntimeError(
            f"Modelo spaCy '{model_name}' no instalado. Ejecuta: python -m spacy download {model_name}"
        ) from exc

    if "entity_ruler" not in nlp.pipe_names:
        nlp.add_pipe("entity_ruler", before="ner", config={"phrase_matcher_attr": "LOWER"})
    ruler = nlp.get_pipe("entity_ruler")
    if not getattr(ruler, "patterns", None):
        ruler.add_patterns(patterns)

    _NLP = nlp
    return _NLP
