/* Counted loops */
do 10
    say 'hello world'
end

/* forever loops 
do forever
    nop
end
*/

/* Control loops */
do c = 1 to 10
    say c
end

do c = 1 to 10 by 2
    say c
end

do c = 1 for 3 by 0.7
    say c
end

/*
do c = 0
    say c
end
*/

/* Conditional loops */
do until ans \= 'NO'
    pull ans
end

do while ans2 = 'NO'
    pull ans2
end

/* Conditional Control loops */
do 3 until ans3 \= 'NO'
    pull ans3
end

do n = 1 to 10 until ans4 == ''
    pull ans4
end

/* leave and iterate */










