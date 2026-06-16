# 双比特量子纠缠制备与 CHSH 不等式违背的蒙特卡洛验证

## 摘要

本项目使用 NumPy 自建量子态矢量模拟器，制备双比特 Bell 态

```text
|Phi+> = (|00> + |11>) / sqrt(2)
```

并在偏振光子测量角约定下，对两个量子比特进行大量重复测量。程序统计不同测量基组合下的关联期望值，最终计算 CHSH 参数。MVP 实验表明，在最优偏振角设置下，Monte Carlo 模拟得到的 CHSH 参数超过经典局域隐变量理论上界 2，并接近量子理论值 `2sqrt(2)`。

## 理论约定

本项目采用偏振光子测量角约定。角度为 `theta` 的测量基定义为：

```text
|+_theta> = cos(theta)|0> + sin(theta)|1>
|-_theta> = -sin(theta)|0> + cos(theta)|1>
```

对于 Bell 态 `|Phi+>`，两个测量角分别为 `theta_A` 和 `theta_B` 时，理论关联函数为：

```text
E(theta_A, theta_B) = cos(2(theta_A - theta_B))
```

因此本实验使用偏振角约定下的 CHSH 最优角度：

```text
a  = 0 deg
a' = 45 deg
b  = 22.5 deg
b' = -22.5 deg
```

CHSH 参数定义为：

```text
S = E(a,b) + E(a,b') + E(a',b) - E(a',b')
```

经典局域隐变量理论要求 `|S| <= 2`，而量子理论在上述设置下给出：

```text
S = 2sqrt(2) ≈ 2.828427
```

## 方法

程序首先从 `|00>` 出发，对第一个量子比特施加 Hadamard 门，再施加以第一个量子比特为控制位、第二个量子比特为目标位的 CNOT 门，得到 `|Phi+>`。

对于每一组测量角，程序计算四种联合测量结果的概率：

```text
P(++), P(+-), P(-+), P(--)
```

概率由投影振幅给出：

```text
P(s,t) = |(<s_thetaA| tensor <t_thetaB|) |Phi+>|^2
```

随后程序按该概率分布进行 `shots` 次 Monte Carlo 抽样。关联期望值由计数得到：

```text
E = (N++ + N-- - N+- - N-+) / shots
```

## MVP 实验结果

默认运行命令为：

```bash
python main.py --shots 10000 --seed 42
```

该命令会生成：

```text
results/chsh_mvp_summary.csv
results/chsh_mvp_convergence.csv
figures/chsh_mvp_convergence.png
```

本次默认实验结果如下：

| Pair | E_sim | E_theory | Error |
|---|---:|---:|---:|
| a_b | 0.709400 | 0.707107 | 0.002293 |
| a_bp | 0.696800 | 0.707107 | -0.010307 |
| ap_b | 0.716200 | 0.707107 | 0.009093 |
| ap_bp | -0.699000 | -0.707107 | 0.008107 |

由此得到：

```text
S_sim    = 2.821400
S_theory = 2.828427
```

因此本次 Monte Carlo 实验满足 `S_sim > 2`，表现出对 CHSH 经典上界的违背。

收敛图保存在：

```text
figures/chsh_mvp_convergence.png
```

![CHSH convergence](figures/chsh_mvp_convergence.png)

该图以 shots 为横轴，以 CHSH 参数 `S` 为纵轴，同时标出经典极限 `2` 和量子理论值 `2sqrt(2)`。

## 讨论

有限 shots 下的实验结果会有统计涨落，因此单次模拟得到的 `S` 不会严格等于理论值。随着 shots 增加，Monte Carlo 估计会逐渐接近理论值。若测量角度采用偏振基约定下的最优设置，`|Phi+>` 的关联结构会使 CHSH 参数超过经典上界 2，从而展示量子纠缠关联无法由经典局域隐变量模型解释。

角度约定是本实验的关键。若使用偏振测量基 `cos(theta)|0> + sin(theta)|1>`，理论关联函数必须写作 `cos(2(theta_A - theta_B))`，对应最优角度是 `0, 45, 22.5, -22.5` 度，而不是自旋 1/2 约定下的角度组合。

## 结论

MVP 阶段已经完成 Bell 态制备、偏振基测量、Monte Carlo shots 抽样、关联期望值统计和 CHSH 参数计算。默认实验应能得到 `S > 2` 的结果，并随 shots 增大逐步接近 `2sqrt(2)`。后续可以在此基础上继续加入四个 Bell 态比较、visibility 噪声模型、约化密度矩阵与 von Neumann 熵分析。
