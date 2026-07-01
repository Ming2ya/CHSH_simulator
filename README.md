# 双比特量子纠缠制备与 CHSH 不等式违背的蒙特卡洛验证

这是量子信息基础课程大作业的代码仓库。项目实现 Bell 态制备、偏振基测量、Monte Carlo shots 抽样、CHSH 参数计算，并生成角度扫描和噪声扫描结果。

## 目录结构

```text
.
├── src/
│   ├── chsh.py          # 核心物理计算与 Monte Carlo 抽样
│   └── main.py          # 命令行入口、CSV 输出和绘图
├── report_LaTeX/        # LaTeX 报告与最终 PDF
├── results/             # CSV 实验结果
├── figures/             # 实验图像
├── requirements.txt
└── README.md
```

## 环境配置

建议使用单独的 conda 环境：

```bash
conda create -n chsh python=3.11
conda activate chsh
pip install -r requirements.txt
```

## 快速运行

在项目根目录下运行：

```bash
python -m src.main --shots 10000 --seed 42 --bell phi_plus
```

默认实验采用偏振角约定下的 CHSH 最优角度：

```text
a = 0 deg, a' = 45 deg, b = 22.5 deg, b' = -22.5 deg
```

一次典型输出为：

```text
S_sim    = 2.842800
S_theory = 2.828427
```

其中 `S_sim > 2` 表示 Monte Carlo 模拟结果违反经典 CHSH 上界。

## 常用实验命令

切换 Bell 态：

```bash
python -m src.main --shots 10000 --seed 42 --bell psi_minus
```

可选 Bell 态：

```text
phi_plus, phi_minus, psi_plus, psi_minus
```

角度扫描：

```bash
python -m src.main \
  --bell phi_plus \
  --angle-scan \
  --scan-start -45 \
  --scan-stop 45 \
  --scan-points 181 \
  --scan-shots 5000
```

噪声扫描：

```bash
python -m src.main \
  --bell phi_plus \
  --noise-scan \
  --noise-points 101 \
  --noise-shots 5000
```

自定义 shots 收敛实验：

```bash
python -m src.main \
  --bell phi_plus \
  --convergence-shots 100,500,1000,5000,10000,50000
```

## 输出文件

主程序会生成或更新以下文件：

```text
results/chsh_mvp_summary.csv
results/chsh_mvp_convergence.csv
results/chsh_angle_scan.csv
results/chsh_noise_scan.csv

figures/chsh_mvp_convergence.png
figures/chsh_angle_scan.png
figures/chsh_noise_scan.png
```

仓库中还保留了四个 Bell 态的角度扫描图：

```text
figures/phi_plus_angle_scan.png
figures/phi_minus_angle_scan.png
figures/psi_plus_angle_scan.png
figures/psi_minus_angle_scan.png
```
