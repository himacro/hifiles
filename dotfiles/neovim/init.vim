call plug#begin('~/.config/nvim/plugged')

function! DoRemote(arg)
	UpdateRemotePlugins
endfunction

Plug 'Shougo/deoplete.nvim', { 'do': function('DoRemote') }
Plug 'zchee/deoplete-clang'
Plug 'zchee/deoplete-jedi'

call plug#end()

let g:deoplete#enable_at_startup = 1
let g:deoplete#sources#clang#libclang_path = '/usr/lib/libclang.so'
let g:deoplete#sources#clang#clang_header = '/usr/lib/clang'
