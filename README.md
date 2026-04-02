# UIKA On Extreme Parkour

本仓库是在 `extreme-parkour` 基础上，为 UIKA 四足机器人做的适配版本。

## 仓库里包含什么

- UIKA 机器人资源与 URDF 适配
- UIKA 任务配置：`legged_gym/legged_gym/envs/uika/uika_parkour_config.py`
- 平地训练脚本：`legged_gym/legged_gym/scripts/train_uika_flat.py`
- 平地测试脚本：`legged_gym/legged_gym/scripts/play_uika_flat.py`
- 诊断脚本：
  - `legged_gym/legged_gym/scripts/check_uika_urdf.py`
  - `legged_gym/legged_gym/scripts/play_test.py`
  - `legged_gym/legged_gym/scripts/urdf_play_test.py`

## 环境安装

推荐直接使用导出的 conda 环境：

```bash
conda env create -f requirements/conda/parkour.yml
conda activate parkour
```

精简 pip 依赖文件：

```bash
requirements/parkour-requirements.txt
```

**PyTorch 版本要求：2.4.1**

```bash
pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1
pip install trimesh
```

## 训练流程

### 1）先做平地预训练（推荐）

```bash
cd legged_gym/legged_gym/scripts
python train_uika_flat.py --task uika --proj_name parkour_flat --exptid uika-flat-001 --num_envs 2048
```

### 2）在正常地形继续训练

```bash
cd legged_gym/legged_gym/scripts
python train.py --task uika --proj_name parkour_flat --exptid uika-rough-001 --resume --resumeid uika-flat-001 --num_envs 2048
```

## 测试与可视化

### 平地策略回放

```bash
cd legged_gym/legged_gym/scripts
python play_uika_flat.py --task uika --proj_name parkour_flat --exptid uika-flat-001 --checkpoint 300
```

### URDF 站立与接触检查

```bash
cd legged_gym/legged_gym/scripts
python check_uika_urdf.py --task uika --headless --num_envs 1
```

