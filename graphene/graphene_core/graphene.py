import logging

from discoursesimplification.processing.discourse_simplifier import DiscourseSimplifier
from discoursesimplification.processing.processing_type import ProcessingType
from stanza.server import CoreNLPClient

from graphene.graphene_core.discourse_simplification.discourse_simplification_content import DiscourseSimplificationContent


class Graphene:
    def __init__(self, client: CoreNLPClient):
        self.logger = logging.getLogger(__name__)

        self.discourse_simplification_runner = DiscourseSimplifier(client)

        self.logger.info("Graphene initialized")

    def do_discourse_simplification(self, text: str, do_coreference: bool,
                                    isolate_sentences: bool) -> DiscourseSimplificationContent:
        self.logger.debug("doDiscourseSimplification for text")
        pt = ProcessingType.SEPARATE if isolate_sentences else ProcessingType.WHOLE
        sc = self.discourse_simplification_runner.do_discourse_simplification_from_string(text, pt)
        dsc = DiscourseSimplificationContent(sc)
        dsc.coreferenced = do_coreference
        self.logger.debug("Discourse Simplification for text finished")
        return dsc
