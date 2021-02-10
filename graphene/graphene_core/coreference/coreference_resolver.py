from __future__ import annotations

from graphene.graphene_core.coreference.model.coreference_content import CoreferenceContent


class CoreferenceResolver:
    def __init__(self):
        pass

    def do_coreference_resolution(self, text: str) -> CoreferenceContent:
        pass  # Implemented in subclasses
