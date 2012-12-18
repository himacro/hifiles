let g:lftp_host = 'dvlp'
let g:lftp_user = 'tspxm'
let g:lftp_pass = 'rocket2'
let g:lftp_remote_base = '/u/tspxm/'
let g:lftp_local_base = '/files/myfiles/projects/zos_tspxm/'

fun! s:get_relative_path(local_path)
	let path = 'null'
	let relative_path = "null"
	if a:local_path[0] == '~'
		let path = expand(a:local_path . ":p")
	elseif a:local_path[0] != '/'
		let path = expand(getcwd() . '/' . a:local_path)
	else
		let path = a:local_path
	endif

	let path = resolve(path)
	"echo path
	"echo g:lftp_local_base

	if stridx(path, g:lftp_local_base) == -1
	"	echo 'not found'
		let relative_path = "null"
	else
		let relative_path = strpart(path, strlen(g:lftp_local_base))
"		let relative_path = substitute(a:local_path, g:lftp_local_base, g:lftp_remote_base, "")
	endif

	"echo relative_path
	
	return relative_path
endf

fun! s:scan_buffers()
  let buflist = []
  for i in range(1, bufnr('$') ) 
    if bufexists(i) && buflisted(i) && filereadable(bufname(i))
      cal add( buflist , bufname(i) )
    endif
  endfor
  return buflist
endf

fun! s:auto_mkdir()
	let lftp_cmd = 'null'
	let buffers = s:scan_buffers()
	let lftp_cmds = [ ]
	let script = tempname()
	cal add( lftp_cmds , printf('open -u %s,%s %s' , g:lftp_user ,g:lftp_pass , g:lftp_host ) )
	for f in buffers
		let f = s:get_relative_path(f)	
"		echo f 
		if f != 'null'
			let f = g:lftp_remote_base . f  "s:get_relative_path(f)
			"echo f
			let lftp_cmd = 'mkdir -p ' . matchstr(f, '.*/') 
			if count(lftp_cmds, lftp_cmd) == 0
				cal add(lftp_cmds, lftp_cmd)
			endif
		endif
	endfor
	
	"echo lftp_cmds
	if len(lftp_cmds) > 1
		cal writefile(lftp_cmds, script)
		redraw
		echomsg "Upload:"
		exec '!lftp -f ' . script
	
		cal delete( script )
		echomsg "Done"
	else
		echo 'No valid buffer found'
	endif
endf


	

fun! s:gen_script_buffers(buffers)
  let file = tempname()
  let lines = [ ]
  cal add( lines , printf('open -u %s,%s %s' , g:lftp_user ,g:lftp_pass , g:lftp_host ) )
  cal add( lines , 'set ftp:ssl-allow no')
  "cal add( lines , 'lcd ' . g:lftp_local_base)
  for f in a:buffers
	let f = s:get_relative_path(f)
	if f != 'null'
		cal add( lines , printf('put -a %s -o %s', g:lftp_local_base . f, g:lftp_remote_base . f) )
		"cal add( lines , printf('mput -a -d -O %s %s', g:lftp_remote_base, f) )
	endif
  endfor
  cal writefile( lines , file )
  " echo lines
  return file
endf

func! g:lftp_sync_test()
	let buffers = s:scan_buffers()
	let script = s:gen_script_buffers(buffers)
	return "hello world"
endf


fun! s:gen_config()
  let user = input( "User:" )
  let pass = input( "Pass:" )
  let host = input( "Host:" )
  let lines = []
  cal add(lines , printf( "let g:lftp_user = '%s' " , user ) )
  cal add(lines , printf( "let g:lftp_pass = '%s' " , pass ) )
  cal add(lines , printf( "let g:lftp_host = '%s' " , host ) )
  cal writefile( lines , ".lftp.vim" )
endf

fun! s:read_config()
  if ! filereadable( ".lftp.vim" )
    return
  endif
  source .lftp.vim
endf

fun! s:lftp_sync_buffers()
  cal s:read_config()
  let buffers = s:scan_buffers()
  let script = s:gen_script_buffers(buffers)
  redraw
  echomsg "Upload:"
  "echomsg buffers
  exec '!lftp -f ' . script
  cal delete( script )
  echomsg "Done"
endf

fun! s:lftp_sync_current()
  cal s:read_config()
  w
  let buffers = [ bufname('%') ]
  let script = s:gen_script_buffers(buffers)
  exec '!lftp -f ' . script
  cal delete( script )
endf

fun! s:lftp_console()
  source .lftp.vim
  exec printf('!lftp -u %s,%s %s', g:lftp_user , g:lftp_pass, g:lftp_host )
endf


com! LftpConsole      :cal s:lftp_console()
com! LftpGenConfig    :cal s:gen_config()
com! LftpSyncBuffers  :cal s:lftp_sync_buffers()
com! LftpSyncCurrent  :cal s:lftp_sync_current()
com! LftpAutoMkdir    :cal s:auto_mkdir()
cabbr ftpsb  LftpSyncBuffers
cabbr wf	 LftpSyncCurrent
cabbr wfs	 LftpSyncBuffers


if ! exists( 'g:lftp_sync_no_default_mapping' )
  nnoremap <leader>fu   :LftpSyncBuffers<CR>
  nnoremap <leader>fc   :LftpSyncCurrent<CR>
  nnoremap <leader>ff   :LftpConsole<CR>
endif
