\ProvidesClass{zjureport}
\LoadClass[12pt]{article}
\RequirePackage{xeCJK}
\RequirePackage{CJKnumb}
\RequirePackage{graphicx}
\RequirePackage{geometry}
\RequirePackage{titlesec}
\RequirePackage{fancyhdr}
\RequirePackage{enumitem}
\RequirePackage{listings}
\RequirePackage{xcolor}
\RequirePackage{array}
\RequirePackage{mathtools}
\RequirePackage{float}
\RequirePackage{indentfirst}
\RequirePackage{zhnumber}

\RequirePackage{listings}  % 排版代码用
\RequirePackage{fontspec}  % 调字体的
\setmonofont{Menlo}
\RequirePackage{ulem}      % 删除线、下划线
\RequirePackage{booktabs}  % 画三线表
\RequirePackage{subfigure} 
\RequirePackage{titletoc}  % 调整目录用
\RequirePackage{cite}      % 引用参考文献


\linespread{1.35}
\geometry{top=1in,bottom=1in,left=1in,right=1in}
\setcounter{secnumdepth}{3}
\renewcommand\thesection{\CJKnumber{\arabic{section}}、}
\renewcommand\thesubsection{\arabic{subsection}.}
\renewcommand\thesubsubsection{(\arabic{subsubsection})}
\setlist[enumerate]{label=(\arabic*)}

\setCJKmainfont[AutoFakeBold=true,AutoFakeSlant=0.2]{Songti SC}
\setCJKmonofont{Songti SC}
\setmonofont{Menlo}


% \titleformat{\section}%定义标题类型和标题样式，字体
%   {\fontsize{15.75pt}\textbf\heiti\centering}%定义标题格式:字号（大小），加粗，斜体
%   {}%定义标题的标签，即标题的标号等
%   {0em}%定义标题和标号之间的水平距离
%   {} %定义标题前的内容
%   [] %定义标题后的内容
\titleformat*{\section}{\Large\bfseries}
\titleformat*{\subsection}{\large\bfseries}
\titleformat*{\subsubsection}{\normalsize}
\graphicspath{{figures/}{figure/}{pictures/}
{picture/}{pic/}{pics/}{image/}{images/}}

\titlespacing{\subsection}{1em}{*4}{*1.5}

% 代码格式和颜色定义
\definecolor{dkgreen}{rgb}{0,0.6,0}
\definecolor{gray}{rgb}{0.5,0.5,0.5}
\definecolor{comment}{rgb}{0.56,0.64,0.68}
\lstset{
  frame=tb,
  aboveskip=3mm,
  belowskip=3mm,
  xleftmargin=2em,
  xrightmargin=2em,
  showstringspaces=false,
  columns=flexible,
  framerule=1pt,
  rulecolor=\color{gray!35},
  backgroundcolor=\color{gray!5},
  basicstyle=\small\ttfamily,
  numbers=none,
  numberstyle=\small\color{gray},
  keywordstyle=\color{blue},
  commentstyle=\color{comment},
  stringstyle=\color{dkgreen},
  breaklines=true,
  breakatwhitespace=true,
  tabsize=2,
}

% 信息
\newcommand\major[1]{\def\@major{#1}}
\newcommand\name[1]{\def\@name{#1}}
\newcommand\stuid[1]{\def\@stuid{#1}}
\newcommand\college[1]{\def\@college{#1}}
\renewcommand\date[1]{\def\@date{#1}}
\newcommand\lab[1]{\def\@lab{#1}}
\newcommand\course[1]{\def\@course{#1}}
\newcommand\instructor[1]{\def\@instructor{#1}}
\newcommand\grades[1]{\def\@grades{#1}}
\newcommand\expname[1]{\def\@expname{#1}}
\newcommand\exptype[1]{\def\@exptype{#1}}
\newcommand\partner[1]{\def\@partner{#1}}

\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}} % 我新增加的格式
\newcolumntype{C}[1]{>{\centering\arraybackslash}p{#1}}   % 我新增加的格式
\newcolumntype{R}[1]{>{\raggedleft\arraybackslash}p{#1}}  % 我新增加的格式

% 页眉
\pagestyle{fancy}
\setlength{\headheight}{15pt}
\lhead{实验名称：\@expname}
\chead{}
\rhead{学号：\@stuid}

% 下划线定义
\def\zjuu[#1]#2{
  \underline{\hbox to #1{\hfil#2\hfil}}}

% 首页头部
\newcommand{\makeheader}{
\begin{figure}[h]
  \begin{minipage}{0.62\linewidth}
    \centerline{\includegraphics[width=\linewidth]{head.jpg}}
  \end{minipage}
  \hfill
  \begin{minipage}{.36\linewidth}
    \raggedleft
    \begin{tabular*}{.95\linewidth}{ll}
      专业： & \zjuu[95pt]\@major   \\
      姓名： & \zjuu[95pt]\@name    \\
      学号： & \zjuu[95pt]\@stuid   \\
      日期： & \zjuu[95pt]\@date    \\
      地点： & \zjuu[95pt]\@lab
    \end{tabular*}
  \end{minipage}
\end{figure}

\begin{table}[!htbp]
  \centering
  \scriptsize
  \begin{tabular*}{\linewidth}{llllll}
    课程名称： & \zjuu[120pt]\@course   & 指导老师： & \zjuu[90pt]\@instructor   & 成绩：       &  \zjuu[50pt]\@grades \\
    实验名称： & \zjuu[120pt]\@expname  & 实验类型： & \zjuu[90pt]\@exptype      & 同组学生姓名：&  \zjuu[50pt]\@partner
  \end{tabular*}
\end{table}
\thispagestyle{plain}
\setcounter{page}{1}
}

% 封面
\newcommand{\makecover}{
  \begin{center}
    \begin{center}
      \includegraphics[width=0.68\linewidth]{cover.png}
    \end{center}
    \vspace{0.45cm}
    \bfseries\huge{本科实验报告}\\
    \vspace{0.3cm}
    \bfseries\Large{\@expname}
    \vspace{1.5cm}
    \begin{center}
      \large
      \linespread{1.45}
      \centering
      \renewcommand\arraystretch{1.35}
      \begin{tabular}{L{3cm}C{6cm}}
        \bfseries{课程名称：}  & \@course     \\ \cline{2-2}
        \bfseries{姓名：}     & \@name       \\ \cline{2-2}
        \bfseries{学院：}     & \@college    \\ \cline{2-2}
        \bfseries{专业：}     & \@major      \\ \cline{2-2}
        \bfseries{学号：}     & \@stuid      \\ \cline{2-2}
        \bfseries{指导老师：}  & \@instructor \\ \cline{2-2}
      \end{tabular}
    \end{center}
    \vspace{1cm}
    \Large{\@date}
  \end{center}
  \thispagestyle{empty}
  \newpage
}

% 目录
\newcommand{\makecontent}{
  \thispagestyle{empty}  
  \renewcommand{\contentsname}{\fontsize{20pt}{\baselineskip} \centerline{目\hspace{2em}录}}% 调整目录
  \tableofcontents
  \thispagestyle{empty}
  \newpage
}
