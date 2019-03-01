*DEVELOPMENT
*PROBLEM SET 3

*QUESTION 3

* Transform string to numbers
encode wave, gen(n_wave)

* Define panel data structure
xtset hh n_wave

*It is unbalanced. Balanced it
by hh: gen count = _N
drop if count == 1
drop count

*Get one value per HH and per year
*collapse (sum) ctotal inctotal, by(hh)

*Aggregate consumption by wave
egen agg_c  = sum(ctotal), by(n_wave)

*Convert to logs
gen log_c=log(ctotal)
gen log_y=log(inctotal)
gen log_C=log(agg_c)

gen d_c=log_c[_n]-log_c[n-1]
gen d_y=log_y[_n]-log_y[n-1]
gen d_C=log_C[_n]-log_C[n-1]

save "/Users/Pau_Belda/Documents/Uni/Màster IDEA/2nd year/Development/PS3/dataUGAA_T.dta"

*Regress
xtreg d_c d_y d_C,fe
est store B


* For urban people
keep if urban==1
xtreg d_c d_y d_C,fe
est store B
esttab B C using table1.tex

*For rural people
use "/Users/Pau_Belda/Documents/Uni/Màster IDEA/2nd year/Development/PS3/dataUGAA_T.dta", clear
keep if urban==0
xtreg d_c d_y d_C,fe
est store D
esttab D using table1.tex, append

