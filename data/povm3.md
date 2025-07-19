<!--3out-->
$$M_a = \mu_a\left(\mathbb{I} + \hat{x}_a \cdot \vec{\sigma}\right)\text{, } \sum_a \mu_a = 1\text{, } \sum_a \mu_a \hat{x}_a = 0\text{, } \mu_a \ge 0$$
<!--3outnoisy-->
Noisy POVM:  
$$M_a^{r=\frac{1}{2}} = \mu_a\left(\mathbb{I} + \frac{1}{2} \hat{x}_a \cdot \vec{\sigma}\right)$$
<!--parent-->
Let's use the same parent POVM:  
$$\Pi_{\hat{\lambda}} = \frac{1}{4\pi}\left(\mathbb{I} + \hat{\lambda} \cdot \vec{\sigma}\right)$$
<!--simpleresponce-->
Does a similar response function work?
$$p(a|\{\hat{x}_a\},\hat{\lambda}) = 2\mu_a \Theta(\hat{x}_a\cdot\hat{\lambda})$$
<!--simpleintegral-->
But we can simulate $M_a^{r=\frac{1}{2}}$:
$$\begin{align}\int_S d\hat{\lambda} p(a|\{\hat{x}_a\},\hat{\lambda}) \Pi_{\hat{\lambda}} &= 2\mu_a\frac{1}{4\pi} \int_{\hat{x}_a\cdot\hat{\lambda} >0} d\hat{\lambda} (\mathbb{I} + \hat{\lambda} \cdot \vec{\sigma}) =\\&= 2\mu_a\frac{1}{2}\left(\mathbb{I} + \frac{1}{2} \hat{x}_a \cdot \vec{\sigma}\right) = M_a^{r=\frac{1}{2}}\end{align}$$
<!--simplenormalization-->
This response function is not normalized:  
$$\sum_a p(a|\{\hat{x}_a\},\hat{\lambda}) \neq 1$$
<!--letsfix-->
Let's fix $p(a|\{\hat{x}_a\},\hat{\lambda})$!
<!--6regions-->
6 regions: $A \in \{\{1\}, \{2\}, \{3\}, \{1, 2\}, \{2, 3\}, \{1, 3\}\}$
<!--coarse-->
Integrate $\hat{\lambda}$ over each region $A$:  
$$\Pi_A = \int_S d\hat{\lambda} \prod_{a \in A}\Theta(\hat{x}_a\cdot\hat{\lambda})\prod_{a' \notin A}(1 - \Theta(\hat{x}_{a'}\cdot\hat{\lambda})) \Pi_{\hat{\lambda}}$$
<!--coarse2-->
Integrate $\hat{\lambda}$ over each region $A$:  
$$\Pi_A = \int_S d\hat{\lambda} \quad\text{"1 on the region A"}\quad \Pi_{\hat{\lambda}}$$
<!--coarseexplicit-->
$$\begin{align}\Pi_{\{1\}} &= \frac{\theta_1}{2\pi}(\mathbb{I} - \frac{\pi \sin{\frac{\theta_1}{2}}}{2 \theta_1}\hat{\lambda}_1 \cdot \vec{\sigma})\\\Pi_{\{1\}^c}=\Pi_{\{2, 3\}} &= \frac{\theta_1}{2\pi}(\mathbb{I} + \frac{\pi \sin{\frac{\theta_1}{2}}}{2 \theta_1}\hat{\lambda}_1 \cdot \vec{\sigma})\end{align}$$  
$$\hat{\lambda}_1 = \frac{\hat{x}_2 + \hat{x}_3}{|\hat{x}_2 + \hat{x}_3|}\text{, } \theta_1 = \arccos{(-\hat{x}_2 \cdot \hat{x}_3)}\text{, }\theta_1 + \theta_2 + \theta_3 = \pi$$
<!--coarsesim-->
Coarse-grained POVM:

$$\underbrace{\Pi_{\hat{\lambda}}}_{\substack{\text{parent POVM}\\\text{infinite}}} \xrightarrow{\text{simulates}} \underbrace{\Pi_A}_{\substack{\text{coarse-grained POVM}\\\text{finite}}} \xrightarrow{\text{simulates}} \underbrace{M_a^{r=\frac{1}{2}}}_{\text{target}}$$
<!--responceunnorm-->
Original (unnormalized) response function:

|                       | $\Pi_{\{2,3\}}$ | $\Pi_{\{1,3\}}$ | $\Pi_{\{1,2\}}$ | $\Pi_{\{3\}}$ | $\Pi_{\{2\}}$ | $\Pi_{\{1\}}$ |
|:---------------------:|:---------------:|:---------------:|:---------------:|:-------------:|:-------------:|:-------------:|
| $M_1^{r=\frac{1}{2}}$ |                 |    $2\mu_1$     |    $2\mu_1$     |               |               |   $2\mu_1$    |
| $M_2^{r=\frac{1}{2}}$ |    $2\mu_2$     |                 |    $2\mu_2$     |               |   $2\mu_2$    |               |
| $M_3^{r=\frac{1}{2}}$ |    $2\mu_3$     |    $2\mu_3$     |                 |   $2\mu_3$    |               |               |
<!--responcenorm-->
Modified response function:

|                       | $\Pi_{\{2,3\}}$ | $\Pi_{\{1,3\}}$ | $\Pi_{\{1,2\}}$ | $\Pi_{\{3\}}$ | $\Pi_{\{2\}}$ | $\Pi_{\{1\}}$ |
|:---------------------:|:---------------:|:---------------:|:---------------:|:-------------:|:-------------:|:-------------:|
| $M_1^{r=\frac{1}{2}}$ |                 |    $2\mu_1$     |    $2\mu_1$     |               |               |   $2\mu_1$    |
| $M_2^{r=\frac{1}{2}}$ |  $2\mu_2 - X$   |                 |  $1 - 2\mu_1$   |               |      $1$      |      $Y$      |
| $M_3^{r=\frac{1}{2}}$ |  $2\mu_3 - Y$   |  $1 - 2\mu_1$   |                 |      $1$      |               |      $X$      |

We need $2 \mu_1 + X + Y = 1$, $X \le 2\mu_2$ and $Y \le 2\mu_3$.
<!--simulates-->
Can we find such $X$ and $Y$ to simulate $M_a^{r=\frac{1}{2}}$?
<!--simulatesanswer-->
$$X = \frac{\theta_1(1-2\mu_1) - \theta_2(1-2\mu_2) + \theta_3(1-2\mu_3)}{2\theta_1}$$
$$Y = \frac{\theta_1(1-2\mu_1) + \theta_2(1-2\mu_2) - \theta_3(1-2\mu_3)}{2\theta_1}$$
<!--coarsesimple-->
Coarse-grained POVM:
$$\begin{align}
\Pi_{\{i\}} &= \frac{\theta_i}{2\pi}(\mathbb{I} - \frac{\pi \sin{\frac{\theta_i}{2}}}{2 \theta_i}\hat{\lambda}_i \cdot \vec{\sigma}) &= \frac{\theta_i}{2\pi}\mathbb{I} - \frac{1}{4}\hat{\lambda}'_1 \cdot \vec{\sigma}\\
\Pi_{\{i\}^c} &= \frac{\theta_i}{2\pi}(\mathbb{I} + \frac{\pi \sin{\frac{\theta_i}{2}}}{2 \theta_i}\hat{\lambda}_i \cdot \vec{\sigma}) &= \frac{\theta_i}{2\pi}\mathbb{I} + \frac{1}{4}\hat{\lambda}'_i \cdot \vec{\sigma}\end{align}$$
<!--coarsesimplesim-->
We can simulate $M_a^{r=\frac{1}{2}}$ with unnormalized response function:
$$\begin{align}
2 \mu_1 \Pi_{\{1\}} + 2 \mu_1 \Pi_{\{1, 2\}} + 2 \mu_1 \Pi_{\{1,3\}} &= M_1^{r=\frac{1}{2}} &= \mu_1(\mathbb{I} + \frac{1}{2}\hat{x}_1\cdot\vec{\sigma})\\
2 \mu_2 \Pi_{\{1,2\}} + 2 \mu_2 \Pi_{\{2\}} + 2 \mu_2 \Pi_{\{2,3\}} &= M_2^{r=\frac{1}{2}} &= \mu_2(\mathbb{I} + \frac{1}{2}\hat{x}_2\cdot\vec{\sigma})\\
2 \mu_3 \Pi_{\{1,3\}} + 2 \mu_3 \Pi_{\{2,3\}} + 2 \mu_3 \Pi_{\{3\}} &= M_3^{r=\frac{1}{2}} &= \mu_3(\mathbb{I} + \frac{1}{2}\hat{x}_3\cdot\vec{\sigma})
\end{align}$$
<!--coarsesimplesimsub1-->
We get:
$$\begin{align}
\mu_1\frac{\theta_1 + \theta_2 + \theta_3}{\pi}\mathbb{I} + \frac{\mu_1}{2}(\hat{\lambda}'_2 + \hat{\lambda}'_3 - \hat{\lambda}'_1)\cdot\vec{\sigma} &= \mu_1\mathbb{I} + \frac{\mu_1}{2} \hat{x}_1 \cdot \vec{\sigma}\\
\mu_2\frac{\theta_1 + \theta_2 + \theta_3}{\pi}\mathbb{I} + \frac{\mu_2}{2}(\hat{\lambda}'_1 + \hat{\lambda}'_3 - \hat{\lambda}'_2)\cdot\vec{\sigma} &= \mu_2\mathbb{I} + \frac{\mu_2}{2} \hat{x}_2 \cdot \vec{\sigma}\\
\mu_3\frac{\theta_1 + \theta_2 + \theta_3}{\pi}\mathbb{I} + \frac{\mu_3}{2}(\hat{\lambda}'_1 + \hat{\lambda}'_2 - \hat{\lambda}'_3)\cdot\vec{\sigma} &= \mu_3\mathbb{I} + \frac{\mu_3}{2} \hat{x}_3 \cdot \vec{\sigma}
\end{align}$$
<!--coarsesimplesimsub2-->
We get:
$$\begin{align}
\mu_1(\hat{\lambda}'_2 + \hat{\lambda}'_3 - \hat{\lambda}'_1) &= \mu_1 \hat{x}_1\\
\mu_2(\hat{\lambda}'_1 + \hat{\lambda}'_3 - \hat{\lambda}'_2) &= \mu_2 \hat{x}_2\\
\mu_3(\hat{\lambda}'_1 + \hat{\lambda}'_2 - \hat{\lambda}'_3) &= \mu_3 \hat{x}_3
\end{align}$$
<!--coarsesimplesimsub3-->
$$
(1-2\mu_1)\hat{\lambda}'_1 + (1-2\mu_2)\hat{\lambda}'_2 + (1-2\mu_3)\hat{\lambda}'_3 = \mu_1 \hat{x}_1 + \mu_2 \hat{x}_2 + \mu_3 \hat{x}_3 = 0
$$
<!--coarsesimple2-->
Coarse-grained POVM:
$$
\Pi_{\{i\}} = \frac{\theta_i}{2\pi}\mathbb{I} - \frac{1}{4}\hat{\lambda}'_1 \cdot \vec{\sigma}\text{, }\quad\Pi_{\{i\}^c} = \frac{\theta_i}{2\pi}\mathbb{I} + \frac{1}{4}\hat{\lambda}'_i \cdot \vec{\sigma}
$$
<!--coarseneed1-->
We need to simulate $M_a^{r=\frac{1}{2}}$ with normalized response function:
$$\begin{align}
2 \mu_1 \Pi_{\{1\}} + 2 \mu_1 \Pi_{\{1, 2\}} + 2 \mu_1 \Pi_{\{1,3\}} &= M_1^{r=\frac{1}{2}} &= \mu_1(\mathbb{I} + \frac{1}{2}\hat{x}_1\cdot\vec{\sigma})\\
(1 - 2 \mu_1) \Pi_{\{1,2\}} + \Pi_{\{2\}} + (2 \mu_2 - X) \Pi_{\{2,3\}} + Y \Pi_{\{1\}} &= M_2^{r=\frac{1}{2}} &= \mu_2(\mathbb{I} + \frac{1}{2}\hat{x}_2\cdot\vec{\sigma})\\
(1 - 2\mu_1) \Pi_{\{1,3\}} + (2 \mu_3 - Y) \Pi_{\{2,3\}} + \Pi_{\{3\}} + X \Pi_{\{1\}} &= M_3^{r=\frac{1}{2}} &= \mu_3(\mathbb{I} + \frac{1}{2}\hat{x}_3\cdot\vec{\sigma})
\end{align}$$
<!--coarseneed2-->
We need to simulate $M_2^{r=\frac{1}{2}}$ with normalized response function:
$$
(1 - 2 \mu_1) \Pi_{\{1,2\}} + \Pi_{\{2\}} + (2 \mu_2 - X) \Pi_{\{2,3\}} + Y \Pi_{\{1\}} = \mu_2(\mathbb{I} + \frac{1}{2}\hat{x}_2\cdot\vec{\sigma})
$$
<!--coarseneedi1-->
Coefficients in front of $\mathbb{I}$:
$$
(1 - 2\mu_1)\frac{\theta_3}{2\pi} + \frac{\theta_2}{2\pi} + (2\mu_2 - X)\frac{\theta_1}{2\pi} + Y\frac{\theta_1}{2\pi} = \mu_2
$$
<!--coarseneedi2-->
$$
(1 - 2\mu_1)\theta_3 + \theta_2 + (2\mu_2 - X)\theta_1 + (1 - 2\mu_1 - X)\theta_1 = 2 \mu_2 (\theta_1 + \theta_2 + \theta_3)
$$
<!--coarseneedi3-->
$$\begin{aligned}
X &= \frac{\theta_1(1-2\mu_1) - \theta_2(1-2\mu_2) + \theta_3(1-2\mu_3)}{2\theta_1}\\
Y &= \frac{\theta_1(1-2\mu_1) + \theta_2(1-2\mu_2) - \theta_3(1-2\mu_3)}{2\theta_1}
\end{aligned}$$
<!--coarseneedsigma1-->
Coefficients in front of $\vec{\sigma}$:
$$
(1-2\mu_1)\hat{\lambda}'_3 - \hat{\lambda}'_2 + (2\mu_2 - X) \hat{\lambda}'_1 - Y\hat{\lambda}'_1 = 2\mu_2\hat{x}'_2 
$$
<!--coarseneedsigma2-->
We already know that:
$$
2\mu_2\hat{\lambda}'_3 - 2\mu_2\hat{\lambda}'_2 + 2\mu_2 \hat{\lambda}'_1 = 2\mu_2\hat{x}'_2
$$
<!--coarseneedsigma3-->
Subtracting, we get:
$$
(1-2\mu_1-2\mu_2)\hat{\lambda}'_3 + (2\mu_2-1) \hat{\lambda}'_2 + (-Y - X) \hat{\lambda}'_1 = 0 
$$
<!--coarseneedsigma4-->
Which we can rewrite as:
$$
(2\mu_3-1)\hat{\lambda}'_3 + (2\mu_2-1) \hat{\lambda}'_2 + (2\mu_1-1) \hat{\lambda}'_1 = 0
$$