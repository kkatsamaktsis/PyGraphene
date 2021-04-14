import logging
from graphene import config

from discoursesimplification.runner.discourse_tree.extraction.rules.coordination_extractor import CoordinationExtractor
from discoursesimplification.runner.discourse_tree.extraction.rules.restrictive_apposition_extractor import RestrictiveAppositionExtractor

from discoursesimplification.model.element import Element


class HeadVerbFinder:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def find_head_verb(self, parse_tree):
        leaf = None  # TODO

        pattern = "ROOT <<: (__ < (VP=vp [ <+(VP) (VP=lowestvp !< VP) | ==(VP=lowestvp !< VP) ]))"
        matches = config.corenlp_client.tregex(leaf.text, pattern)

        return None
