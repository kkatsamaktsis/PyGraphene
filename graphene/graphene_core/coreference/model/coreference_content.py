class CoreferenceContent:
    def __init__(self, original_text: str, substituted_text: str):
        self.original_text = original_text
        self.substituted_text = substituted_text

    def __eq__(self, other) -> bool:
        if (other is not None) and isinstance(other, CoreferenceContent):
            other_content = other

            return self.original_text == other_content.original_text \
                and self.substituted_text == other_content.substituted_text

        return False

    def __str__(self) -> str:
        return "CoreferenceContent{" + "originalText='" + self.original_text \
               + '\'' + ", substitutedText='" + self.substituted_text + '\'' + '}'
