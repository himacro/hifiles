pull a

if a < 50 then
    say a 'is less than 50'

/* if .. else .. */
if a < 50 then 
    say a 'is less than 50'
else
    say a 'is more than 50'

/* Statement block */
if a < 50 then
    do
        say a 'is less than 50'
    end

/* select */
select 
    when a < 50 then
        say a 'is less than 50'
    when a = 50 then
        say a 'is equal to 50'
    when a > 50 then
        say a 'is more than 50'
    otherwise
        nop
end

/* Compare number: =, <, >, <=, >=, <>, \=, \>, \< */
/* Compare string: ==, <<, >>, <<=, >>=, \==, \>>, \<< */


