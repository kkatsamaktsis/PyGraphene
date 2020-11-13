from discoursesimplification.model.simplification_content import SimplificationContent


class DiscourseSimplificationContent(SimplificationContent):
    def __init__(self, simplification_content: SimplificationContent):
        super().__init__()
        for out_sentence in simplification_content.sentences:
            self.add_sentence(out_sentence)

        self.coreferenced = False
