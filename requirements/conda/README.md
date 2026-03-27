# Conda Environment Snapshots

This folder stores reproducible conda environment snapshots exported from this machine.

## Exported environments

- `base.yml` (python=3.13.9)
- `env_isaaclab.yml` (python=3.10.19)
- `isaaclab_tacto.yml` (python=3.8.20)
- `parkour.yml` (python=3.8.20)
- `tac3d.yml` (python=3.11.15)
- `tacsl.yml` (python=3.8.0)
- `tacto.yml` (python=3.7.12)

## Recreate on another machine

```bash
conda env create -f requirements/conda/parkour.yml
conda activate parkour
```

For any other environment, replace `parkour.yml` with the corresponding file name.
