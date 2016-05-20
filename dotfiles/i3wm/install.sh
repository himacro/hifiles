#!/usr/bin/env sh

#install the plugin manager plug.vim
I3WM_CONFIG_DIR="$HOME/.config/i3"

#install the startup file
install_init_file() {
    local INIT_FILE_PATH="$I3WM_CONFIG_DIR/config"
    if [ ! -e "$INIT_FILE_PATH" ]; then
	echo 'Linking config...'
	ln -s $(pwd)/config "$INIT_FILE_PATH"
        echo 'Done.'
    else
	echo 'config already installed.'
    fi
}
	
install_init_file

