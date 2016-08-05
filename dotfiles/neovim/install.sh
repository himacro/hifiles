#!/usr/bin/env sh

#install the plugin manager plug.vim
NVIM_CONFIG_DIR="$HOME/.config/nvim"

install_plugin_manager() {
    local PLUG_VIM_PATH="$NVIM_CONFIG_DIR/autoload/plug.vim"
    if [ ! -e "$PLUG_VIM_PATH" ]; then
	echo 'Installing plug.vim...'
        curl -fLo "$PLUG_VIM_PATH" --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
        echo 'Done.'
    else
	echo 'plug.vim already installed.'
    fi
}

#install the startup file
install_init_file() {
    local INIT_FILE_PATH="$NVIM_CONFIG_DIR/init.vim"
    if [ ! -e "$INIT_FILE_PATH" ]; then
	echo 'Linking to init.vim...'
	ln -s $(pwd)/init.vim "$INIT_FILE_PATH"
        echo 'Done.'
    else
	echo 'init.vim already installed.'
    fi
}
	
install_plugin_manager
install_init_file

