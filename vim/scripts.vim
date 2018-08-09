" my filetype file
if getline(1) =~ '^#### Summary'
    setfiletype tsk
endif

