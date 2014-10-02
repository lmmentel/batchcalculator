
import subprocess
import os

texdata = r'''\documentclass[10pt,a4paper]{article}
% font
\usepackage[scaled]{helvet}
%\usepackage{DejaVuSansCondensed}
\renewcommand*\familydefault{\sfdefault}
\usepackage[T1]{fontenc}
%\usepackage[bitstream-charter]{mathdesign}

\usepackage[utf8]{inputenc}							% Input encoding
\usepackage[english]{babel}								% English language/hyphenation
\usepackage{amsmath,amsfonts}							% Math

\usepackage{xcolor}
\definecolor{bl}{rgb}{0.0,0.2,0.6}

% define mergins
\usepackage[a4paper, left=2cm, right=2cm, top=2cm, bottom=2cm]{geometry}

\usepackage[colorlinks=true]{hyperref}

\usepackage{booktabs}

\usepackage{tabularx} % Better tables
\newcolumntype{C}{>{\centering\arraybackslash}X}
\newcolumntype{L}{>{\raggedright\arraybackslash}X}
\newcolumntype{R}{>{\raggedleft\arraybackslash}X}
\setlength{\extrarowheight}{3pt} % Increase table row height

\usepackage{sectsty}
\usepackage[compact]{titlesec}
\allsectionsfont{\centering\color{bl}\scshape\selectfont}


%% environment for taking notes, takes 3 parameters
%% \notes[add. vertical space]{number lines}{width}
%% number lines: the number of lines to be drawn
%% width: the vertical space occupied by these lines
%% add. vertical space: adds more vertical space between the lines

\usepackage{pgffor, ifthen}
\newcommand{\notes}[3][\empty]{%
    \noindent Notes\vspace{10pt}\\
    \foreach \n in {1,...,#2}{%
        \ifthenelse{\equal{#1}{\empty}}
            {\rule{#3}{0.5pt}\\}
            {\rule{#3}{0.5pt}\vspace{#1}\\}
        }
}

%% small snippet for inserting date
\usepackage{fancybox}
\newcommand{\datefield}{%
\begin{flushright}%
{\color{bl} Date: \Ovalbox{ \begin{minipage}{1.2in} \hfill\vspace{10pt} \end{minipage} }}%
\end{flushright}}

\newcommand{\secwithdate}[1]{\indent {\color{bl}\scshape\bfseries\Large {#1} }\hfill %
{\color{bl} Date: \Ovalbox{ \begin{minipage}{1.2in} \hfill\vspace{10pt} \end{minipage} }} \\}

\newcommand{\subsecwithdate}[1]{\indent {\color{bl}\scshape\bfseries\large {#1} }\hfill %
{\color{bl} Date: \Ovalbox{ \begin{minipage}{1.2in} \hfill\vspace{10pt} \end{minipage} }} \par}

\newcommand{\subsecwodate}[1]{\indent {\color{bl}\scshape\bfseries\large {#1} } \par }

%%%%% Definitions
% Define a new command that prints the title only
\makeatletter							% Begin definition
\def\printtitle{%						% Define command: \printtitle
    {\color{bl} \centering \huge \sc \textbf{\@title}\par}}		% Typesetting
\makeatother							% End definition

\title{Offretite with ZGM ethanol \\ {\large \normalfont 4.8Na$_{2}$O:1.0K$_{2}$O:1.0Al$_{2}$O$_{3}$:15.8SiO$_{2}$:249.5H$_{2}$O:1.0C$_{4}$H$_{12}$NCl:6.0C$_{3}$H$_{7}$OH:15.8C$_{2}$H$_{5}$OH}}

% Define a new command that prints the author(s) only
\makeatletter							% Begin definition
\def\printauthor{%					% Define command: \printauthor
    {\centering \small \@author}}				% Typesetting
\makeatother							% End definition

\author{Katarzyna \L{}ukaszuk \\
\href{mailto:lukaszuk.kasia@gmail.com}{{\color{bl}lukaszuk.kasia@gmail.com}}\\}

% Custom headers and footers
\usepackage{fancyhdr}
	\pagestyle{fancy}					% Enabling the custom headers/footers
\usepackage{lastpage}
	% Header (empty)
	\lhead{}
	\chead{}
	\rhead{22:54:05 28.07.2014}
	% Footer (you may change this to your own needs)
	\lfoot{}
	\cfoot{}
	\rfoot{\footnotesize page \thepage\ of \pageref{LastPage}}	% "Page 1 of 2"
	\renewcommand{\headrulewidth}{0.0pt}
	\renewcommand{\footrulewidth}{0.4pt}

\begin{document}

\printtitle

\printauthor
\section{Batch Composition Calculation}
\subsecwodate{Composition Matrix [C]}
\begin{center}
\begin{tabularx}{\textwidth}{l|RRRRRRRR}\toprule
Formula &\multicolumn{1}{c}{Na$_{2}$O} & \multicolumn{1}{c}{K$_{2}$O} & \multicolumn{1}{c}{Al$_{2}$O$_{3}$} & \multicolumn{1}{c}{SiO$_{2}$} & \multicolumn{1}{c}{H$_{2}$O} & \multicolumn{1}{c}{C$_{4}$H$_{12}$NCl} & \multicolumn{1}{c}{C$_{3}$H$_{7}$OH} & \multicolumn{1}{c}{C$_{2}$H$_{5}$OH}\\ \midrule
Mole ratio &\multicolumn{1}{c}{           4.80} & \multicolumn{1}{c}{           1.00} & \multicolumn{1}{c}{           1.00} & \multicolumn{1}{c}{          15.80} & \multicolumn{1}{c}{         249.50} & \multicolumn{1}{c}{           1.00} & \multicolumn{1}{c}{           6.00} & \multicolumn{1}{c}{          15.80}\\ 
Weight [g] &       297.4989 &         94.1960 &        101.9613 &        949.3319 &       4494.7924 &        109.5985 &        360.5736 &        727.8870\\ 
Mol. wt. [g/mol] &        61.9789 &         94.1960 &        101.9613 &         60.0843 &         18.0152 &        109.5985 &         60.0956 &         46.0688\\ 
\bottomrule\end{tabularx}
\end{center}
\subsecwodate{Batch Matrix [B]}
\begin{center}
\begin{tabularx}{\textwidth}{lCCCCCCCC}\toprule
formula & Na$_{2}$O & K$_{2}$O & Al$_{2}$O$_{3}$ & SiO$_{2}$ & H$_{2}$O & C$_{4}$H$_{12}$NCl & C$_{3}$H$_{7}$OH & C$_{2}$H$_{5}$OH\\ \midrule
KOH(87.0\%) &     0.0000 &     0.7303 &     0.0000 &     0.0000 &     0.2697 &     0.0000 &     0.0000 &     0.0000\\
NaOH(98.0\%) &     0.7593 &     0.0000 &     0.0000 &     0.0000 &     0.2407 &     0.0000 &     0.0000 &     0.0000\\
SiO$_{2}$ &     0.0000 &     0.0000 &     0.0000 &     1.0000 &     0.0000 &     0.0000 &     0.0000 &     0.0000\\
Al(OC$_{3}$H$_{7}$)$_{3}$(98.0\%) &     0.0000 &     0.0000 &     0.2446 &     0.0000 &    -0.1097 &     0.0000 &     0.8650 &     0.0000\\
H$_{2}$O &     0.0000 &     0.0000 &     0.0000 &     0.0000 &     1.0000 &     0.0000 &     0.0000 &     0.0000\\
C$_{4}$H$_{12}$NCl(97.0\%) &     0.0000 &     0.0000 &     0.0000 &     0.0000 &     0.0000 &     1.0000 &     0.0000 &     0.0000\\
C$_{3}$H$_{7}$OH &     0.0000 &     0.0000 &     0.0000 &     0.0000 &     0.0000 &     0.0000 &     1.0000 &     0.0000\\
C$_{2}$H$_{5}$OH &     0.0000 &     0.0000 &     0.0000 &     0.0000 &     0.0000 &     0.0000 &     0.0000 &     1.0000\\
\bottomrule\end{tabularx}
\end{center}
\subsecwodate{Result Matrix [X] = [B]$^{-1}\cdot$[C]}
Scaling factors:\\ \indent main:  60.0842,\\ \indent  to 5g:  10.6650,\\ \indent to 25g:   4.2660\begin{center}
\begin{tabularx}{\textwidth}{lrr|c|RR}\toprule
Substance & \multicolumn{1}{c}{Mass [g]} & Scaled Mass [g] & Weighted mass [g] & Scaled to 10g & Scaled to 25g\\ \midrule
         KOH(87.0\%) &        128.9784 &          2.1466 & &     0.2013 &     0.5032 \\\cline{4-4}
        NaOH(98.0\%) &        391.8080 &          6.5210 & &     0.6114 &     1.5286 \\\cline{4-4}
           SiO$_{2}$ &        949.3319 &         15.8000 & &     1.4815 &     3.7037 \\\cline{4-4}
Al(OC$_{3}$H$_{7}$)$_{3}$(98.0\%) &        416.8258 &          6.9374 & &     0.6505 &     1.6262 \\\cline{4-4}
            H$_{2}$O &       4411.4100 &         73.4205 & &     6.8843 &    17.2107 \\\cline{4-4}
C$_{4}$H$_{12}$NCl(97.0\%) &        109.5985 &          1.8241 & &     0.1710 &     0.4276 \\\cline{4-4}
    C$_{3}$H$_{7}$OH &          0.0000 &          0.0000 & &     0.0000 &     0.0000 \\
\midrule Sum &       6407.9526 &        106.6495 & &         10.0000 &         25.0000\\ \midrule
C$_{2}$H$_{5}$OH&       727.8870&        12.1145 & &          1.1359 &          2.8398\\ 
\bottomrule\end{tabularx}
\end{center}


\newpage
\section{Synthesis}
\begin{center}
\begin{tabularx}{\textwidth}{l|C}
\toprule
Sample name & \\
\midrule
Time & \\ \cline{2-2}
Date & \\ \cline{2-2}
Temperature & \\ \cline{2-2}
Oven & \\ \cline{2-2}
Liner & \\ \cline{2-2}
Autoclave & \\ \cline{2-2}
Drying & \\ \cline{2-2}
Comment & \\
\bottomrule
\end{tabularx}
\end{center}

\subsecwithdate{Calcination I}
\begin{center}
\begin{tabularx}{\textwidth}{l|C|C}
\toprule
Mass [g] & Before calcination & After calcination \\
\midrule
Weighing boat & & \\ \cline{2-3}
Weighing boat + sample & & \\ \cline{2-3}
Sample & & \\
\bottomrule
\end{tabularx}
\end{center}

\subsecwithdate{Ion exchange}
\notes[8pt]{4}{\textwidth}

\subsecwithdate{Calcination II}
\begin{center}
\begin{tabularx}{\textwidth}{l|C|C}
\toprule
Mass [g] & Before calcination & After calcination \\
\midrule
Weighing boat & & \\ \cline{2-3}
Weighing boat + sample & & \\ \cline{2-3}
Sample & & \\
\bottomrule
\end{tabularx}
\end{center}

\section{Analysis}

\indent \subsecwithdate{XRD}
\begin{center}
\begin{tabularx}{\textwidth}{C|C|C}
\toprule
Sample name & Result & Comment \\
\midrule
            &        &         \\
\bottomrule
\end{tabularx}
\end{center}

\subsecwithdate{SEM}
\begin{center}
\begin{tabularx}{\textwidth}{C|C|C|C}
\toprule
Sample name & Aspect ratio & Si/Al & Comment \\
\midrule
            &              &       &   \\
\bottomrule
\end{tabularx}
\end{center}
\end{document}'''


def clean_tex(fname, wrkdir='/tmp'):
    exts = [".out", ".aux", ".log", ".tex"]
    fbase = os.path.splitext(fname)[0]
    for fil in [fbase + ext for ext in exts]:
        if os.path.exists(os.path.join(wrkdir, fil)):
            os.remove(os.path.join(wrkdir, fil))

def which(prog):
    for path in os.getenv('PATH').split(os.path.pathsep):
        fprog = os.path.join(path, prog)
        if os.path.exists(fprog) and os.access(fprog, os.X_OK):
            return fprog
        
def generate_pdf(texstr, fname, wrkdir='/tmp', clean=True):
    os.chdir(wrkdir)
    with open(fname, 'w') as tex:
        tex.write(texstr)
    pdflatex = which('pdflatex')
    print "pdflatex: ", pdflatex
    if pdflatex is not None:
        p = subprocess.Popen([pdflatex, fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if p.returncode == 0 and clean:
            clean_tex(fname)
        else:
            print "something went wrong"
    else:
        print "Could not find pdlfatex"

which('pdflatex')
generate_pdf(texdata, 'test.tex')
