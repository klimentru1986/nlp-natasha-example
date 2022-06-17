from natasha import (
    Doc,
    MorphVocab,
    NamesExtractor,
    AddrExtractor,
    PER,
    LOC,
    Segmenter,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
)

from src.dto.predict_in_dto import PredictInDto


class NlpService:
    def predict(self, predict_dto: PredictInDto):
        doc = Doc(predict_dto.text)

        emb = NewsEmbedding()
        morph_tagger = NewsMorphTagger(emb)
        syntax_parser = NewsSyntaxParser(emb)
        ner_tagger = NewsNERTagger(emb)

        segmenter = Segmenter()
        doc.segment(segmenter)
        doc.tag_morph(morph_tagger)
        doc.parse_syntax(syntax_parser)
        doc.tag_ner(ner_tagger)

        return {
            "names": self._get_names(doc),
            "addr": self._get_addr(doc),
        }

    def _get_names(self, doc: Doc):

        morph_vocab = MorphVocab()
        names_extractor = NamesExtractor(morph_vocab)

        for span in doc.spans:
            span.normalize(morph_vocab)

        for span in doc.spans:
            if span.type == PER:
                span.extract_fact(names_extractor)

        result = [
            {"normal": _.normal, **_.fact.as_dict}
            for _ in doc.spans
            if _.type == PER and _.fact is not None
        ]

        return result

    def _get_addr(self, doc: Doc):

        morph_vocab = MorphVocab()
        addr_extractor = AddrExtractor(morph_vocab)

        loc = [list(addr_extractor(_.text)) for _ in doc.sents]

        result = [[_.fact for _ in l if _.fact] for l in loc if len(l)]

        return result
