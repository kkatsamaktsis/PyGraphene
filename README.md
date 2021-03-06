# PyGraphene

A translation in python 3.7 of a minimal version of the [Graphene](https://github.com/Lambda-3/Graphene) project.

## Dependencies
  - [python3.7](https://www.python.org/)
  - [discoursesimplification](https://github.com/kkatsamaktsis/PyDiscourseSimplification/)

    For development [PyCharm Community](https://www.jetbrains.com/pycharm/) is recommended

## Setup
    python3.7 setup.py sdist
    pip3.7 install ./dist/graphene-0.0.1.tar.gz


### Run the command line interface
    python3.7 graphene_cli.py --operation SIM --output CMDLINE --reformat DEFAULT --input_source TEXT --input 'We walk, although it rains.' --isolateSentences True

or

    python3.7 graphene_cli.py --operation SIM --output CMDLINE --reformat DEFAULT --input_source FILE --input input.txt --isolateSentences True

## Use as library
Check `graphene_cli.py`. 
    
   
## Author
Konstantinos Katsamaktsis
