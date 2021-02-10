import re

from graphene.graphene_core.coreference.coreference_resolver import CoreferenceResolver
from graphene.graphene_core.coreference.model.coreference_content import CoreferenceContent
from graphene import config


class Word:
    def __init__(self, text: str):
        self.text = text
        self.keep = True


class Sentence:
    def __init__(self):
        self.words = []

    def add_word(self, word: str) -> None:
        self.words.append(Word(word))

    def replace_words(self, start_idx: int, end_idx: int, replacement: str):
        for i in range(start_idx, end_idx):
            if i == start_idx:
                self.words[i].text = replacement
            else:
                self.words[i].keep = False

    def __str__(self) -> str:
        words_filtered = list(filter(lambda w: w.keep, self.words))
        return " ".join([w.text for w in words_filtered])

    def __repr__(self):
        return self.__str__()


class StanfordCoref(CoreferenceResolver):
    def __init__(self):
        super().__init__()

    @staticmethod
    def __get_replacement(coref_mention: str, core_mention: str) -> str:
        if bool(re.match(r"his|her", coref_mention.strip().lower())):
            return core_mention + "'s"
        if bool(re.match(r"their|our", coref_mention.strip().lower())):
            return core_mention + "s'"

        return core_mention

    def do_coreference_resolution(self, text: str) -> CoreferenceContent:
        # Annotate text with NLP client:
        document = config.corenlp_client.annotate(text)

        # extract sentences
        sentences = []
        for sent in document.sentence:
            sentence = Sentence()

            for tk in sent.token:
                sentence.add_word(tk.word)

            sentences.append(sentence)

        # replace coreferences
        for mention in document.mentions:
            if mention.entityMentionIndex != mention.canonicalEntityMentionIndex:

                number_of_tokens_up_to_mention_text = 0
                for i in range(0, mention.sentenceIndex):
                    number_of_tokens_up_to_mention_text += len(document.sentence[i].token)

                sentences[mention.sentenceIndex].replace_words(
                    mention.tokenStartInSentenceInclusive - number_of_tokens_up_to_mention_text,
                    mention.tokenEndInSentenceExclusive - number_of_tokens_up_to_mention_text,
                    self.__get_replacement(mention.entityMentionText,
                                           document.mentions[mention.canonicalEntityMentionIndex].entityMentionText)
                )

        return CoreferenceContent(text, " ".join([str(s) for s in sentences]))
