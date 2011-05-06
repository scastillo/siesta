#!/bin/bash

# This is a note for you: Remember that to return 0 is to return a success. Thanks. Bye, see you next script.

source siesta/ext/hooks/utils.sh

BRANCH=$(git branch | grep '*' | cut -d' ' -f2)
COV_TARGET=85
PEP8_COMMAND="pep8 --ignore=E501,E221,E202,E251,W391,W291,E701,W293 --repeat siesta setup.py"
COVERAGE_DIR=siesta/tests/coverage

function clean {
    # Clean artifacts (*.pyc for example)
    for i in $(find . -name '*.pyc')
    do
        rm -f $i
    done
}

function static_checks {
    #First the pylint rate
    pylint . | grep rated
    
    #pep8
    PEP8=$( eval $PEP8_COMMAND | wc -l );
    if [ $PEP8 -gt 0 ]; then
	eval $PEP8_COMMAND
        return 1
    fi

    #pyflakes
    ##exclude __init__.py's from pyflakes so we can import w/o using on modules
    files=$(find . -name "*.py" -not -name "__init__.py")
    if ! pyflakes $files; then
        return 1
    fi
    
}

function unit_tests {
    if ! nosetests .; then
        return 1
    fi
}

function check_coverage {
    # Get coverage
    echo -n "Generating coverage report..."
    coverage html --include="*siesta/*" -d $COVERAGE_DIR
    echo "$(tput setaf 2)Done.$(tput sgr0)"
    coverage report --include="*siesta/*" | grep -v "100%"

    ACTUAL_COVERAGE=$(coverage report --include="*siesta/*" | tail -1 | awk '{print $4}' | sed 's/\%//g')

    if ! (( $ACTUAL_COVERAGE >= $COV_TARGET ));
    then
        echo "Your coverage ($ACTUAL_COVERAGE%) is under $COV_TARGET% goal."
        echo "Check file:///$(pwd)/$COVERAGE_DIR/index.html"
        return 1
    fi
}

function main {
    clean
    if ! static_checks; then error "Static checks broken\nno commit for you."; fi
    if ! unit_tests; then error "Unit tests broken\nno commit for you."; fi
    echo
    if ! check_coverage; then error "Poor coverage\nno commit for you"; fi
    echo "HTML report is at: $(pwd)/$COVERAGE_DIR/index.html"
}

main
