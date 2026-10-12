<!--pvm-->
$$M_{\pm} = \frac{1}{2}\left(\mathbb{I} \pm \hat{x} \cdot \vec{\sigma}\right)$$
<!--noisypvm2-->
$$M_{\pm} = \frac{1}{2}\left(\mathbb{I} \pm \hat{x} \cdot \vec{\sigma}\right) \xrightarrow{\text{noise}} M_{\pm}^{r=\frac{1}{2}} = \frac{1}{2}\left(\mathbb{I} \pm \frac{1}{2} \hat{x} \cdot \vec{\sigma}\right)$$
<!--noisypvm-->
Noisy version:  
$$M_{\pm}^{r=\frac{1}{2}} = \frac{1}{2}\left(\mathbb{I} \pm \frac{1}{2} \hat{x} \cdot \vec{\sigma}\right)$$
<!--parentpvm-->
Parent POVM:  
$$\Pi_{\hat{\lambda}} = \frac{1}{4\pi}\left(\mathbb{I} + \hat{\lambda} \cdot \vec{\sigma}\right)$$
<!--response-->
Response function:  
$$p(\pm|\{\hat{x}\},\hat{\lambda}) = \Theta(\pm\hat{x}\cdot\hat{\lambda}) = \begin{cases}1 & \text{if } \pm\hat{x}\cdot\hat{\lambda} >0\\ 0 & \text{otherwise}\end{cases}$$
<!--integral-->
Checking that $\Pi_{\hat{\lambda}}$ simulates $M_{\pm}^{r=\frac{1}{2}}$:  
$$\begin{align}\int_S d\hat{\lambda} p(\pm|\{\hat{x}\},\hat{\lambda}) \Pi_{\hat{\lambda}} &= \frac{1}{4\pi} \int_{\pm\hat{x}\cdot\hat{\lambda} >0} d\hat{\lambda} (\mathbb{I} + \hat{\lambda} \cdot \vec{\sigma}) = \\ &= \frac{1}{2}\left(\mathbb{I} \pm \frac{1}{2} \hat{x} \cdot \vec{\sigma}\right) = M_{\pm}^{r=\frac{1}{2}}\end{align}$$