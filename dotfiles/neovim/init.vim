call plug#begin('~/.config/nvim/plugged')

function! DoRemote(arg)
    UpdateRemotePlugins
endfunction

Plug 'Shougo/deoplete.nvim', { 'do': function('DoRemote') }
Plug 'zchee/deoplete-clang'
Plug 'zchee/deoplete-jedi'
Plug 'altercation/vim-colors-solarized'
Plug 'vim-airline/vim-airline'


call plug#end()

syntax enable
set sts=4 "softtabstop
set ts=4  "tabstop
set sw=4  "shiftwidth
set et    "xpandtab
set autoindent
set smartindent
set number
set nowrap
set incsearch
set ignorecase
set nobackup
set showmode
set ruler
set splitbelow
set splitright


let g:deoplete#enable_at_startup = 1
let g:deoplete#sources#clang#libclang_path = '/usr/lib/libclang.so'
let g:deoplete#sources#clang#clang_header = '/usr/lib/clang'

if $TERM_PALETTE == 'SOLARIZED'
    set background=dark
    set t_Co=16
    let g:solarized_termcolors=16
    colorscheme solarized
elseif &t_Co == 256
    set background=dark
    let g:solarized_termtrans=0
    let g:solarized_contrast=0
    let g:solarized_termcolors=256
    colorscheme solarized
else
    set background=dark
    colorscheme desert
endif

