
" Vim syntax file
" Language:     S/390 Assembler
" Maintainer:   mph
" Last change:  2011 Mar 23
"
" This is incomplete.  
"
" For version 5.x: Clear all syntax items
" For version 6.x: Quit when a syntax file was already loaded
if version < 600
  syntax clear
elseif exists("b:current_syntax")
  finish
endif

syn case ignore


setlocal iskeyword+=@
setlocal iskeyword+=#
setlocal iskeyword+=$

syntax sync match hlasmSyncNonContinue grouphere NONE "\%72c \|\%<73c$"

syntax match hlasmLabel "^[^- ]*\s"me=e-1 nextgroup=hlasmOpcode skipwhite
syntax match hlasmOpcode "\S\+" contained nextgroup=hlasmOperand skipwhite
" syntax match hlasmOperand "\S\+" contained nextgroup=hlasmComment,hlasmContinued skipwhite
syntax region hlasmOperand start="\s\@<=\S" end="\(\%<72c\s\|\%<73c$\|\%72c.\)" oneline contained nextgroup=hlasmComment,hlasmContinued skipwhite
syntax match hlasmOperand "\S\ze\(\%<72c\s\|\%<72c$\|\%72c.\)" contained nextgroup=hlasmComment,hlasmContinued skipwhite
syntax match hlasmComment  "\(\%<72c.\)\+" contained nextgroup=hlasmContinued skipwhite
syntax region hlasmContinued start="\%72c\S" end="\(\%72c\s\)\|\(\%<73c$\)" keepend contained contains=hlasmHeadInContinued
syntax match hlasmHeadInContinued "\(^-\s\+\)\|\(\s\{15}\)" contained nextgroup=hlasmOperand
syntax match hlasmCommentLine "^\.\?\*.*"

syntax match hlasmValue "\(\<[CXFH]\?[L]\)\@<!'[^']*'" contained containedin=hlasmOperand
syntax keyword hlasmReg R0 R1 R2 R3 R4 R5 R6 R7 R8 R9 R10 R11 R12 R13 R14 R15 RA RB RC RD RE RF contained containedin=hlasmOperand
syntax match hlasmOperandPara "\w\+\ze=" contained containedin=hlasmOperand

syn case match

" Define the default highlighting.
" For version 5.7 and earlier: only when not done already
" For version 5.8 and later: only when an item doesn't have highlighting yet
if version >= 508 || !exists("did_hlasm_syntax_inits")
  if version < 508
    let did_hlasm_syntax_inits = 1
    command -nargs=+ HiLink hi link <args>
  else
    command -nargs=+ HiLink hi def link <args>
  endif

  " The default methods for highlighting.  Can be overridden later
  " Comment Constant Error Identifier PreProc Special Statement Todo Type
  "
  " Constant            Boolean Character Number String
  " Identifier          Function
  " PreProc             Define Include Macro PreCondit
  " Special             Debug Delimiter SpecialChar SpecialComment Tag
  " Statement           Conditional Exception Keyword Label Operator Repeat
  " Type                StorageClass Structure Typedef

  HiLink hlasmLabel            Label
  HiLink hlasmOpcode           Macro       
  HiLink hlasmOperand          Normal
  HiLink hlasmCommentLine      Comment
  HiLink hlasmComment          Comment 


  HiLink hexNumber              Number          " Constant
  HiLink decNumber              Number          " Constant
  HiLink binNumber              Number          " Constant
  HiLink chrNumber              Number          " Constant
  HiLink hlasmNum		Number		
  HiLink hlasmStr		Number
  HiLink hlasmStar		Number


  HiLink hlasmReg              Identifier
  HiLink hlasmOperandPara      Special
  HiLink hlasmValue            Constant


  delcommand HiLink
endif

let b:current_syntax = "hlasm"

" vim: ts=8 sw=2



" echo synIDattr(synID(line("."), col("."), 1), "name")
