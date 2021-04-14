import logging
import importlib

from discoursesimplification.processing.discourse_simplifier import DiscourseSimplifier
from discoursesimplification.processing.processing_type import ProcessingType
from stanza.server import CoreNLPClient

from graphene.config import Config
from graphene.graphene_core.discourse_simplification.discourse_simplification_content import DiscourseSimplificationContent
from graphene import config


class Graphene:
    def __init__(self, client: CoreNLPClient):
        self.logger = logging.getLogger(__name__)

        config.corenlp_client = client
        self.coreference = self.get_coreference_resolver()
        self.discourse_simplification_runner = DiscourseSimplifier(client)
        self.relation_extraction_runner = None  # TODO

        self.logger.info("Graphene initialized")

    def get_coreference_resolver(self):
        coreference_resolver_config = Config.coreference_resolver_config
        class_name = coreference_resolver_config[1]
        coreference_resolver = None

        self.logger.info("Load Coreference-Resolver: '" + class_name + "'")

        coreference_resolver_mod = importlib.import_module("graphene." + coreference_resolver_config[0])
        rule_class_ = getattr(coreference_resolver_mod, class_name)
        coreference_resolver = rule_class_()

        if coreference_resolver is None:
            raise RuntimeError("Fail to initialize CoreferenceResolver: " + class_name)

        return coreference_resolver

    def do_coreference(self, text: str):
        self.logger.debug("doCoreference for text")
        content = self.coreference.do_coreference_resolution(text)
        self.logger.debug("Coreference for text finished")
        return content

    def do_discourse_simplification(self, text: str, do_coreference: bool,
                                    isolate_sentences: bool) -> DiscourseSimplificationContent:
        if do_coreference:
            cc = self.do_coreference(text)
            text = cc.substituted_text()

        self.logger.debug("doDiscourseSimplification for text")
        pt = ProcessingType.SEPARATE if isolate_sentences else ProcessingType.WHOLE
        sc = self.discourse_simplification_runner.do_discourse_simplification_from_string(text, pt)
        dsc = DiscourseSimplificationContent(sc)
        dsc.coreferenced = do_coreference
        self.logger.debug("Discourse Simplification for text finished")
        return dsc

    def do_relation_extraction(self, text: str, do_coreference: bool, isolate_sentences: bool):
        dsc = self.do_discourse_simplification(text, do_coreference, isolate_sentences)

        self.logger.debug("doRelationExtraction for text")
        ec = self.relation_extraction_runner.do_relationExtraction(dsc)
        ec.coreferenced = dsc.coreferenced
        self.logger.debug("Relation Extraction for text finished")
        return ec

    def do_relation_extraction_from_dsc(self, discourse_simplification_content: DiscourseSimplificationContent,
                                        coreferenced: bool):
        self.logger.debug("doRelationExtraction for discourseSimplificationContent")
        ec = self.relation_extraction_runner.do_relation_extraction_from_dsc(discourse_simplification_content)
        ec.coreferenced = discourse_simplification_content.coreferenced
        self.logger.debug("Relation Extraction for discourseSimplificationContent finished")
        return ec
