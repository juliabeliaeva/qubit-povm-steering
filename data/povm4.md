<!--4out-->
4-outcome POVM:
$$M_a = \mu_a\left(\mathbb{I} + \hat{x}_a \cdot \vec{\sigma}\right)\text{, } \sum_a \mu_a = 1\text{, } \sum_a \mu_a \hat{x}_a = 0\text{, } \mu_a \ge 0$$
<!--4outnoisy-->
Noisy POVM:  
$$M_a^{r=\frac{1}{2}} = \mu_a\left(\mathbb{I} + \frac{1}{2} \hat{x}_a \cdot \vec{\sigma}\right)$$
<!--pseudo1-->
$$\mu_5\hat{x}_{5^+} = -\mu_5\hat{x}_{5^-} = -\mu_1\hat{x}_1 - \mu_2\hat{x}_2 = \mu_3\hat{x}_3 + \mu_4\hat{x}_4$$
<!--pseudo2-->
$$M_{5^\pm}^{r=\frac{1}{2}} = \mu_5\left(\mathbb{I} + \frac{1}{2}\hat{x}_{5^\pm}\cdot \vec{\sigma}\right)$$
<!--povm3-->
Two 3-outcome POVMs:
$$\begin{align}POVM_{+} &= \frac{1}{k_+}\{ M_{5^+}^{r=\frac{1}{2}}, M_{1}^{r=\frac{1}{2}}, M_{2}^{r=\frac{1}{2}} \}\\ POVM_{-} &= \frac{1}{k_-}\{ M_{5^-}^{r=\frac{1}{2}}, M_{3}^{r=\frac{1}{2}}, M_{4}^{r=\frac{1}{2}} \} \end{align}$$
<!--povm3weknow-->
We know how to simulate 3-outcome POVMs!
<!--responsepm-->
Coarse-grained POVMs $\{\Pi^{\pm}_{A_\pm}\}$:

$$
\begin{array}{l}
\Pi^{\pm}_{A_\pm} = \int_S d\hat{\lambda} \prod_{a \in A_{\pm}}\Theta(\hat{x}\cdot\hat{\lambda})\prod_{a \notin A_{\pm}}(1 - \Theta(\hat{x}\cdot\hat{\lambda})) \Pi_{\hat{\lambda}}\\
A_{\pm} \subset O_\pm\text{, where }O_+ =\{5^+, 1, 2\}\text{, }O_+ =\{5^-, 3, 4\}
\end{array}$$

Response function $p_+(a|A_+)$ for $POVM_+$:

|                                        |     $\Pi^+_{\{1,2\}}$      |   $\Pi^+_{\{2,5^+\}}$    |   $\Pi^+_{\{1,5^+\}}$    | $\Pi^+_{\{2\}}$ | $\Pi^+_{\{1\}}$ |  $\Pi^+_{\{5^+\}}$   |
|:--------------------------------------:|:--------------------------:|:------------------------:|:------------------------:|:---------------:|:---------------:|:--------------------:|
| $\frac{1}{k_+}M_{5^+}^{r=\frac{1}{2}}$ |                            |   $\frac{2}{k_+}\mu_5$   |   $\frac{2}{k_+}\mu_5$   |                 |                 | $\frac{2}{k_+}\mu_5$ |
|   $\frac{1}{k_+}M_1^{r=\frac{1}{2}}$   | $\frac{2}{k_+}\mu_1 - X_+$ |                          | $1 - \frac{2}{k_+}\mu_5$ |                 |        1        |        $Y_+$         |
|   $\frac{1}{k_+}M_2^{r=\frac{1}{2}}$   | $\frac{2}{k_+}\mu_2 - Y_+$ | $1 - \frac{2}{k_+}\mu_5$ |                          |        1        |                 |        $X_+$         |

Response function $p_-(a|A_-)$ for $POVM_-$:

|                                        |     $\Pi^-_{\{3,4\}}$      |   $\Pi^-_{\{4,5^-\}}$    |   $\Pi^-_{\{3,5^-\}}$    | $\Pi^-_{\{4\}}$ | $\Pi^-_{\{3\}}$ |  $\Pi^-_{\{5^-\}}$   |
|:--------------------------------------:|:--------------------------:|:------------------------:|:------------------------:|:---------------:|:---------------:|:--------------------:|
| $\frac{1}{k_-}M_{5^-}^{r=\frac{1}{2}}$ |                            |   $\frac{2}{k_-}\mu_5$   |   $\frac{2}{k_-}\mu_5$   |                 |                 | $\frac{2}{k_-}\mu_5$ |
|   $\frac{1}{k_-}M_3^{r=\frac{1}{2}}$   | $\frac{2}{k_-}\mu_3 - X_-$ |                          | $1 - \frac{2}{k_-}\mu_5$ |                 |        1        |        $Y_-$         |
|   $\frac{1}{k_-}M_4^{r=\frac{1}{2}}$   | $\frac{2}{k_-}\mu_4 - Y_-$ | $1 - \frac{2}{k_-}\mu_5$ |                          |        1        |                 |        $X_-$         |