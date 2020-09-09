" Plug.vim
if has('win32')
    let s:plugins_dir = '~/AppData/Local/nvim/share/plugged'
else
    let s:plugins_dir = '~/.local/share/nvim/plugged'
endif

 
call plug#begin(s:plugins_dir)
    let s:config_plugins = []
    let s:plugin_entries = {}
    function! s:plug2(...)
        call call('plug#', a:000)
        let l:repo_name = split(a:1, '/')[-1]
        if a:0 == 2 && has_key(a:2, 'entry') 
            let s:plugin_entries[l:repo_name] = a:2['entry'] 
        endif
        call add(s:config_plugins, l:repo_name)
    endfunction

    command! -nargs=+ -bar Plug call <SID>plug2(<args>)

    Plug 'junegunn/seoul256.vim'
    Plug 'editorconfig/editorconfig-vim', {'entry': 'editorconfig'}

    if has('nvim')
        Plug 'neoclide/coc.nvim', {'branch': 'release', 'entry': 'coc'}
        Plug 'jsfaint/gen_tags.vim' , {'entry': 'gen_tags'}
    else
        if has('win32')
            Plug 'Yggdroot/LeaderF', {'do': '.\install.bat', 'entry': 'leaderf' } 
        else
            Plug 'Yggdroot/LeaderF', {'do': './install.sh', 'entry': 'leaderf' } 
        endif

        Plug 'davidhalter/jedi-vim', {'entry': 'jedi'}
    endif
call plug#end()


" My setting
let g:colorschemes = ['seoul256', 'desert']


" Common Settings
"" Editing
set tabstop=4
set softtabstop=4
set shiftwidth=4
set expandtab
set smartindent
set ignorecase
set number
set hidden

"" Keybind
tnoremap <Esc> <C-\><C-n>
tnoremap <A-h> <C-\><C-N><C-w>h
tnoremap <A-j> <C-\><C-N><C-w>j
tnoremap <A-k> <C-\><C-N><C-w>k
tnoremap <A-l> <C-\><C-N><C-w>l
inoremap <A-h> <C-\><C-N><C-w>h
inoremap <A-j> <C-\><C-N><C-w>j
inoremap <A-k> <C-\><C-N><C-w>k
inoremap <A-l> <C-\><C-N><C-w>l
nnoremap <A-h> <C-w>h
nnoremap <A-j> <C-w>j
nnoremap <A-k> <C-w>k
nnoremap <A-l> <C-w>l

"" Python runtime 
if has('win32')
    let g:python3_host_prog = 'c:\scoop\apps\python\current\python.exe'
endif

"" Command
command! -nargs=0 Vimrc :e! $MYVIMRC


" Assist functions
function! s:launch() 
    call s:config_plugins()
    call s:set_colorscheme()
endfunction

function! s:config_plugins()
    for l:plug in s:config_plugins
        call s:config(l:plug)
    endfor
endfunction

function! s:set_colorscheme() 
    if exists('g:colorschemes')
        let l:schemes = g:colorschemes 
    else
        let l:schemes = []
    endif

    for l:scm in l:schemes + ['default']
        if s:has_colorscheme(l:scm)
            call execute(':colorscheme ' . l:scm, 'silent!')
            return l:scm
        endif
    endfor
endfunction

function! s:config(plugin)
    let l:entry = s:has_plugin(a:plugin)
    if len(l:entry) && exists("*s:config__" . l:entry)
        call call("s:config__" . l:entry, [])
"        echo "config__" . l:entry . "()"
    endif
endfunction

function! s:has_plugin(plug)
    let l:plugin_entry = get(s:plugin_entries, a:plug, a:plug)
    if !empty(globpath(&rtp, 'plugin/' . l:plugin_entry . '.vim'))
        return l:plugin_entry
    endif

    if !empty(globpath(&rtp, 'colors/' . l:plugin_entry . '.vim'))
        return l:plugin_entry
    endif

    return ""
endfunction

function! s:has_colorscheme(cs)
    return !empty(globpath(&rtp, 'colors/' . a:cs . '.vim'))
endfunction

function! HasColorScheme(cs)
    return s:has_colorscheme(a:cs)
endfunction

function! HasPlugin(plug)
    return s:has_plugin(a:plug)
endfunction


" gen_tags
function! s:config__gen_tags()
    let $GTAGSLABEL = 'native-pygments'
    if has('win32')
        let $GTAGSCONF = 'c:\ThirdParty\global\share\gtags\gtags.conf'
    else
        let $GTAGSCONF = '/usr/share/gtags/gtags.conf'
    endif

    let g:loaded_gentags#ctags = 1
    let g:gen_tags#gtags_opts = ['-c', '--verbose']
    let g:gen_tags#use_cache_dir = 0
    let g:gen_tags#blacklist = ['$HOME', '$HOME\Projects']
    let g:gen_tags#statusline = 0
    let g:gen_tags#verbose = 0
endfunction

" LeaderF
function! s:config__leaderf() 
    let g:Lf_ShortcutF = '<C-P>'
    let g:Lf_WildIgnore = {
                \ 'dir': ['.git', '.svn', '.hg', '.cvs'],
                \ 'file': ['*.sw?','~$*','*.bak','*.exe','*.o','*.so','*.py[co]']
                \}
    let g:Lf_DefaultExternalTool = 'rg'
    let g:Lf_UseVersionControlTool = 0
endfunction

" jedi-vim
function! s:config__jedi()
    let g:jedi#show_call_signatures = 2
    let g:jedi#show_call_signatures_modes = 'ni'
    autocmd FileType python set splitbelow
    autocmd FileType python set completeopt=menuone,longest
endfunction


" coc
function! s:config__coc()
    set statusline^=%{coc#status()}

    "" Command panel
    nmap <silent> <F1> <Esc>:CocCommand<CR>
    inoremap <silent> <F1> <Esc>:CocCommand<CR>

    "" Code navigation
    nmap <silent> gd <Plug>(coc-definition)
    nmap <silent> gy <Plug>(coc-type-definition)
    nmap <silent> gi <Plug>(coc-implementation)
    nmap <silent> gr <Plug>(coc-references)

    "" Use K to show documentation in preview window
    nnoremap <silent> K :call <SID>coc__show_documenation()<CR>
    nmap <C-P> :CocList files<CR>
    imap <C-P> <ESC>:CocList files<CR>

endfunction

function! s:coc__show_documenation()
    if (index(['vim', 'help'], &filetype) >= 0)
        execute 'h '.expand('<cword>')
    else
        call CocAction('doHover')
    endif
endfunction

" Actual setting
call s:launch()




