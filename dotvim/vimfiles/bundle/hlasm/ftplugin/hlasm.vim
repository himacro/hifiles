" File:          
" Author:        
" Last Updated:  
" Version:       
" Description:   
"
" if exists('loaded_ftplugin_hlasm') || &cp || version < 700
"    finish
" endif

"let loaded_ftplugin_hlasm = 1

" Config lists & dictionaries
let s:lonely_opcodes = [ "CASE","ENDIF","ENDO","ENDCASE","GOLABEL","GOBACK"]
let s:toplvl_opcodes = [ 'GOBASE', 'GOEND', 'GOBACK', 'MSCTITLE' , 'CSECT', 'DSECT' ]
let s:indent_opcodes = { 'IF' : 2, 'DO' : 2, 'CASE' : 4, 'WHEN' : 2, 'ELSE' : 2 }
let s:retract_opcodes = {'ENDIF' : 2, 'ENDO' : 2, 'ENDCASE' : 4, 'WHEN' : 2, 'ELSE' : 2 }

" inoremap <buffer> <CR> <ESC>:call HLASM_Format()<CR>o<ESC>:call HLASM_Tab()<CR>i

" For debugging
if exists('s:stm_funcs') 
   unlet s:stm_funcs
endif


" Functions: HLASM_Xxx()                                             "{{{ 
fun! HLASM_Format(ln)                                                  "{{{
   call setline(a:ln, HLASM_NewStatement(a:ln).format().mkline())
   return ''
endf          
"}}}
fun! HLASM_Tab(ln)                                                     "{{{
    call HLASM_NewStatement(a:ln).tab()
    return ''
endf                                                                 
"}}}
fun! HLASM_Enable()                                                  "{{{
   inoremap <buffer> <Tab> <C-R>=HLASM_Tab(line('.'))<CR>
   nnoremap <buffer> <Tab> :call HLASM_Tab(line('.'))<CR>
   inoremap <buffer> <CR> <CR><C-R>=HLASM_Tab(line('.'))<CR><C-R>=HLASM_Format(line('.')-1)<CR>
"   inoremap <buffer> <CR> <CR><C-R>=HLASM_Format(line('.')-1)<CR>
   nnoremap <buffer> o o<C-R>=HLASM_Format(line('.')-1)<CR>
   nnoremap <buffer> == :call HLASM_Format(line('.'))<CR>
   vnoremap <buffer> = :call HLASM_Format(line('.'))<CR>
endf
"}}}
fun! HLASM_Disable()                                                  "{{{
   iunmap <buffer> <Tab>
   nunmap <buffer> <Tab>
   iunmap <buffer> <CR>
   nunmap <buffer> o
   nunmap <buffer> ==
   vunmap <buffer> =
endf
"}}}
fun! HLASM_NewStatement(linenum)                                     "{{{
   if !exists('s:stm_funcs') 
      let s:stm_funcs = {
               \ 'DUMMY'     : {
               \                'init'   : function('HLASM_Dmy_Init') ,
               \                'show'   : function('HLASM_Dmy_Show') ,
               \                'format' : function('HLASM_Dmy_Format') ,
               \                'indent' : function('HLASM_Dmy_Indent') ,
               \                'mkline' : function('HLASM_Dmy_MakeLine') ,
               \                'tab'    : function('HLASM_Dmy_Tab')
               \               },
               \ 'BLANK'     : {
               \                'init'   : function('HLASM_Dmy_Init') ,
               \                'show'   : function('HLASM_Dmy_Show') ,
               \                'format' : function('HLASM_Dmy_Format') ,
               \                'indent' : function('HLASM_Dmy_Indent') ,
               \                'mkline' : function('HLASM_Dmy_MakeLine') ,
               \                'tab'    : function('HLASM_Blnk_Tab')
               \               },
               \ 'OPERATION' : {
               \                'init'   : function('HLASM_Oprt_Init') ,
               \                'show'   : function('HLASM_Oprt_Show') ,
               \                'format' : function('HLASM_Oprt_Format') ,
               \                'indent' : function('HLASM_Oprt_Indent') ,
               \                'mkline' : function('HLASM_Oprt_MakeLine') ,
               \                'tab'    : function('HLASM_Oprt_Tab') ,
               \                'findent': function('HLASM_Oprt_FollowedIndent') ,
               \               },
               \ 'CONTINUED' : {
               \                'init'   : function('HLASM_Cont_Init') ,
               \                'show'   : function('HLASM_Cont_Show') ,
               \                'format' : function('HLASM_Cont_Format') ,
               \                'indent' : function('HLASM_Cont_Indent') ,
               \                'findent': function('HLASM_Cont_Indent') ,
               \                'mkline' : function('HLASM_Cont_MakeLine') ,
               \                'tab'    : function('HLASM_Cont_Tab'),
               \               },
               \ 'COMMENT'   : {
               \                'init'   : function('HLASM_Cmnt_Init') ,
               \                'show'   : function('HLASM_Cmnt_Show') ,
               \                'format' : function('HLASM_Cmnt_Format') ,
               \                'indent' : function('HLASM_Cmnt_Indent') ,
               \                'mkline' : function('HLASM_Cmnt_MakeLine') ,
               \                'tab'    : function('HLASM_Cmnt_Tab')
               \               }
               \ }
   endif

   let stm = {
            \ 'linenum'  : a:linenum ,
            \ 'did_init' : 0 ,
            \ '_type'    : '' , 
            \ '_subtype' : '' ,
            \ '_indent'  : -1 ,
            \ 'clear'    : function('HLASM_Stm_Clear') ,
            \ 'last'     : function('HLASM_Stm_GetLast') ,
            \ 'type'     : function('HLASM_Stm_GetType') ,
            \ 'subtype'  : function('HLASM_Stm_GetSubtype') 
            \ }

   return extend(stm, get(s:stm_funcs, stm.type()))
endf                                                                 "}}}
"}}} 

" Functions: HLASM_Blnk_Xxx() dict                                   "{{{
fun! HLASM_Blnk_Tab() dict                                           "{{{
   let cur_csr = col(".")

   let last = self
   while 1
      let last = last.last('','')
      let last_type = last.type()
      if last_type == 'OPERATION' 
         if last.contflg.exist()
            let indent = last.indent() + 6
         else
            let indent = last.findent()
         endif
         break
      elseif last_type == 'CONTINUED'
         if last.contflg.exist()
            let indent = last.indent()
         else
            let indent = last.last('OPERATION', '').findent()
         endif
         break
      else
         continue
      endif
   endw

   if last.contflg.exist()
      call setline (self.linenum, '-' . repeat(' ', indent - 1)) 
   else
      call setline (self.linenum, repeat(' ', indent)) 
   endif

   if cur_csr < indent
      let tgt_cur = indent
   else
      let tgt_cur = 1
   endif

   "   let dbgln = string(indent) . ' ' . string(cur_csr) . ' ' . string(tgt_cur) . ' ' . string(col('$'))
   "   call append(".", dbgln)

   call cursor(self.linenum, tgt_cur)
endf                                                                 "}}}
"}}}

" Functions: HLASM_Oprt_Xxx() dict                                   "{{{
fun! HLASM_Oprt_Init() dict                                          "{{{
   if self.did_init
      return 1
   else
      let self.did_init = 1
   endif

   let line = getline(self.linenum)
   let patterns = [ '^\(\S*\s*\)' ,
            \     '\(\S*\s*\)' ,
            \     '\(\%(\%((.*)\)\|\%([^l]\@<=\''[^'']*''\)\|\S\)*\s*\)' ,
            \     '\(.*\%<73c\)' ,
            \     '\(\%(\%72c.\)\?\s*\)' ,
            \     '\(.*\)' ]
   let fields = s:GetFields(line, patterns)
   if empty(fields)  
      return 0
   endif

   let self.label     = fields[0]
   let self.opcode    = fields[1]
   let self.operand   = fields[2]
   let self.comment   = fields[3]
   let self.contflg   = fields[4]
   let self.over72c   = fields[5]

   " Special opcodes without any operands
   if index(s:lonely_opcodes, self.opcode.str) >= 0 && self.operand.str != ','
      let col = self.operand.col
      let str = self.operand.str

      if self.comment.exist()
         let spaces_len = self.comment.col - self.operand.col - self.operand.len()
         let str = str . repeat(' ', spaces_len) . self.comment.str
      endif

      call self.comment.set(col, str)
      call self.operand.clr()
   endif

   let self.subtype = self.opcode.str

   return 1
endf                                                                 "}}}
fun! HLASM_Oprt_Show() dict                                          "{{{
   if !self.did_init
      call self.init()
   endif

   echo self.type()
   echo 'Label:   ' self.label.col   self.label.str
   echo 'Opcode:  ' self.opcode.col  self.opcode.str
   echo 'Operand: ' self.operand.col self.operand.str
   echo 'Comment: ' self.comment.col self.comment.str
   echo 'ContFlg: ' self.contflg.col self.contflg.str
   echo 'Over72c: ' self.over72c.col self.over72c.str
   return
endf                                                                 "}}}
fun! HLASM_Oprt_Indent() dict                                        "{{{
   if !self.did_init
      call self.init()
   endif

   if self._indent <= 0
      if self.opcode.exist()
         if !self.label.exist()
            let indent = self.opcode.col
         elseif self.label.len() + 2 < self.opcode.col
            let indent = self.opcode.col
         elseif index(s:toplvl_opcodes, self.opcode.str) > -1 
            let indent = 10
         else
            let indent = 0
         endif
      else
         let indent = 0
      endif

      if indent == 0
         let last = self.last('OPERATION', '')
         if empty(last)
            let indent = 10
         else
            let indent = last.findent()
         endif
      endif

      let self._indent = indent
   endif

   return self._indent
endf                                                                 "}}}
fun! HLASM_Oprt_FollowedIndent() dict                                "{{{
   if !self.did_init
      call self.init()
   endif

   let indent = self.indent()
   let follow_indent = indent + get(s:indent_opcodes, self.opcode.str)

   return follow_indent
endf                                                                 "}}}
fun! HLASM_Oprt_Format() dict                                        "{{{
   if !self.did_init
      call self.init()
   endif

   " Calculate which column the opcode should start with
   let indent = self.last('OPERATION', '').findent()
   if self.opcode.exist()
      let indent -= get(s:retract_opcodes, self.opcode.str)
   endif
   if self.label.exist()
      let indent = max([indent, self.label.len() + 2])
   endif

   let self.opcode.col = indent
   call self.opcode.setcol(indent)

   " Calculate the operand's column accroding the opcodes
   if self.operand.exist()
      call self.operand.setcol(self.opcode.col + max([6, self.opcode.len() + 1]))
   endif

   " Adjust comment's column, just a temp thinking
   if self.comment.exist()
      if self.operand.exist() 
         let op_right = self.operand.col + self.operand.len() 
      elseif self.opcode.exist()
         let op_right = self.opcode.col + self.opcode.len()
      else
         let op_right = 0
      endif
      call self.comment.setcol(max([op_right + 2, self.comment.col]))
   endif

   " Check if a continued line
   let cont_flag = 0
   if self.contflg.exist()
      let cont_flag = 1
   elseif self.comment.exist() 
      if self.comment.str == '+'
         let cont_flg = 1
         call self.comment.clr()
      else
         let new_comment = matchstr(self.comment.str, '^.*\S\( \++$\)\@=')
         if new_comment != ''
            let cont_flag = 1
            call self.comment.setstr(new_comment)
         endif
      endif
   elseif self.operand.exist() && self.operand.str =~ '^.*\S,$'
      let cont_flag = 1
   endif

   " if a continued operation, set col72 flag
   if !self.contflg.exist() && cont_flag
      call self.contflg.set(72, '+')
   endif

   " last char of operand must be ','
   if self.contflg.exist()
            \ && self.operand.exist()
            \ && self.operand.str !~ '^.\+,$'
      call self.operand.setstr(self.operand.str . ',')
   endif

   return self
endf                                                                 "}}}
fun! HLASM_Oprt_MakeLine() dict                                      "{{{
   let fmt_line = self.label.str
   let fmt_line = fmt_line . repeat(' ', self.opcode.col  - 1 - strlen(fmt_line)) . self.opcode.str
   let fmt_line = fmt_line . repeat(' ', self.operand.col - 1 - strlen(fmt_line)) . self.operand.str
   let fmt_line = fmt_line . repeat(' ', self.comment.col - 1 - strlen(fmt_line)) . self.comment.str
   let fmt_line = fmt_line . repeat(' ', self.contflg.col - 1 - strlen(fmt_line)) . self.contflg.str

   return fmt_line
endf                                                                 "}}}
fun! HLASM_Oprt_Tab() dict                                           "{{{
   if !self.did_init
      call self.init()
   endif

   let cur_csr = col(".") 
   let col_list = [1]
   "call setline(self.linenum, self.format().mkline())

   if self.opcode.exist()
      let opcode_col = self.opcode.col
   else
      let opcode_col = self.last('OPERATION','').findent()
      if self.label.exist()
         let opcode_col = max([opcode_col, self.label.len() + 2])
      endif
   endif
   call add(col_list, opcode_col)

   if self.operand.exist()
      let operand_col = self.operand.col
      call add(col_list, operand_col)
      call add(col_list, 72)
   else
      if self.opcode.exist()
         let operand_col = self.opcode.col + max([6, self.opcode.len() + 1])
         call add(col_list, operand_col)
      endif
   endif

   if self.opcode.exist()
       if self.comment.exist()
           let comment_col = self.comment.col
       elseif self.operand.exist()
           let comment_col = self.operand.col + self.operand.len()
       else
           let comment_col = self.opcode.col + self.opcode.len()
       endif

       let comment_col = max([comment_col, 40])
       call add(col_list, comment_col)
   endif
       

   call sort(col_list)
   let tgt_csr = 0
   for col in col_list
      if cur_csr < col
         let tgt_csr = col
         break
      endif
   endfor
   let tgt_csr = max([tgt_csr, 1])

   let eol = col("$") - 1
   if tgt_csr > eol
      call setline(self.linenum, 
               \ getline(self.linenum) . repeat(' ', tgt_csr - eol))
   endif

   call cursor(self.linenum, tgt_csr)
   return
endf                                                                 "}}}
"}}}

" Functions: HLASM_Cont_Xxx() dict                                   "{{{
fun! HLASM_Cont_Init() dict                                          "{{{
   if self.did_init
      return 1
   else
      let self.did_init = 1
   endif

   let line = getline(self.linenum)
   let patterns = [ '^\(\%(-\s*\)\|\%(\s\{15}\S\@=\)\)' , 
            \    '\(\%(\%(([^(]*)\)\|\%([^l]\@<=\''[^'']*''\)\|\S\)*\s*\)' ,
            \    '\(.*\%<73c\)' ,
            \    '\(\%(\%72c.\)\?\s*\)' ,
            \    '\(.*\)' ]
   let fields = s:GetFields(line, patterns)
   if empty(fields)
      return 0
   endif

   let self.conthdr  = fields[0] 
   let self.operand  = fields[1] 
   let self.comment  = fields[2] 
   let self.contflg  = fields[3] 
   let self.over72c  = fields[4] 


   return 1
endf                                                                 "}}}
fun! HLASM_Cont_Show() dict                                          "{{{
   if !self.did_init
      call self.init()
   endif

   echo 'ContHdr: ' self.conthdr.col self.conthdr.str
   echo 'Operand: ' self.operand.col self.operand.str
   echo 'Comment: ' self.comment.col self.comment.str
   echo 'ContFlg: ' self.contflg.col self.contflg.str
   echo 'Over72c: ' self.over72c.col self.over72c.str

   return
endf                                                                 "}}}
fun! HLASM_Cont_Indent() dict                                        "{{{
   if !self.did_init
      call self.init()
   endif

   if self._indent >= 0 
      return self._indent
   endif

   if self.operand.exist()
      let indent = self.operand.col
   else
      let last = self.last('', '')
      if last.type() == 'OPERATION'
         let indent = last.indent() + 6
      elseif last.type() == 'CONTINUED'
         let indent = last.indent()
      else
         let indent = 16
      endif
   endif

   let self._indent = indent
   return indent
endf                                                                 "}}}
fun! HLASM_Cont_Format() dict                                        "{{{
   if !self.did_init
      call self.init()
   endif

   let last = self.last('', '')
   if last.type() == 'OPERATION'
      let indent = last.indent() + 6
   elseif last.type() == 'CONTINUED'
      let indent = last.indent()
   else
      return self
   endif

   if !self.operand.exist()
      return self
   endif

   call self.operand.setcol(indent)
   let self._indent = indent

   " Adjust comment's column, just a temp thinking
   if self.comment.exist()
      if self.operand.exist()
         let op_right = self.operand.col + self.operand.len()
      else
         let op_right = 0
      endif
      call self.comment.setcol(max([op_right + 2, self.comment.col]))
   endif

   " Check if a continued line
   let cont_flag = 0
   if self.contflg.exist()
      let cont_flag = 1
   elseif self.comment.exist() 
      if self.comment.str == '+'
         let cont_flg = 1
         call self.comment.clr()
      else
         let new_comment = matchstr(self.comment.str, '^.*\S\( \++$\)\@=')
         if new_comment != ''
            let cont_flag = 1
            call self.comment.setstr(new_comment)
         endif
      endif
   elseif self.operand.exist() && self.operand.str =~ '^.*\S,$'
      let cont_flag = 1
   endif

   " if a continued operation, set col72 flag
   if !self.contflg.exist() && cont_flag
      call self.contflg.set(72, '+')
   endif

   " last char of operand must be ','
   if self.contflg.exist()
            \ && self.operand.exist()
            \ && self.operand.str !~ '^.*,$'
      call self.operand.setstr(self.operand.str . ',')
   endif

   return self
endf                                                               
"}}}
fun! HLASM_Cont_MakeLine() dict                                      "{{{
   if !self.did_init
      call self.init()
   endif

   let fmt_line = self.conthdr.str
   let fmt_line = fmt_line . repeat(' ', self.operand.col - 1 - strlen(fmt_line)) . self.operand.str
   let fmt_line = fmt_line . repeat(' ', self.comment.col - 1 - strlen(fmt_line)) . self.comment.str
   let fmt_line = fmt_line . repeat(' ', self.contflg.col - 1 - strlen(fmt_line)) . self.contflg.str

   return fmt_line
endf                                                                 
"}}}
fun! HLASM_Cont_Tab() dict                                           "{{{
   if !self.did_init
      call self.init()
   endif

   let cur_csr = col(".") + 1
   let col_list = [self.indent()]
   " call setline(self.linenum, self.format().mkline())

   if self.operand.exist()
      call add(col_list, 72)
   endif

   call sort(col_list)
   let tgt_csr = 0
   for col in col_list
      if cur_csr < col
         let tgt_csr = col
         break
      endif
   endfor

   if tgt_csr == 0
      let tgt_csr = self.indent()
   endif

   let eol = col("$") - 1
   if tgt_csr > eol
      call setline(self.linenum, 
               \ getline(self.linenum) . repeat(' ', tgt_csr - eol))
   endif

   call cursor(self.linenum, tgt_csr)

   return
endf                                                                 "}}}
"}}}

" Functions: HLASM_Cmnt_Xxx() dict                                   "{{{
fun! HLASM_Cmnt_Init() dict                                          "{{{
   if self.did_init
      return 1
   else
      let self.did_init = 1
   endif

   let line = getline(self.linenum)
   let patterns = ['^\(\%(\*\+[ \.]\+\*\)\|\* *\)\@>',
            \      '\([\*-=]\+\)\%(\*\)\@=',
            \      '\(\%(\*\+\%([^\*]*\)\)\?\)$' ]
   let fields = s:GetFields(line, patterns)
   if !empty(fields)
      let self.subtype = "BORDER"
   else
      let patterns = ['^\(\*\+\%([ \.]\+\*\+\)\? *\)\@>',
               \      '\(.*[^\* ] *\)',
               \      '\(\%(\*\+\%([^\*]*\)\)\?\)$' ]
      let fields = s:GetFields(line, patterns)
      if !empty(fields)
         let self.subtype = 'TEXT'
      else
         return 0
      endif
   endif

   let self.commhdr = fields[0]
   let self.commbdy = fields[1]
   let self.commtai = fields[2]

   return 1
endf                                                                 "}}}
fun! HLASM_Cmnt_Show() dict                                          "{{{
   if !self.did_init
      call self.init()
   endif

   echo self.type()
   echo 'CommHdr: ' self.commhdr.col self.commhdr.str
   echo 'CommBdy: ' self.commbdy.col self.commbdy.str
   echo 'CommTai: ' self.commtai.col self.commtai.str
   return 
endf                                                                 "}}}
fun! HLASM_Cmnt_Indent() dict                                        "{{{
   if !self.did_init
      call self.init()
   endif

   return 0
endf                                                                 "}}}
fun! HLASM_Cmnt_Format() dict                                        "{{{
   if !self.did_init
      call self.init()
   endif

   return self
endf                                                                 "}}}
fun! HLASM_Cmnt_MakeLine() dict                                      "{{{
   if !self.did_init
      call self.init()
   endif

   return getline(self.linenum)
endf                                                                 "}}}
fun! HLASM_Cmnt_Tab() dict                                           "{{{
   return
endf                                                                 "}}}
"}}}

" Functions: HLASM_Dmy_Xxx() dict                                    "{{{
fun! HLASM_Dmy_Init() dict                                           "{{{
   if self.did_init
      return 1
   else
      let self.did_init = 1
   endif

   let self.line = getline(self.linenum)

   return self
endf                                                                 "}}}
fun! HLASM_Dmy_Show() dict                                           "{{{
   if !self.did_init
      call self.init()
   endif

   echo self.mkline()

   return 
endf                                                                 "}}}
fun! HLASM_Dmy_Indent() dict                                         "{{{
   if !self.did_init
      call self.init()
   endif

   return match(self.line, "\(^ *\)\@<=\S") + 1
endf                                                                 "}}}
fun! HLASM_Dmy_Format() dict                                         "{{{
   if !self.did_init
      call self.init()
   endif

   return self
endf                                                                 "}}}
fun! HLASM_Dmy_MakeLine() dict                                       "{{{
   if !self.did_init
      call self.init()
   endif

   return self.line
endf                                                                 "}}}
fun! HLASM_Dmy_Tab() dict                                            "{{{
   return
endf                                                                 "}}}
"}}}

" Functions: HLASM_Stm_Xxx() dict                                    "{{{
fun! HLASM_Stm_Clear() dict                                          "{{{
   let self.linenum = 0
   let self.did_init = 0
   let self._type = ''
   let self._subtype = ''
   return 
endf                                                                 "}}}
fun! HLASM_Stm_GetType() dict                                        "{{{
   if self._type != ''
      return self._type
   endif

   if self.linenum < 1 
      let self._type = 'DUMMY'
   else
      let line = getline(self.linenum)
      if match(line, '^ *$') >= 0
         let self._type = 'BLANK'
      elseif match(line, '^ ') >= 0
         let last72c = getline(self.linenum - 1)[71]
         if last72c == '' || last72c == ' '
            let self._type = 'OPERATION'
         else
            let self._type = 'CONTINUED'
         endif
      elseif match(line,'^\.\?\*') >= 0
         let self._type = 'COMMENT'
      elseif match(line, '^[^-]') >= 0
         let self._type = 'OPERATION'
      elseif match(line, '^-') >= 0
         let self._type = 'CONTINUED'
      else
         let self._type = 'DUMMY'
      endif
   endif

   return self._type
endf                                                                 "}}}
fun! HLASM_Stm_GetSubtype() dict                                     "{{{
   if ! self.did_init
      call self.init()
   endif

   return self._subtype
endf                                                                 "}}}
fun! HLASM_Stm_GetLast(type, subtype) dict                           "{{{
   let ln = self.linenum

   while ln > 1
      let ln -= 1
      let stm = HLASM_NewStatement(ln)
      " echo ln a:type stm.type stm.subtype
      if a:type != '' && a:type != stm.type()
         continue
      endif
      if a:subtype != '' && a:subtype != stm.subtype()
         continue
      endif
      call stm.init()
      return stm
   endw

   return {}
endf                                                                 "}}}
"}}}

" Functions: HLASM_Field_Xxx() dict                                  "{{{
fun! s:GetFields(line, patterns)                                     "{{{
   let fields = []
   let pieces = matchlist(a:line, join(a:patterns, ''))
   if !empty(pieces)
      let col = 1
      for i in range(1, len(a:patterns))
         let fld = { 'col'   : col, 
                  \  'str'   : pieces[i],
                  \  'trim'  : function('s:Field_Trim'),
                  \  'len'   : function('s:Field_GetLen'),
                  \  'exist' : function('s:Field_GetLen'),
                  \  'set'   : function('s:Field_Set'),
                  \  'setstr': function('s:Field_SetStr'),
                  \  'setcol': function('s:Field_SetCol'),
                  \  'clr'   : function('s:Field_Clear')
                  \ }
         call add(fields, fld.trim())
         let col += strlen(pieces[i])
      endfor
   endif

   return fields
endf                                                                 "}}}
fun! s:Field_Trim() dict                                             "{{{
   return self.setstr(matchstr(self.str, '^.*\S\(\s*$\)\@='))
endf                                                                 "}}}
fun! s:Field_GetLen() dict                                           "{{{
   return strlen(self.str)
endf                                                                 "}}}
fun! s:Field_SetStr(str) dict                                        "{{{
   let self.str = a:str
   if !self.len()
      let self.col = 0
   endif
   return self
endf                                                                 "}}}
fun! s:Field_SetCol(col) dict                                        "{{{
   if self.len()
      let self.col = a:col
   endif

   return self
endf                                                                 "}}}
fun! s:Field_Set(col, str) dict                                      "{{{
   return self.setstr(a:str).setcol(a:col)
endf                                                                 "}}}
fun! s:Field_Clear() dict                                            "{{{
   let self.str = ''
   let self.col = 0
endf                                                                 "}}}
"}}}
