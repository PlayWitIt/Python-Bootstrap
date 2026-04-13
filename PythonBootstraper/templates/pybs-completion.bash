#!/bin/bash

# Bash completion for pybs
# Install: Save this to /etc/bash_completion.d/pybs or ~/.bash_completion

_pybs_completion() {
    local cur prev words cword
    _init_completion || return

    # Main commands
    local commands="init bootstrap run exec --help --version --force"

    if [[ $cword -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "$commands" -- "$cur") )
        return
    fi

    # Command-specific options
    case "${words[1]}" in
        init|bootstrap|run)
            if [[ "$cur" == -* ]]; then
                COMPREPLY=( $(compgen -W "--dir --force -f --help" -- "$cur") )
            fi
            ;;
        exec)
            if [[ "$cur" == -* ]]; then
                COMPREPLY=( $(compgen -W "--no-venv --help" -- "$cur") )
            fi
            ;;
    esac
}

complete -F _pybs_completion pybs