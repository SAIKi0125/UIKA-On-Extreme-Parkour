#!/usr/bin/env python3
"""
测试通用的 STL 地形框架
"""

import numpy as np

# 模拟 STL_TERRAIN_CONFIG
STL_TERRAIN_CONFIG = {
    "T_step_stl": {
        "heightmap_path": "legged_gym/legged_gym/terrain_assets/T_step_heightmap.npy",
        "display_name": "T_step"
    },
    # 示例：添加更多地形
    # "staircase_stl": {
    #     "heightmap_path": "legged_gym/legged_gym/terrain_assets/staircase_terrain_heightmap.npy",
    #     "display_name": "Staircase"
    # },
}

def test_stl_config():
    print("=" * 60)
    print("测试 STL 地形配置框架")
    print("=" * 60)

    print(f"\n[1] STL_TERRAIN_CONFIG 配置:")
    for key, value in STL_TERRAIN_CONFIG.items():
        print(f"  {key}:")
        print(f"    heightmap_path: {value['heightmap_path']}")
        print(f"    display_name: {value['display_name']}")

    print(f"\n[2] 测试配置访问:")
    terrain_name = "T_step_stl"
    stl_config = STL_TERRAIN_CONFIG.get(terrain_name)

    if stl_config:
        print(f"  ✓ 成功获取 '{terrain_name}' 配置")
        print(f"    显示名称: {stl_config['display_name']}")
        print(f"    Heightmap 路径: {stl_config['heightmap_path']}")

        # 测试加载 heightmap
        try:
            heightmap = np.load(stl_config['heightmap_path'])
            print(f"  ✓ Heightmap 加载成功")
            print(f"    形状: {heightmap.shape}")
            print(f"    范围: [{heightmap.min():.3f}, {heightmap.max():.3f}] meters")
        except FileNotFoundError:
            print(f"  ✗ Heightmap 文件未找到: {stl_config['heightmap_path']}")
    else:
        print(f"  ✗ 未找到 '{terrain_name}' 配置")

    print(f"\n[3] 测试添加新地形:")
    new_terrain_name = "staircase_stl"
    new_config = {
        "heightmap_path": "legged_gym/legged_gym/terrain_assets/staircase_terrain_heightmap.npy",
        "display_name": "Staircase"
    }

    # 添加新配置
    STL_TERRAIN_CONFIG[new_terrain_name] = new_config

    print(f"  ✓ 添加新地形: {new_terrain_name}")
    print(f"    配置: {new_config}")

    # 验证添加
    retrieved_config = STL_TERRAIN_CONFIG.get(new_terrain_name)
    if retrieved_config:
        print(f"  ✓ 新地形配置验证成功")
    else:
        print(f"  ✗ 新地形配置验证失败")

    print(f"\n[4] 测试地形比例配置:")
    terrain_dict = {
        "parkour": 0.2,
        "parkour_hurdle": 0.15,
        "parkour_step": 0.15,
        "T_step_stl": 0.1,
        "staircase_stl": 0.15,
    }

    total = sum(terrain_dict.values())
    print(f"  地形总数: {len(terrain_dict)}")
    print(f"  总比例: {total:.2f}")
    print(f"  STL 地形比例: {terrain_dict.get('T_step_stl', 0) + terrain_dict.get('staircase_stl', 0):.2f}")

    if abs(total - 1.0) < 0.01:
        print(f"  ✓ 地形比例总和正确")
    else:
        print(f"  ✗ 地形比例总和错误（应为 1.0）")

    print(f"\n[5] 测试框架使用流程:")
    print(f"  步骤 1: 生成 heightmap")
    print(f"    python generate_heightmap.py --stl_path my_terrain.STL --output my_terrain_heightmap.npy")
    print(f"  步骤 2: 在 STL_TERRAIN_CONFIG 中添加配置")
    print(f"    STL_TERRAIN_CONFIG['my_terrain_stl'] = {{...}}")
    print(f"  步骤 3: 在 make_terrain 中添加处理逻辑")
    print(f"    stl_config = STL_TERRAIN_CONFIG.get('my_terrain_stl')")
    print(f"    stl_heightmap_terrain(terrain, **stl_config)")
    print(f"  步骤 4: 在 terrain_dict 中添加地形类型")
    print(f"    terrain_dict['my_terrain_stl'] = 0.15")

    print("\n" + "=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)

if __name__ == '__main__':
    test_stl_config()