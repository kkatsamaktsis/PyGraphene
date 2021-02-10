import logging

from graphene.graphene_core.coreference.coreference_resolver import CoreferenceResolver
from graphene.graphene_core.coreference.impl.pycobalt.internal_coreference_request import InternalCoreferenceRequest
from graphene.graphene_core.coreference.impl.pycobalt.internal_coreference_response import InternalCoreferenceResponse
from graphene.graphene_core.coreference.model.coreference_content import CoreferenceContent


class PyCobaltCoref(CoreferenceResolver):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        self.logger.info("Will use remote coreference resource at: '", config.getString("pycobalt.url") + "'")

        web_client = None  # TODO

        self.text_target = None  # TODO

        self.logger.info("Coreference initialized")

    def __send_request(self, target, request: InternalCoreferenceRequest) -> InternalCoreferenceResponse:
        pass  # TODO

    def do_coreference_resolution(self, text: str) -> CoreferenceContent:
        response = self.__send_request(self.text_target, InternalCoreferenceRequest(text))

        return CoreferenceContent(text, response.text)
