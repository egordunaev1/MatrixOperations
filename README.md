# MatrixOperations
Simple plugin for Obsidian.md based on Sympy.

### Setting Up
1. Clone plugin
```
cd /YourObsidianVaultPath/.obsidian/plugins/
git clone https://github.com/egordunaev1/MatrixOperations/
```
2. Install Python (https://www.python.org/)
3. Install Python packages
```
pip3 install sympy, antlr4-python3-runtime
```
4. Install another useful plugin

Go to **Options->Comunity plugins**, turn off **Safe mode**.

Click button "Browse" below, find "Extended MathJax" plugin and download it.

Go to **Options->Comunity plugins**, wind the page down and turn on "Extended MathJax" and "Matrix Operations" plugins.

Create file preamble.sty in the root of your obsidian vault with following commands:
```LaTeX
\newcommand{\matrix}[1]{\begin{bmatrix}#1\end{bmatrix}}
\newcommand{\pmatrix}[1]{\begin{pmatrix}#1\end{pmatrix}}  
\newcommand{\dmatrix}[1]{\left|\begin{array}{}#1\end{array}\right|}
\newcommand{\ematrix}[2]{\left[\begin{array}{}#1\end{array}\right|\left.\begin{array}{}#2\end{array}\right]}

\newcommand{\simop}[1]{\Large\overset{\scriptsize\begin{matrix}#1\end{matrix}}{\sim}\normalsize}
\newcommand{\arrop}[1]{\Large\overset{\scriptsize\begin{matrix}#1\end{matrix}}{\longrightarrow}\normalsize}
\newcommand{\eqop}[1]{\Large\overset{\scriptsize\begin{matrix}#1\end{matrix}}{=}\normalsize}

\newcommand{\lra}{\leftrightarrow}
```

This commands will be preloaded when obsidian loads, so you can use them in LaTeX.

5. Setting up plugin

Go to **Options->Matrix Operations**, this is the plugin settings page.

Write python path in "Python path" field. You can find it out with command "which python3" (Linux, MacOS) or "where python" (Windows).

(Optional) Write path to preamble.sty in "Command file" field if you added other custom commands in preable.sty.


### Commands

This plugin understands only the following matrix declarations:
```LaTeX
\matrix{###MatrixContent###} %matrix with square brackets
\pmatrix{###MatrixContent###} %matrix with round brackets
\dmatrix{###MatrixContent###} %dererminant of matrix, "||" brackets
\ematrix{###MatrixContent1###}{###MatrixContent2###} %two matrices separated by "|".
```

And the following elementary operation commands:
```LaTeX
\simop{###Operations###} %operations with symbol "~"
\arrop{###Operations###} %operations with symbol rightarrow
\eqop{###Operations###} %operations with symbol "="
```

>To write commands select neccecary text and press "Cmd+P"/"Ctrl+P".

**ref** - replaces selected matrix with it's row echelon form.

**rref** - replaces selected matrix with it's reduced row echelon form.

**transpose_matrix** - replaces selected matrix with transposed matrix.

**inverse_matrix** - replaces selected matrix with inverse matrix.

**matrix_info** - shows determinant and rank of selected matrix.

**el_ops** - applies elementary operations listed in one of el. op. commands to matrix and writes it after selection.
```LaTeX
\matrix{
2 & -4 & 5 & 3\\
3 & -6 & 4 & 2\\
4 & -8 & 17 & 11
}
\simop{
(1)+\frac{1}{2}(3)\\ %Adds half of the third row to the first row
(1)\lra(2)\\ %Swaps first and second row
(2col)\cdot 2\cdot\frac{1}{7} %Multiplies 2nd column by 2/7
}
```
<img width="253" alt="изображение" src="https://user-images.githubusercontent.com/56740700/142760143-af29c18d-2179-4e81-b4e9-db5048c12703.png">

**simplify** - simplifies selected expression and replaces the selection with result.

Can additionally transpose matrices with ^T and inverse matrices with ^{-1}:

<img width="397" alt="изображение" src="https://user-images.githubusercontent.com/56740700/142760237-f664ec1b-86b9-4d9a-bf04-da2ae624d2cc.png">




