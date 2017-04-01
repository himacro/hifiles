#h!/usr/bin/env bash
GIT=git
SCP=scp
SSH=ssh

last_tree_hash="4b825dc642cb6eb9a060e54bf8d69288fbee4904" #magic hash of empty tree by default
added=''
deleted=''
renamed=''
modified=''

init() {
    # Where I am
    WORKDIR=$(pwd)

    # Find the git repo
    search_git_dir
    ROOTDIR=${GITDIR%.git}

    # data folder for syncz
    DATADIR=$ROOTDIR/'.syncz'
    [ -d "$DATADIR" ] || mkdir "$DATADIR"

    # Read necessary config
    CONFIG=$DATADIR/'config'
    [ -f $CONFIG ] && source $CONFIG  
    if [[ -z "$HOST" || -z "$USER" || -z "$REMOTE_PATH" ]]; then
        echo "Error in config" 
        exit 1
    fi

    HISTORY=$DATADIR/'history'


}

search_git_dir(){
    GITDIR=$($GIT rev-parse --git-dir 2>/dev/null)
    if [ -z "$GITDIR" ]; then
        echo "Fatal: Not in a git repository" 
        exit 1
    fi
    [ "$GITDIR" = ".git" ] && GITDIR=${WORKDIR}/$GITDIR
}

check_changes() {
    get_history

    $GIT add $WORKDIR
    changes=$($GIT diff-tree -r --name-status ${last_tree_hash} $($GIT write-tree))

    local IFS=$'\n'
    for change in $changes; do
        change_type=${change:0:1}
        change_path=${change:2}

        case ${change:0:1} in
        A)
            added=$added'|'${change_path}
            ;;
        D)
            deleted=$deleted'|'${change_path}
            ;;
        M)
            modified=$modified'|'${change_path}
            ;;
        R)
            renamed=$renamed'|'${change_path}
            ;;
        *)
            ;;
        esac
    done

    added=${added:1}
    deleted=${deleted:1}
    renamed=${renamed:1}
    modified=${modified:1}
}

upload() {
    local local_f="$ROOTDIR/$1"
    local remote_f="$USER@$HOST:$REMOTE_PATH/"\"$1\"
    echo "Uploading: $local_f -> $remote_f"
    if ! scp -q $local_f $remote_f 2>/dev/null; then
        new_dir=${1%\/*}
        echo " Making direcotry $new_dir"
        remote_mkdir $new_dir
        echo " Retrying ..."
        scp -q $local_f $remote_f
    fi
}

remote_mkdir() {
    remote_exec mkdir -p "$REMOTE_PATH/"\"$1\"
}

remote_rm() {
    echo "Removing $REMOTE_PATH/\"$1\""
    remote_exec rm "$REMOTE_PATH/"\"$1\"
}

sync_added() {
    local IFS=$'|'
    for f in $added; do
        upload "$f"
    done
}

sync_deleted() {
    local IFS=$'|'
    for f in $deleted; do
        remote_rm "$f"
    done
}

sync_modified() {
    local IFS=$'|'
    for f in $modified; do
        upload "$f"
    done
}

sync_changes() {
    sync_added
    sync_deleted
    sync_modified
    clean_changes
}

get_history() {
    if [ -f $HISTORY ]; then
        last_tree_hash=$(cat $HISTORY)
    fi
}

show_changes() {
    if [[ -z $added && -z $deleted && -z $modified && -z $renamed ]]; then
        echo "No changes!"
        return 0
    fi

    echo "================================"
    local IFS=$'|'
    for f in $added; do
        echo "Added:" $f
    done

    for f in $deleted; do
        echo "Deleted:" $f
    done

    for f in $modified; do
        echo "Modified:" $f
    done

    for f in $renamed; do
        echo "Renamed:" $f
    done
    echo "================================"
    echo ""
}

clean_changes() {
    echo $($GIT write-tree) > $HISTORY
}

remote_exec () {
#    echo $SSH $USER@$HOST $*
    $SSH $USER@$HOST $*
}

reset() {
    echo "Clearing remote directory..."
    remote_exec '[ "$(ls ' "$REMOTE_PATH" ')" ] && rm -r ' $REMOTE_PATH/*
    echo "Clearing local history..."
    [ -f $HISTORY ] && rm $HISTORY
}

usage() {
    echo "Usage:"
    echo "    syncz [reset]"
}


init
if [ $# -gt 1 ]; then
    usage
elif [ $# -eq 0 ]; then
    check_changes 
    show_changes
    sync_changes
elif [ $1 = 'set' ]; then
    clean_changes
elif [ $1 = 'reset' ]; then
    reset
else
    usage
fi

