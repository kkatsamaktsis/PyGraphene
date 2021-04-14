import logging


class RelationExtractor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def do_extraction(self, parse_tree):
        pass  # Implemented in subclasses

    def extract(self, parse_tree):
        head_verb = None

        extractions = self.do_extraction(parse_tree)

        return extractions
