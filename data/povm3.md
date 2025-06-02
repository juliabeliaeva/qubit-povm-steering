<!--3out-->
3-outcome POVM:
$$M_a = \mu_a\left(\mathbb{I} + \hat{x}_a \cdot \vec{\sigma}\right)\text{, } \sum_a \mu_a = 1\text{, } \sum_a \mu_a \hat{x}_a = 0\text{, } \mu_a \ge 0$$
<!--3outnoisy-->
Noisy POVM:  
$$M_a^{r=\frac{1}{2}} = \mu_a\left(\mathbb{I} + \frac{1}{2} \hat{x}_a \cdot \vec{\sigma}\right)$$
<!--parent-->
Same parent POVM:  
$$\Pi_{\hat{\lambda}} = \frac{1}{4\pi}\left(\mathbb{I} + \hat{\lambda} \cdot \vec{\sigma}\right)$$
<!--simpleresponce-->
Does a similar response function work?
$$p(a|\{\hat{x}_a\},\hat{\lambda}) = 2\mu_a \Theta(\hat{x}_a\cdot\hat{\lambda})$$
<!--simpleintegral-->
We can simulate $M_a^{r=\frac{1}{2}}$:
$$\begin{align}\int_S d\hat{\lambda} p(a|\{\hat{x}_a\},\hat{\lambda}) \Pi_{\hat{\lambda}} &= 2\mu_a\frac{1}{4\pi} \int_{\hat{x}_a\cdot\hat{\lambda} >0} d\hat{\lambda} (\mathbb{I} + \hat{\lambda} \cdot \vec{\sigma}) =\\&= 2\mu_a\frac{1}{2}\left(\mathbb{I} + \frac{1}{2} \hat{x}_a \cdot \vec{\sigma}\right) = M_a^{r=\frac{1}{2}}\end{align}$$
<!--simplenormalization-->
But it's not normalized:  
$$\sum_a p(a|\{\hat{x}_a\},\hat{\lambda}) \neq 1$$
<!--letsfix-->
Let's fix $p(a|\{\hat{x}_a\},\hat{\lambda})$!
<!--coarse-->
Coarse-grained POVM:
$$\begin{array}{l}\Pi_A = \int_S d\hat{\lambda} \prod_{a \in A}\Theta(\hat{x}\cdot\hat{\lambda})\prod_{a \notin A}(1 - \Theta(\hat{x}\cdot\hat{\lambda})) \Pi_{\hat{\lambda}},\\A \subset \{1, 2, 3\}\end{array}$$
<!--coarseexplicit-->
$$\begin{align}\Pi_{\{1\}} &= \frac{\theta_1}{2\pi}(\mathbb{I} - \frac{\pi \sin{\frac{\theta_1}{2}}}{2 \theta_1}\hat{\lambda}_1 \cdot \vec{\sigma})\\\Pi_{\{2, 3\}} &= \frac{\theta_1}{2\pi}(\mathbb{I} + \frac{\pi \sin{\frac{\theta_1}{2}}}{2 \theta_1}\hat{\lambda}_1 \cdot \vec{\sigma})\end{align}$$  
$$\hat{\lambda}_1 = \frac{\hat{x}_2 + \hat{x}_3}{|\hat{x}_2 + \hat{x}_3|}\text{, } \theta_1 = \arccos{(-\hat{x}_2 \cdot \hat{x}_3)}$$
<!--responceunnorm-->
Unnormalized response function:

|                       | $\Pi_{\{2,3\}}$ | $\Pi_{\{1,3\}}$ | $\Pi_{\{1,2\}}$ | $\Pi_{\{3\}}$ | $\Pi_{\{2\}}$ | $\Pi_{\{1\}}$ |
|:---------------------:|:---------------:|:---------------:|:---------------:|:-------------:|:-------------:|:-------------:|
| $M_1^{r=\frac{1}{2}}$ |                 |    $2\mu_1$     |    $2\mu_1$     |               |               |   $2\mu_1$    |
| $M_2^{r=\frac{1}{2}}$ |    $2\mu_2$     |                 |    $2\mu_2$     |               |   $2\mu_2$    |               |
| $M_3^{r=\frac{1}{2}}$ |    $2\mu_3$     |    $2\mu_3$     |                 |   $2\mu_3$    |               |               |
<!--responcenorm-->
Normalized response function:

|                       | $\Pi_{\{2,3\}}$ | $\Pi_{\{1,3\}}$ | $\Pi_{\{1,2\}}$ | $\Pi_{\{3\}}$ | $\Pi_{\{2\}}$ | $\Pi_{\{1\}}$ |
|:---------------------:|:---------------:|:---------------:|:---------------:|:-------------:|:-------------:|:-------------:|
| $M_1^{r=\frac{1}{2}}$ |                 |    $2\mu_1$     |    $2\mu_1$     |               |               |   $2\mu_1$    |
| $M_2^{r=\frac{1}{2}}$ |  $2\mu_2 - X$   |                 |  $1 - 2\mu_1$   |               |       1       |      $Y$      |
| $M_3^{r=\frac{1}{2}}$ |  $2\mu_3 - Y$   |  $1 - 2\mu_1$   |                 |       1       |               |      $X$      |