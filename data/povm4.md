<!--4out-->
$$M_a = \mu_a\left(\mathbb{I} + \hat{x}_a \cdot \vec{\sigma}\right)\text{, } \sum_a \mu_a = 1\text{, } \sum_a \mu_a \hat{x}_a = 0\text{, } \mu_a \ge 0$$
<!--4outnoisy-->
Noisy POVM:  
$$M_a^{r=\frac{1}{2}} = \mu_a\left(\mathbb{I} + \frac{1}{2} \hat{x}_a \cdot \vec{\sigma}\right)$$
<!--pseudo1-->
Let's introduce two extra vectors $\hat{x}_{5^+}$ and $\hat{x}_{5^-}$:

$$\mu_5\hat{x}_{5^+} = -\mu_5\hat{x}_{5^-} = -\mu_1\hat{x}_1 - \mu_2\hat{x}_2 = \mu_3\hat{x}_3 + \mu_4\hat{x}_4$$
<!--povm3-->
Two 3-outcome POVMs:

$$\begin{align}\operatorname{POVM}_{+} &= \frac{1}{k_+}\{ M_{5^+}^{r=\frac{1}{2}}, M_{1}^{r=\frac{1}{2}}, M_{2}^{r=\frac{1}{2}} \}\\ \operatorname{POVM}_{-} &= \frac{1}{k_-}\{ M_{5^-}^{r=\frac{1}{2}}, M_{3}^{r=\frac{1}{2}}, M_{4}^{r=\frac{1}{2}} \}\end{align}$$
<!--pseudo2-->
where  

$$\begin{aligned}M_{5^\pm}^{r=\frac{1}{2}} &= \mu_5\left(\mathbb{I} + \frac{1}{2}\hat{x}_{5^\pm}\cdot \vec{\sigma}\right)\\k_+ &= \mu1 + \mu2 + \mu5\\\quad k_- &= \mu3 + \mu4 + \mu5\\\end{aligned}$$
<!--povm3weknow-->
We know how to simulate 3-outcome POVMs!
<!--responsepm-->
Coarse-grained POVMs $\{\Pi^{\pm}_{A_\pm}\}$:
$$\begin{array}{l}
\Pi^{\pm}_{A_\pm} = \int_S d\hat{\lambda} \prod_{a \in A_{\pm}}\Theta(\hat{x}_a\cdot\hat{\lambda})\prod_{a \notin A_{\pm}}(1 - \Theta(\hat{x}_a\cdot\hat{\lambda})) \Pi_{\hat{\lambda}}\\
A_{\pm} \subset O_\pm\text{, where }O_+ =\{5^+, 1, 2\}\text{, }O_+ =\{5^-, 3, 4\}
\end{array}$$

Response function $p_+(a|A_+)$ for $\operatorname{POVM}_+$:

|                                        |     $\Pi^+_{\{1,2\}}$      |   $\Pi^+_{\{2,5^+\}}$    |   $\Pi^+_{\{1,5^+\}}$    | $\Pi^+_{\{2\}}$ | $\Pi^+_{\{1\}}$ |  $\Pi^+_{\{5^+\}}$   |
|:--------------------------------------:|:--------------------------:|:------------------------:|:------------------------:|:---------------:|:---------------:|:--------------------:|
| $\frac{1}{k_+}M_{5^+}^{r=\frac{1}{2}}$ |                            |   $\frac{2}{k_+}\mu_5$   |   $\frac{2}{k_+}\mu_5$   |                 |                 | $\frac{2}{k_+}\mu_5$ |
|   $\frac{1}{k_+}M_1^{r=\frac{1}{2}}$   | $\frac{2}{k_+}\mu_1 - X_+$ |                          | $1 - \frac{2}{k_+}\mu_5$ |                 |       $1$       |        $Y_+$         |
|   $\frac{1}{k_+}M_2^{r=\frac{1}{2}}$   | $\frac{2}{k_+}\mu_2 - Y_+$ | $1 - \frac{2}{k_+}\mu_5$ |                          |       $1$       |                 |        $X_+$         |

Response function $p_-(a|A_-)$ for $\operatorname{POVM}_-$:

|                                        |     $\Pi^-_{\{3,4\}}$      |   $\Pi^-_{\{4,5^-\}}$    |   $\Pi^-_{\{3,5^-\}}$    | $\Pi^-_{\{4\}}$ | $\Pi^-_{\{3\}}$ |  $\Pi^-_{\{5^-\}}$   |
|:--------------------------------------:|:--------------------------:|:------------------------:|:------------------------:|:---------------:|:---------------:|:--------------------:|
| $\frac{1}{k_-}M_{5^-}^{r=\frac{1}{2}}$ |                            |   $\frac{2}{k_-}\mu_5$   |   $\frac{2}{k_-}\mu_5$   |                 |                 | $\frac{2}{k_-}\mu_5$ |
|   $\frac{1}{k_-}M_3^{r=\frac{1}{2}}$   | $\frac{2}{k_-}\mu_3 - X_-$ |                          | $1 - \frac{2}{k_-}\mu_5$ |                 |       $1$       |        $Y_-$         |
|   $\frac{1}{k_-}M_4^{r=\frac{1}{2}}$   | $\frac{2}{k_-}\mu_4 - Y_-$ | $1 - \frac{2}{k_-}\mu_5$ |                          |       $1$       |                 |        $X_-$         |
<!--18regions-->
$$\Pi_{A} = \int_S d\hat{\lambda} \prod_{a \in A}\Theta(\hat{x}_a\cdot\hat{\lambda})\prod_{a \notin A}(1 - \Theta(\hat{x}_a\cdot\hat{\lambda})) \Pi_{\hat{\lambda}}$$

where $A = A_+ \cap A_-$ is one of 18 regions
<!--18regionssim-->
Let's simulate $M_1^{r=\frac{1}{2}}$!
<!--18regionssim2-->
$M_1^{r=\frac{1}{2}}$ was in $\operatorname{POVM}_+$, so we can simulate it using $\Pi^+$:
$$\begin{multline}M_1^{r=\frac{1}{2}} = k_+ \sum_{A_+ \subset \{5^+, 1, 2\} } p_+(1|A_+) \Pi^+_{A_+} = \\ = k_+ (\frac{2}{k_+}\mu_1 - X_+) \Pi^+_{\{1,2\}} + (1 - \frac{2}{k_+}\mu_5)) \Pi^+_{\{1,5^+\}}  + \\ + \Pi^+_{\{1\}} + Y_+ \Pi^+_{\{5^+\}})\end{multline}$$
<!--18regionssim3-->
And then express $\Pi^+$ using $\Pi_{A}$:
$$\begin{aligned}
\Pi^+_{\{1,2\}} &=  \Pi_{\{1,2,5−\}} + \Pi_{\{1,2,3,5−\}} + \Pi_{\{1,2,4,5−\}} \\
\Pi^+_{\{1,5^+\}} &= \Pi_{\{1,3,5+\}} + \Pi_{\{1,4,5+\}} + \Pi_{\{1,3,4,5+\}}\\
\Pi^+_{\{1\}} &= \Pi_{\{1,5−\}} + \Pi_{\{1,4,5−\}} + \Pi_{\{1,3,5−\}}\\
\Pi^+_{\{5^+\}} &= \Pi_{\{4,5+\}} + \Pi_{\{3,5+\}} + \Pi_{\{3,4,5+\}}
\end{aligned}$$
<!--18regionssim4-->
$$\begin{aligned}M_1^{r=\frac{1}{2}} &= \sum_{A} p(1|A) \Pi_{A}\\p(1|A) &= k_+ p_+(1|A_+)\text{,}A = A_+ \cap A_-\end{aligned}$$
<!--18regionssimall-->
Response function for $A = A_+ \cap A_-$:
$$\begin{aligned}p(1|A) &= k_+ p_+(1|A_+) & p(2|A) &= k_+ p_+(2|A_+)\\p(3|A) &= k_- p_-(3|A_-) & p(4|A) &= k_- p_-(4|A_-)\end{aligned}$$
<!--18regionsnorm1-->
Let's check normalization:
$$\begin{multline}\sum_{a=1}^4 p(a|A) = k_+ p_+(1|A_+) + k_+ p_+(2|A_+) + \\ + k_- p_-(3|A_-) + k_- p_-(4|A_-)\end{multline}$$
<!--18regionsnorm2-->
Let's check normalization:
$$\begin{multline}\sum_{a=1}^4 p(a|A) = k_+ p_+(1|A_+) + k_+ p_+(2|A_+)  + \\ + k_- p_-(3|A_-) + k_- p_-(4|A_-) = \\ = k_+(1 - p_+(5^+|A_+)) + k_-(1 - p_-(5^-|A_-))\end{multline}$$
<!--18regionsnorm3-->
Let's check normalization:
$$\begin{multline}\sum_{a=1}^4 p(a|A) = k_+ p_+(1|A_+) + k_+ p_+(2|A_+) + \\ + k_- p_-(3|A_-) + k_- p_-(4|A_-) = \\ = k_+(1 - p_+(5^+|A_+)) + k_-(1 - p_-(5^-|A_-)) = \\ = k_+ + k_- - 2\mu_5 = \mu_1 + \mu_2 + \mu_5 + \\ + \mu_3 + \mu_4 + \mu_5 - 2\mu_5 = 1\end{multline}$$