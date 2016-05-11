" Vundle {

    filetype off

    set rtp+=~/.config/nvim/bundle/Vundle.vim
    call vundle#begin('~/.config/nvim/bundle')

    " Let Vundle manage Vundle {
        Plugin 'VundleVim/Vundle.vim'
    " }

    " Original repos on github {
        Plugin 'ctrlpvim/ctrlp.vim'
        Plugin 'altercation/vim-colors-solarized'
        Plugin 'Shougo/deoplete.nvim'
        Plugin 'Shougo/neosnippet'
        Plugin 'Shougo/neosnippet-snippets'
        Plugin 'rking/ag.vim'
        Plugin 'scrooloose/nerdtree'
        Plugin 'Lokaltog/vim-easymotion'
        Plugin 'Lokaltog/vim-powerline'
        Plugin 'himacro/hlasm.vim'
    " }

    " vim-scripts repos {
        " Bundle 'L9'
    " }

    " non github repos {
        " Bundle 'git://git.wincent.com/command-t.git'
    " }

    call vundle#end()
    filetype plugin indent on
" }
 
" Core settings {
    let g:python3_host_prog = '/usr/bin/python'
    let g:python_host_prog = '/usr/bin/python'
    let g:jedi#force_py_version = 3
    set encoding=utf-8
    set fileencodings=ucs-bom,utf-8,chinese
    set ambiwidth=double
    set tabstop=4
    set shiftwidth=4
    set softtabstop=4
    set expandtab
    set autoindent
    set smartindent
    set number
    set nowrap
    set incsearch
    set ignorecase
    set backspace=indent,eol,start
    filetype indent plugin on
    syntax enable
    set nobackup
    set showmode
    set ruler
    set helplang=cn
    set foldenable
    set splitbelow
    set splitright
" }

"   
"
" Colorscheme {
    " solarized setting  {
        if !has('gui') 
            set background=dark
            if $TERM_PALETTE == 'SOLARIZED'
                set t_Co=16
                let g:solarized_termcolors=16
                colorscheme solarized
            elseif &t_Co == 256
                let g:solarized_termcolors=256
                colorscheme solarized
            else
                colorscheme desert
            endif
        endif
    " }
" } 

" plugins {
    " PowerLine {
        set laststatus=2
        " let g:Powerline_symbols = 'fancy'
    " } 

    " NERDTree {
        " map <C-e> :NERDTreeToggle<CR>:NERDTreeMirror<CR>
        nnoremap <silent> <leader>ff :NERDTreeToggle<CR>:NERDTreeMirror<CR>
        nnoremap <silent> <leader>fl :NERDTreeFind<CR>
        " map <leader>e :NERDTreeFind<CR>
        " nmap <leader>nt :NERDTreeFind<CR>

        let NERDTreeShowBookmarks=1
        let NERDTreeIgnore=['\.pyc', '\~$', '\.swo$', '\.swp$', '\.git', '\.hg', '\.svn', '\.bzr']
        let NERDTreeChDirMode=0
        let NERDTreeQuitOnOpen=0
        let NERDTreeMouseMode=2
        let NERDTreeShowHidden=1
        let NERDTreeKeepTreeInNewTab=1
        let g:nerdtree_tabs_open_on_gui_startup=0

    " }
     
    " EasyMotion {
    " }
    
    " ctrlp {
    let g:ctrlp_working_path_mode = 'wa'
    " }

" }

" key mapping {
    map <C-H> <C-W>h
    map <C-J> <C-W>j
    map <C-K> <C-W>k
    map <C-L> <C-W>l

    nmap <leader>f0 :set foldlevel=0<CR>
    nmap <leader>f1 :set foldlevel=1<CR>
    nmap <leader>f2 :set foldlevel=2<CR>
    nmap <leader>f3 :set foldlevel=3<CR>
    nmap <leader>f4 :set foldlevel=4<CR>
    nmap <leader>f5 :set foldlevel=5<CR>
    nmap <leader>f6 :set foldlevel=6<CR>
    nmap <leader>f7 :set foldlevel=7<CR>
    nmap <leader>f8 :set foldlevel=8<CR>
    nmap <leader>f9 :set foldlevel=9<CR>
" }

