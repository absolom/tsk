:syntax match   tsk_bad_line          "^#.*"
:syntax keyword tsk_section_label     Summary Description    contained
:syntax match   tsk_section_header    "^####.*"   contains=tsk_section_label
:syntax match   tsk_data_section_0    "^>.*$"
:syntax match   tsk_data_section_1    "^>>.*$"
:syntax match   tsk_data_section_2    "^>>>\+.*$"
:syntax match   tsk_data_section_3    "^>>>>\+.*$"

:syntax match   tsk_task_incomplete_anchor  "-" contained
:syntax match   tsk_task_incomplete         "^[ ]*-[a-zA-Z0-9]\+.*$" contains=tsk_task_incomplete_anchor

:syntax match   tsk_task_blocked_anchor  "/" contained
:syntax match   tsk_task_blocked         "^[ ]*/[a-zA-Z0-9]\+.*$" contains=tsk_task_blocked_anchor

:syntax match   tsk_task_complete_anchor  "\*" contained
:syntax match   tsk_task_complete         "^[ ]*\*[a-zA-Z0-9]\+.*$" contains=tsk_task_complete_anchor

:syntax match   tsk_question          "^[ ]*?[a-zA-Z0-9]\+.*$" contains=tsk_question_anchor

:syntax match   tsk_important_anchor   "!"
:syntax match   tsk_important          "^[ ]*![a-zA-Z0-9]\+.*$" contains=tsk_question_anchor

:syntax match   tsk_url                   "https*://[\-a-zA-Z]\+\.[\-a-zA-Z/\.]\+\S*"


:highlight tsk_section_header ctermfg=red term=bold
:highlight tsk_bad_line ctermbg=1 ctermfg=7

":highlight tsk_section_label ctermfg=6 cterm=bold
":highlight tsk_data_section_0 ctermfg=yellow cterm=bold,standout
":highlight tsk_data_section_0 ctermfg=magenta  cterm=bold

":highlight tsk_data_item ctermfg=white cterm=bold

:highlight tsk_data_section_0 ctermfg=white cterm=bold
:highlight tsk_data_section_1 ctermfg=cyan cterm=none
:highlight tsk_data_section_2 ctermfg=darkcyan cterm=none
:highlight tsk_data_section_3 ctermfg=darkcyan cterm=underline

":highlight tsk_task_incomplete ctermfg=blue
":highlight tsk_task_incomplete_anchor ctermfg=blue

:highlight tsk_task_incomplete ctermfg=yellow
:highlight tsk_task_incomplete_anchor ctermbg=none ctermfg=yellow
":highlight tsk_task_incomplete_anchor ctermbg=none ctermfg=black

:highlight tsk_task_blocked ctermfg=darkyellow term=none
:highlight tsk_task_blocked_anchor ctermfg=darkyellow ctermbg=none term=none
":highlight tsk_task_blocked_anchor ctermfg=black ctermbg=none term=none

:highlight tsk_task_complete ctermfg=darkgray term=none
:highlight tsk_task_complete_anchor ctermfg=darkgray term=none
":highlight tsk_task_complete_anchor ctermfg=black term=none

:highlight tsk_question ctermfg=darkred

:highlight tsk_important_anchor ctermfg=none cterm=bold
:highlight tsk_important ctermfg=none cterm=bold

:highlight tsk_url ctermfg=darkgray

