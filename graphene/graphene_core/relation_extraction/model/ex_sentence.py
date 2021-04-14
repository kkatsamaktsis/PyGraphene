from graphene.graphene_core.relation_extraction.model.extraction import Extraction


class ExSentence:
    def __init__(self, original_sentence: str, sentence_idx: int):
        self.original_sentence = original_sentence
        self.sentence_idx = sentence_idx
        self.extraction_dict = {}

    def contains_extraction(self, extraction: Extraction):
        for e in self.extraction_dict.values():
            if e == extraction:
                return e.id

        return None

    def add_extraction(self, extraction: Extraction):
        if extraction.id not in self.extraction_dict.keys():
            # or self.extraction_dict[extraction.id] is None:
            self.extraction_dict[extraction.id] = extraction

    def get_extraction(self, id: str):
        if id not in self.extraction_dict.keys():
            return None
        else:
            return self.extraction_dict[id]

    def get_extractions(self):
        return list(self.extraction_dict.values())
