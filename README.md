# UIKA On Extreme Parkour

本仓库是在 `extreme-parkour` 基础上，为 UIKA 四足机器人做的适配版本。

## 环境安装

```bash
conda create -n parkour python=3.8
conda activate parkour

pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1
pip install trimesh

git clone git@github.com:SAIKi0125/UIKA-On-Extreme-Parkour.git
cd UIKA-On-Extreme-Parkour

# 从 https://developer.nvidia.com/isaac-gym 下载 Isaac Gym 二进制文件
cd isaacgym/python && pip install -e .
cd ../rsl_rl && pip install -e .
cd ../legged_gym && pip install -e .

pip install "numpy<1.24" pydelatin wandb tqdm opencv-python ipdb pyfqmr flask
```

## 使用方法

### 环境变量

```bash
export LD_PRELOAD=/home/saiki/miniconda3/envs/parkour/lib/libpython3.8.so.1.0
```

### 训练

进入目录：`cd legged_gym/scripts`

平地预训练：

```bash
python train_uika_flat.py --task uika --proj_name parkour_flat --exptid uika-flat-001 --num_envs 2048
```

复杂地形继续训练：

```bash
python train.py --task uika --proj_name parkour_flat --exptid uika-rough-001 --resume --resumeid uika-flat-001 --num_envs 2048
```

蒸馏策略训练：

```bash
python train.py --task uika --proj_name parkour_flat --exptid uika-distill-001 --resume --resumeid uika-rough-001 --delay --use_camera
```

### 策略回放

平地策略回放：

```bash
python play_uika_flat.py --task uika --proj_name parkour_flat --exptid uika-flat-001 --checkpoint 300
```

### URDF 检查

```bash
python check_uika_urdf.py --task uika --headless --num_envs 1
```

## Viewer 使用方法

IsaacGym 和 Web viewer 均支持。

- `ALT + 鼠标左键 + 拖动`：移动视角
- `[]`：切换上一个/下一个机器人
- `Space`：暂停/继续
- `F`：切换自由相机和跟随相机

## 命令行参数

| 参数 | 说明 |
|------|------|
| `--task` | 机器人任务名，如 `uika` |
| `--proj_name` | 项目/实验组名 |
| `--exptid` | 实验 ID |
| `--num_envs` | 并行环境数量 |
| `--device` | 设备，如 `cuda:0`, `cpu` |
| `--headless` | 无 GUI 运行 |
| `--resume` | 从检查点恢复训练 |
| `--resumeid` | 要恢复的实验 ID |
| `--checkpoint` | 加载的检查点编号，-1 为最新 |
| `--seed` | 随机种子 |
| `--no_wandb` | 禁用 wandb 日志 |
| `--delay` | 添加延迟 |
| `--use_camera` | 使用相机而非扫描点 |
| `--web` | 使用 Web viewer（用于无头机器） |

模型日志保存在 `legged_gym/logs/<proj_name>/<exptid>/`
