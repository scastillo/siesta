function error () {
    # Prints error and exit
    # args:
    #    msg: Message to print on error

    DEFAUL_ERROR="Unexpected error"
    MSG=${1:-$DEFAUL_ERROR}
    echo
    echo -n "$(tput setaf 1)"
    echo -e "Error: $MSG"
    echo -n "$(tput sgr0)"
    exit 1
}
