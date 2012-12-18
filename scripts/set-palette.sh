# vim:ft=sh
#------------------------------------------------------
# NAME      INDEX    SOLOARIZED          TANGO
#------------------------------------------------------
# black     0        #073642 (base02)    #2E3436
# red       1        #DC322F (red)       #CC0000
# green     2        #859900 (green)     #4E9A06
# yellow    3        #B58900 (yellow)    #C4A000
# blue      4        #268BD2 (blue)      #3465A4
# magenta   5        #D33682 (magent)    #75507B
# cyan      6        #2AA198 (cyan))     #06989A
# white     7        #EEE8D5 (base2)     #D3D7CF
# brblack   8        #002B36 (base03)    #555753
# brred     9        #CB4B16 (orange)    #EF2929
# brgreen   10       #586E75 (base01)    #8AE234
# bryellow  11       #657B83 (base00)    #FCE94F
# brblue    12       #839496 (base0)     #729FCF
# brmagenta 13       #6C71C4 (violet)    #AD7FA8
# brcyan    14       #93A1A1 (base1)     #34E2E2
# brwhite   15       #FDFDE3 (base3)     #EEEEEC
#------------------------------------------------------

set_palette() { 
    [[ $# != 1 ]] && return

    case $1 in
        tango)
            term_palette=(\
                [0]="#1C1C1C"  [1]="#CC0000"  [2]="#4E9A06"  [3]="#C4A000"  \
                [4]="#3465A4"  [5]="#75507B"  [6]="#06989A"  [7]="#D3D7CF"  \
                [8]="#555753"  [9]="#EF2929"  [10]="#8AE234" [11]="#FCE94F" \
                [12]="#729FCF" [13]="#AD7FA8" [14]="#34E2E2" [15]="#EEEEEC" \
                )
            term_backgournd="#1C1C1C"
            term_foregournd="#8A8A8A"
            term_cursorcolor="#8A8A8A"
            term_palette_name=TANGO
            ;;
        solarized)
            term_palette=(\
                [0]="#073642"  [1]="#DC322F"  [2]="#859900"  [3]="#B58900"  \
                [4]="#268BD2"  [5]="#D33682"  [6]="#2AA198"  [7]="#EEE8D5"  \
                [8]="#002B36"  [9]="#CB4B16"  [10]="#586E75" [11]="#657B83" \
                [12]="#839496" [13]="#6C71C4" [14]="#93A1A1" [15]="#FDF6E3" \
                )
            term_backgournd=${term_palette[8]};
            term_foregournd=${term_palette[11]};
            term_cursorcolor=${term_palette[14]};
            term_palette_name=SOLARIZED
            ;;
        *)
            return
            ;;
    esac

    local red 
    local green  
    local blue
    for i in {0..15}; do
        red=$(($(printf "%d" 0x${term_palette[$i]:1:2}) * 1000 / 255 + 1))
        green=$(($(printf "%d" 0x${term_palette[$i]:3:2}) * 1000 / 255 + 1))
        blue=$(($(printf "%d" 0x${term_palette[$i]:5:2}) * 1000 / 255 + 1))
        tput initc $i $red $green $blue

    done

#    echo -ne "\e]10;${term_foregournd}\e\\"   # Foreground -> base00
#    echo -ne "\e]11;${term_backgournd}\e\\"   # Background -> base03
#    echo -ne "\e]12;${term_cursorcolor}\e\\"  # Cursor -> base1
#
    export TERM_PALETTE=$term_palette_name
}

