set terminal postscript landscape enhanced color colortext \
   solid dashlength 1.0 linewidth 1.0 defaultplex \
   palfuncparam 2000,0.003 \
   butt "Helvetica" 14
set output 'residual.eps'
set grid xtics nomxtics ytics nomytics noztics nomztics \
 nox2tics nomx2tics noy2tics nomy2tics nocbtics nomcbtics
set logscale x 10
set logscale x2
set logscale y 10
set xlabel "{/Symbol Ds}/{/Symbol s}" 0.000000,0.000000  font ""
set ylabel "F(x_0)/A" 0.000000,0.000000  font ""
set x2label "A/{/Symbol m}"
set x2tics ("10,000" 1e-4,"1,000" 1e-3,"100" 1e-2,"10" 1e-1,"1" 1)
set size square
plot [1e-4:1] (1+2*x-x**2)**( 1/( 1/(2*x)-1/x**2)+1 ) - (1+2*x-x**2)**( 1/( 1/(2*x)-1/x**2) ) t ''
