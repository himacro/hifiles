#!/usr/bin/env bash

# Cd the dotfiles dir
cd_dotfiles_dir ()
{
	cd $(dirname $1)
	DOTFILES_DIR=$(pwd)
	echo "Current root direcotry of project 'dotfiles': $DOTFILES_DIR"
}


# Mainline
cd_dotfiles_dir $0

