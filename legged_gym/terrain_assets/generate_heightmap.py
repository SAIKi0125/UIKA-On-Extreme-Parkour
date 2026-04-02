#!/usr/bin/env python3
"""
从 STL mesh 文件生成 heightmap 用于 Extreme Parkour 地形观测

用法:
    python generate_heightmap.py --stl_path T_step.STL --output heightmap.npy
"""

import numpy as np
import argparse
import os
try:
    import trimesh
except ImportError:
    print("正在安装 trimesh...")
    os.system("pip install trimesh")
    import trimesh


def generate_heightmap_from_stl(stl_path, output_path, terrain_size=12.0, resolution=0.02, z_offset=0.0,
                               rotation_angle=0.0, x_offset=0.0, y_offset=0.0, auto_terrain_size=False, padding=0.5):
    """
    从 STL mesh 文件生成 heightmap

    参数:
        stl_path: STL 文件路径
        output_path: 输出的 heightmap.npy 文件路径
        terrain_size: 地形尺寸 [meters]，默认 12m × 12m。当 auto_terrain_size=True 时，此参数被忽略
        resolution: 分辨率 [meters]，默认 0.02m
        z_offset: z轴偏移量 [meters]，默认 0.0（mesh中心在z=0平面）
        rotation_angle: 围绕中心轴顺时针旋转角度 [度]，默认 0.0（不旋转）
        x_offset: 在 x 轴平移距离 [meters]，正数代表往图像右方移动，默认 0.0
        y_offset: 在 y 轴平移距离 [meters]，正数代表往图像上方移动，默认 0.0
        auto_terrain_size: 是否根据模型实际尺寸自动计算 terrain_size，默认 False
        padding: 边缘留白 [meters]，仅在 auto_terrain_size=True 时有效，默认 0.5m
    """
    print(f"正在加载 STL 文件: {stl_path}")
    
    # 加载 STL mesh
    mesh = trimesh.load_mesh(stl_path)
    
    # 检查 mesh 是否 watertight
    if not mesh.is_watertight:
        print(f"警告: Mesh 不是 watertight，可能会有空洞")
    
    # 检查单位并自动转换
    bbox = mesh.bounding_box.bounds
    bbox_size = bbox[1] - bbox[0]
    max_dim = np.max(bbox_size)
    
    print(f"Mesh bounding box: {bbox}")
    print(f"Mesh size: {bbox_size}")
    print(f"Max dimension: {max_dim:.3f} meters")
    
    # 如果 max_dim > 100，假设单位是 mm，转换为 meters
    if max_dim > 100:
        print("检测到单位可能是 mm，自动转换为 meters")
        mesh.apply_scale(0.001)
        bbox = mesh.bounding_box.bounds
        bbox_size = bbox[1] - bbox[0]
        max_dim = np.max(bbox_size)
        print(f"转换后 Mesh bounding box: {bbox}")
        print(f"转换后 Mesh size: {bbox_size}")

    # 如果启用自动计算 terrain_size
    if auto_terrain_size:
        print("启用自动 terrain_size 计算模式")

        # 先将 mesh 居中到原点（便于旋转）
        mesh_center = mesh.bounding_box.centroid
        mesh.apply_translation(-mesh_center)

        # 应用旋转变换（围绕原点，顺时针旋转）
        if rotation_angle != 0.0:
            # 将角度转换为弧度（顺时针旋转，所以取负）
            angle_rad = np.radians(-rotation_angle)

            # 创建旋转矩阵（围绕 z 轴）
            rotation_matrix = np.array([
                [np.cos(angle_rad), -np.sin(angle_rad), 0.0],
                [np.sin(angle_rad), np.cos(angle_rad), 0.0],
                [0.0, 0.0, 1.0]
            ])

            # 应用旋转
            mesh.vertices = mesh.vertices @ rotation_matrix.T

            print(f"Mesh 已顺时针旋转 {rotation_angle:.1f} 度")

        # 计算旋转后的 bounding box
        bbox = mesh.bounding_box.bounds
        bbox_size = bbox[1] - bbox[0]

        print(f"旋转后 Mesh bounding box: {bbox}")
        print(f"旋转后 Mesh size: {bbox_size}")

        # 根据 bbox + padding 计算 terrain_size
        mesh_size_x = bbox_size[0]
        mesh_size_y = bbox_size[1]

        terrain_size_x = mesh_size_x + 2 * padding
        terrain_size_y = mesh_size_y + 2 * padding

        # 取较大的尺寸作为正方形 terrain_size
        terrain_size = max(terrain_size_x, terrain_size_y)

        # 确保 terrain_size 是 resolution 的整数倍
        terrain_size = np.ceil(terrain_size / resolution) * resolution

        print(f"Mesh 实际尺寸: {mesh_size_x:.3f}m × {mesh_size_y:.3f}m")
        print(f"自动计算 terrain_size: {terrain_size:.3f}m × {terrain_size:.3f}m (padding: {padding:.3f}m)")

        # 将 mesh 居中到地形中央
        target_center = np.array([terrain_size / 2, terrain_size / 2, z_offset])
        mesh.apply_translation(target_center)

        print(f"Mesh 已居中到地形中央: ({target_center[0]:.2f}, {target_center[1]:.2f}, {target_center[2]:.2f})")
        if z_offset != 0.0:
            print(f"z 轴偏移量: {z_offset:.3f} m")
    else:
        print("使用手动 terrain_size 模式")

        # 将 mesh 居中到地形中央
        mesh_center = mesh.bounding_box.centroid
        target_center = np.array([terrain_size / 2, terrain_size / 2, z_offset])
        translation = target_center - mesh_center
        mesh.apply_translation(translation)

        print(f"Mesh 已居中到地形中央: ({target_center[0]:.2f}, {target_center[1]:.2f}, {target_center[2]:.2f})")
        if z_offset != 0.0:
            print(f"z 轴偏移量: {z_offset:.3f} m")

        # 应用旋转变换（围绕地形中心，顺时针旋转）
        if rotation_angle != 0.0:
            # 将角度转换为弧度（顺时针旋转，所以取负）
            angle_rad = np.radians(-rotation_angle)
            rotation_center = np.array([terrain_size / 2, terrain_size / 2, 0.0])

            # 创建旋转矩阵（围绕 z 轴）
            rotation_matrix = np.array([
                [np.cos(angle_rad), -np.sin(angle_rad), 0.0],
                [np.sin(angle_rad), np.cos(angle_rad), 0.0],
                [0.0, 0.0, 1.0]
            ])

            # 将顶点平移到原点，旋转，再平移回中心
            vertices = mesh.vertices - rotation_center
            vertices = vertices @ rotation_matrix.T
            vertices = vertices + rotation_center
            mesh.vertices = vertices

            print(f"Mesh 已顺时针旋转 {rotation_angle:.1f} 度")
            print(f"旋转中心: ({rotation_center[0]:.2f}, {rotation_center[1]:.2f}, {rotation_center[2]:.2f})")

    # 应用平移变换（x 和 y 轴）
    if x_offset != 0.0 or y_offset != 0.0:
        translation_offset = np.array([x_offset, y_offset, 0.0])
        mesh.apply_translation(translation_offset)
        print(f"Mesh 已平移: x={x_offset:.3f} m, y={y_offset:.3f} m")

    # 打印最终位置信息
    final_bbox = mesh.bounding_box.bounds
    print(f"最终 Mesh bounding box: {final_bbox}")
    
    # 生成 ray grid
    grid_size = int(terrain_size / resolution)
    x = np.linspace(0, terrain_size, grid_size)
    y = np.linspace(0, terrain_size, grid_size)
    xx, yy = np.meshgrid(x, y)
    
    # 创建 ray origins (从上方投射)
    ray_origins = np.zeros((grid_size * grid_size, 3))
    ray_origins[:, 0] = xx.flatten()
    ray_origins[:, 1] = yy.flatten()
    ray_origins[:, 2] = 100.0  # 从高处投射
    
    # ray directions (向下)
    ray_directions = np.zeros((grid_size * grid_size, 3))
    ray_directions[:, 2] = -1.0
    
    print(f"正在 raycasting: {grid_size} × {grid_size} = {grid_size * grid_size} rays")
    
    # 执行 ray intersection
    locations, _, _ = mesh.ray.intersects_location(
        ray_origins=ray_origins,
        ray_directions=ray_directions
    )
    
    # 构建 heightmap
    heightmap = np.zeros((grid_size, grid_size), dtype=np.float32)
    
    # 对于每个 ray，找到最近的交点
    for i in range(grid_size):
        for j in range(grid_size):
            idx = i * grid_size + j
            # 找到所有来自这个 ray 的交点
            mask = (locations[:, 0] == xx[i, j]) & (locations[:, 1] == yy[i, j])
            ray_hits = locations[mask]
            
            if len(ray_hits) > 0:
                # 取最高点（z坐标最大的）
                heightmap[i, j] = np.max(ray_hits[:, 2])
            else:
                # 没有交点，设置为地面高度 (0)
                heightmap[i, j] = 0.0
    
    print(f"Heightmap 生成完成: shape={heightmap.shape}")
    print(f"Heightmap 范围: {heightmap.min():.3f} ~ {heightmap.max():.3f} meters")

    # 计算并显示尺寸信息
    heightmap_size_x = heightmap.shape[1] * resolution
    heightmap_size_y = heightmap.shape[0] * resolution
    print(f"Heightmap 物理尺寸: {heightmap_size_x:.3f}m × {heightmap_size_y:.3f}m")
    print(f"Resolution: {resolution:.3f}m/pixel")

    # 计算模型在 heightmap 中的占用情况
    final_bbox = mesh.bounding_box.bounds
    model_min_x, model_max_x = final_bbox[0, 0], final_bbox[1, 0]
    model_min_y, model_max_y = final_bbox[0, 1], final_bbox[1, 1]

    # 转换为像素坐标
    pixel_min_x = int(model_min_x / resolution)
    pixel_max_x = int(model_max_x / resolution)
    pixel_min_y = int(model_min_y / resolution)
    pixel_max_y = int(model_max_y / resolution)

    model_width_pixels = pixel_max_x - pixel_min_x
    model_height_pixels = pixel_max_y - pixel_min_y

    print(f"模型在 heightmap 中的占用: {model_width_pixels} × {model_height_pixels} pixels")
    print(f"模型实际尺寸: {(model_max_x - model_min_x):.3f}m × {(model_max_y - model_min_y):.3f}m")

    # 验证尺寸一致性
    model_width_meters = model_width_pixels * resolution
    model_height_meters = model_height_pixels * resolution
    print(f"从像素计算的模型尺寸: {model_width_meters:.3f}m × {model_height_meters:.3f}m")

    # 保存 heightmap
    np.save(output_path, heightmap)
    print(f"Heightmap 已保存到: {output_path}")
    
    return heightmap


def main():
    parser = argparse.ArgumentParser(description='从 STL 生成 heightmap')
    parser.add_argument('--stl_path', type=str, default='T_step.STL',
                        help='STL 文件路径')
    parser.add_argument('--output', type=str, default='heightmap.npy',
                        help='输出的 heightmap.npy 文件路径')
    parser.add_argument('--terrain_size', type=float, default=12.0,
                        help='地形尺寸 [meters] (默认: 12.0, 当 --auto_terrain_size=True 时被忽略)')
    parser.add_argument('--resolution', type=float, default=0.02,
                        help='分辨率 [meters] (默认: 0.02)')
    parser.add_argument('--z_offset', type=float, default=0.0,
                        help='z轴偏移量 [meters] (默认: 0.0, mesh中心在z=0平面)')
    parser.add_argument('--rotation_angle', type=float, default=0.0,
                        help='围绕中心轴顺时针旋转角度 [度] (默认: 0.0, 不旋转)')
    parser.add_argument('--x_offset', type=float, default=0.0,
                        help='在 x 轴平移距离 [meters] (默认: 0.0, 正数代表往图像右方移动)')
    parser.add_argument('--y_offset', type=float, default=0.0,
                        help='在 y 轴平移距离 [meters] (默认: 0.0, 正数代表往图像上方移动)')
    parser.add_argument('--auto_terrain_size', action='store_true',
                        help='自动根据模型实际尺寸计算 terrain_size (推荐，确保模型尺寸准确)')
    parser.add_argument('--padding', type=float, default=0.5,
                        help='边缘留白 [meters] (默认: 0.5, 仅在 --auto_terrain_size=True 时有效)')

    args = parser.parse_args()

    # 生成 heightmap
    heightmap = generate_heightmap_from_stl(
        stl_path=args.stl_path,
        output_path=args.output,
        terrain_size=args.terrain_size,
        resolution=args.resolution,
        z_offset=args.z_offset,
        rotation_angle=args.rotation_angle,
        x_offset=args.x_offset,
        y_offset=args.y_offset,
        auto_terrain_size=args.auto_terrain_size,
        padding=args.padding
    )


if __name__ == '__main__':
    main()