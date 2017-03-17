if [ -z "$(which xdotool)" ]; then
    echo "Could not find `xdotool`, have it been installed?"
    exit 1
fi

if [ -z "$1" ]; then
    echo "Title not specified"
    exit 1
fi
TITLE="$1"

if [ -z "$2" ]; then
    if [ -n "$TERMINAL" ]; then
        PROG="$TERMINAL"
    else
        PROG="xterm"
    fi
else
    PROG="$2"
fi

EXEC="$PROG --title $TITLE"
pid=$(xdotool search --name $TITLE)
this_pid=$(xdotool getactivewindow)

if [ -z "$pid" ]; then
    $EXEC &
elif [ "$pid" = "$this_pid" ]; then
    xdotool windowminimize $pid
else
    xdotool windowactivate $pid
fi

