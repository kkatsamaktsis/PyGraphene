import argparse
import json
import logging
import logging.config

import os
import sys
from enum import Enum, auto
from typing import List

from discoursesimplification.model.simplification_content import SimplificationContent
from stanza.server import CoreNLPClient

from graphene.graphene_core.graphene import Graphene


class Operation(Enum):
    COREF = auto()
    SIM = auto()
    RE = auto()


class OutputSource(Enum):
    CMDLINE = auto()
    FILE = auto()


class InputSource(Enum):
    TEXT = auto()
    FILE = auto()
    WIKI = auto()


class CoreferenceResolutionOutputFormat(Enum):
    DEFAULT = auto()
    SERIALIZED = auto()


class DiscourseSimplificationOutputFormat(Enum):
    DEFAULT = auto()
    DEFAULT_RESOLVED = auto()
    FLAT = auto()
    FLAT_RESOLVED = auto()
    SERIALIZED = auto()


class RelationExtractionOutputFormat(Enum):
    DEFAULT = auto()
    DEFAULT_RESOLVED = auto()
    FLAT = auto()
    FLAT_RESOLVED = auto()
    RDF = auto()
    SERIALIZED = auto()


class Result:
    def __init__(self, name: str, content: SimplificationContent):
        self.name = name
        self.content = content


# Set the logger
logging.config.fileConfig('logging.conf', defaults={'logfilename': './ouput.log', 'logfilemode': 'w'})
logger = logging.getLogger('ROOT')

cli = argparse.ArgumentParser(description='Graphene CLI')

# cli.add_argument('Path',
#                 metavar='path',
#                 type=str,
#                 help='')

cli.add_argument('-op',
                 '--operation',
                 type=str,
                 help='Choose whether to run Coreference-Resolution [COREF], Discourse-Simplification [SIM], or Relation-Extraction [RE].')

cli.add_argument('-is',
                 '--input_source',
                 type=str,
                 help='Choose the input format [TEXT/FILE/WIKI]')

cli.add_argument('-i',
                 '--input',
                 type=str,
                 help='')

cli.add_argument('-out',
                 '--output',
                 type=str,
                 help='Choose whether to create files [FILE] or print result to commandline [CMDLINE].')

cli.add_argument('-simf',
                 '--simformat',
                 type=str,
                 help='Specifies which textual representation for Discourse-Simplification should be returned [DEFAULT/DEFAULT_RESOLVED/FLAT/FLAT_RESOLVED/SERIALIZED].',
                 default=DiscourseSimplificationOutputFormat.DEFAULT)

cli.add_argument('-r',
                 '--reformat',
                 type=str,
                 help='Specifies which textual representation for Relation-Extraction should be returned [DEFAULT/DEFAULT_RESOLVED/FLAT/FLAT_RESOLVED/RDF/SERIALIZED].',
                 default=RelationExtractionOutputFormat.DEFAULT)

cli.add_argument('-dc',
                 '--doCoreference',
                 type=bool,
                 help='Specifies whether coreference should be executed before Discourse-Simplification or Relation-Extraction.',
                 default=False)

cli.add_argument('-isen',
                 '--isolateSentences',
                 type=bool,
                 help='Specifies whether the sentences from the input text should be processed individually (This will not extract relationships that occur between neighboured sentences). Set true, if you run Graphene over a collection of independent sentences and false for a full coherent text.',
                 default=False)

# Parse the input.
args = cli.parse_args()

input_source = InputSource[args.input_source]
operation = Operation[args.operation]
output_source = OutputSource[args.output]
re_output_format = RelationExtractionOutputFormat[args.reformat]
user_input = [str(args.input)]
do_coref = args.doCoreference
isolate_sentences = args.isolateSentences
sim_output_format = args.simformat


def convert_contents(contents) -> List[Result]:
    results = []

    output_name = ""
    output_name += "output_"

    if operation == Operation.COREF:
        output_name += "coref_"
    elif operation == Operation.SIM:
        output_name += "sim_"
        if do_coref:
            output_name += "coref_"
    elif operation == Operation.RE:
        output_name += "re_"
        if do_coref:
            output_name += "coref_"
    else:
        raise AssertionError("Unknown Operation")

    for i in range(0, len(contents)):
        if input_source == InputSource.TEXT:
            output_name += str(i + 1) + str(len(user_input)) + "d"
        elif input_source == InputSource.FILE:
            file_name = os.path.splitext(user_input[i])[0]
            output_name += file_name.replace("\\s+", "-")
        elif input_source == InputSource.WIKI:
            output_name += user_input[i].replace("\\s+", "-")

        results.append((Result(output_name, contents[i])))

    return results


def reformat(content: SimplificationContent) -> str:
    if isinstance(content, SimplificationContent):
        if sim_output_format == DiscourseSimplificationOutputFormat.DEFAULT:
            return content.default_format(False)
        elif sim_output_format == DiscourseSimplificationOutputFormat.DEFAULT_RESOLVED:
            return content.default_format(True)
        elif sim_output_format == DiscourseSimplificationOutputFormat.FLAT:
            return content.flat_format(False)
        elif sim_output_format == DiscourseSimplificationOutputFormat.FLAT_RESOLVED:
            return content.flat_format(True)
        elif sim_output_format == DiscourseSimplificationOutputFormat.SERIALIZED:
            return json.dumps(json.loads(content.serialize_to_json()), indent=4, sort_keys=True)

    return json.dumps(json.loads(content.serialize_to_json()), indent=4, sort_keys=True)


def print_result(result: Result) -> None:
    sb = ""

    sb += "############\n"
    sb += "Name: " + result.name + " →\n"

    try:
        sb += reformat(result.content)
    except TypeError:
        logger.error("Could not convert the result of '{}' to JSON".format(result.name))
        return  # error, we have nothing to print

    print(sb)


def write_result(result: Result) -> None:
    try:
        with open("{}.txt".format(result.name)) as out_file:
            out_file.write(reformat(result.content))
    except IOError:
        logger.error("Could not write file")


def print_or_write_result(contents: List[SimplificationContent]) -> None:
    if len(contents) != len(user_input):
        logger.error("The output length is not the same as the input size: {}:{}".format(len(contents), len(user_input)))

    if output_source == OutputSource.CMDLINE:
        for c in convert_contents(contents):
            print_result(c)
    elif output_source == OutputSource.FILE:
        for c in convert_contents(contents):
            write_result(c)


def read_from_file(filename: str) -> str:
    content = ""

    with open(filename, 'r') as input_file:
        try:
            for line in input_file:
                content = content + line + " "
        except IOError:
            logger.warning("Can't read from file.")

    return content


def get_input(given_inputs: List[str], given_format: InputSource) -> List[str]:
    result = None

    if given_format == InputSource.TEXT:
        result = given_inputs
    elif given_format == InputSource.FILE:
        result = list(map(lambda f: read_from_file(f), given_inputs))
    elif given_format == InputSource.WIKI:
        raise ValueError("This is not (yet) implemented.")

    return result


def do_main():
    # Create CoreNLPClient used in Graphene and Discourse Simplification.
    with CoreNLPClient(
            annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'parse', 'depparse', 'coref'],
            timeout=30000,
            memory='16G',
            be_quiet=True) as client:

        # Init Graphene
        graphene = Graphene(client)

        if input is None or len(user_input) == 0:
            raise ValueError("Input must be at least one entry.")

        input_texts = get_input(user_input, input_source)
        result = None

        if operation == Operation.COREF:
            raise AssertionError("Not implemented yet.")
        elif operation == Operation.SIM:
            result = list(
                map(lambda text: graphene.do_discourse_simplification(text, do_coref, isolate_sentences), input_texts))
        elif operation == Operation.RE:
            raise AssertionError("Not implemented yet.")
        else:
            raise AssertionError("Unknown Operation")

        if result is None:
            raise ValueError("No valid configuration")
        else:
            print_or_write_result(result)


do_main()
