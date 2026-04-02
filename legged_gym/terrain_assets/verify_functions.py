#!/usr/bin/env python3
"""
验证 terrain.py 中添加的函数
"""

import numpy as np


def load_heightmap(heightmap_path, horizontal_scale=0.02, vertical_scale=0.005):
    """加载预生成的 heightmap.npy 文件。"""
    print(f"正在加载 heightmap: {heightmap_path}")
    heightmap = np.load(heightmap_path).astype(np.float32)
    height_field_raw = (heightmap / vertical_scale).astype(np.int16)
    print(f"Heightmap 加载完成: shape={height_field_raw.shape}")
    print(f"Heightmap 范围: {heightmap.min():.3f} ~ {heightmap.max():.3f} meters")
    return height_field_raw, heightmap


def get_heightmap_extent(heightmap, resolution=0.02, threshold=1e-6):
    """从高程图中提取实际占用的尺寸、中心和高度。"""
    mask = heightmap > threshold
    if not np.any(mask):
        return {
            "center_x": 0.0,
            "center_y": 0.0,
            "size_x": 0.0,
            "size_y": 0.0,
            "height_max": float(heightmap.max()),
        }

    ys, xs = np.where(mask)
    min_y, max_y = ys.min(), ys.max()
    min_x, max_x = xs.min(), xs.max()

    size_y = (max_y - min_y + 1) * resolution
    size_x = (max_x - min_x + 1) * resolution
    center_y = ((min_y + max_y + 1) / 2.0) * resolution
    center_x = ((min_x + max_x + 1) / 2.0) * resolution

    return {
        "center_x": float(center_x),
        "center_y": float(center_y),
        "size_x": float(size_x),
        "size_y": float(size_y),
        "height_max": float(heightmap.max()),
    }


def load_stl_mesh(stl_path, heightmap_extent=None, terrain_size=5.0, center_to_terrain=True):
    """加载 STL mesh；如果提供 heightmap_extent，则 mesh 按高程图对齐。"""
    import trimesh

    print(f"正在加载 STL mesh: {stl_path}")
    mesh = trimesh.load_mesh(stl_path)

    if not mesh.is_watertight:
        print(f"警告: Mesh '{stl_path}' 不是 watertight，可能会有空洞")

    bbox = mesh.bounding_box.bounds
    bbox_size = bbox[1] - bbox[0]
    max_dim = np.max(bbox_size)

    print(f"Mesh bounding box: {bbox}")
    print(f"Mesh size: {bbox_size}")
    print(f"Max dimension: {max_dim:.3f} meters")

    if max_dim > 100:
        print("检测到单位可能是 mm，自动转换为 meters")
        mesh.apply_scale(0.001)
        bbox = mesh.bounding_box.bounds
        bbox_size = bbox[1] - bbox[0]
        print(f"转换后 Mesh bounding box: {bbox}")
        print(f"转换后 Mesh size: {bbox_size}")

    if heightmap_extent is not None:
        bbox = mesh.bounding_box.bounds
        bbox_size = bbox[1] - bbox[0]
        scale_x = heightmap_extent["size_x"] / bbox_size[0] if bbox_size[0] > 0 else 1.0
        scale_y = heightmap_extent["size_y"] / bbox_size[1] if bbox_size[1] > 0 else 1.0
        scale_z = heightmap_extent["height_max"] / bbox_size[2] if bbox_size[2] > 0 else 1.0
        mesh.apply_scale([scale_x, scale_y, scale_z])

        bbox = mesh.bounding_box.bounds
        translation = np.array([
            heightmap_extent["center_x"] - 0.5 * (bbox[0, 0] + bbox[1, 0]),
            heightmap_extent["center_y"] - 0.5 * (bbox[0, 1] + bbox[1, 1]),
            -bbox[0, 2],
        ])
        mesh.apply_translation(translation)
        print(
            f"Mesh 已按 heightmap 对齐: center=({heightmap_extent['center_x']:.3f}, {heightmap_extent['center_y']:.3f}), "
            f"size=({heightmap_extent['size_x']:.3f}, {heightmap_extent['size_y']:.3f}), "
            f"height={heightmap_extent['height_max']:.3f}"
        )
    elif center_to_terrain:
        mesh_center = mesh.bounding_box.centroid
        target_center = np.array([terrain_size / 2, terrain_size / 2, 0.0])
        mesh.apply_translation(target_center - mesh_center)
        print(f"Mesh 已居中到地形中央: ({target_center[0]:.2f}, {target_center[1]:.2f}, {target_center[2]:.2f})")

    vertices = mesh.vertices.astype(np.float32)
    triangles = mesh.faces.astype(np.uint32)
    print(f"Mesh 加载完成: {vertices.shape[0]} 顶点, {triangles.shape[0]} 三角形面")
    return vertices, triangles


def main():
    print("=" * 60)
    print("验证 STL mesh 加载功能")
    print("=" * 60)

    heightmap_path = "/home/saiki/IsaacGym/extreme-parkour/legged_gym/terrain_assets/height_maps/T_step.npy"
    stl_path = "/home/saiki/IsaacGym/extreme-parkour/legged_gym/terrain_assets/terrain_models/T_step.STL"

    print("\n[1] 测试 load_heightmap 函数...")
    height_field_raw, heightmap = load_heightmap(heightmap_path, horizontal_scale=0.02, vertical_scale=0.005)
    extent = get_heightmap_extent(heightmap, resolution=0.02)

    print("\n✓ load_heightmap 测试通过:")
    print(f"  Heightmap 形状: {height_field_raw.shape}")
    print(f"  Heightmap 范围: [{height_field_raw.min() * 0.005:.3f}, {height_field_raw.max() * 0.005:.3f}] m")
    print(f"  Heightmap 占用尺寸: [{extent['size_x']:.3f}, {extent['size_y']:.3f}] m")
    print(f"  Heightmap 中心: [{extent['center_x']:.3f}, {extent['center_y']:.3f}] m")

    print("\n" + "=" * 60)
    print("[2] 测试 load_stl_mesh 函数...")
    vertices, triangles = load_stl_mesh(stl_path, heightmap_extent=extent)

    print("\n✓ load_stl_mesh 测试通过:")
    print(f"  顶点数: {vertices.shape[0]}")
    print(f"  三角形面数: {triangles.shape[0]}")
    print(f"  顶点 X 范围: [{vertices[:, 0].min():.3f}, {vertices[:, 0].max():.3f}] m")
    print(f"  顶点 Y 范围: [{vertices[:, 1].min():.3f}, {vertices[:, 1].max():.3f}] m")
    print(f"  顶点 Z 范围: [{vertices[:, 2].min():.3f}, {vertices[:, 2].max():.3f}] m")

    print("\n" + "=" * 60)
    print("[3] 验证数据一致性...")
    mesh_bbox_min = vertices.min(axis=0)
    mesh_bbox_max = vertices.max(axis=0)
    mesh_size = mesh_bbox_max - mesh_bbox_min
    mesh_center = 0.5 * (mesh_bbox_min + mesh_bbox_max)

    print(f"  Mesh 尺寸: [{mesh_size[0]:.3f}, {mesh_size[1]:.3f}, {mesh_size[2]:.3f}] m")
    print(f"  Heightmap 目标尺寸: [{extent['size_x']:.3f}, {extent['size_y']:.3f}, {extent['height_max']:.3f}] m")
    print(f"  Mesh 中心: [{mesh_center[0]:.3f}, {mesh_center[1]:.3f}, {mesh_center[2]:.3f}]")
    print(f"  Heightmap 目标中心: [{extent['center_x']:.3f}, {extent['center_y']:.3f}, 0.000]")

    size_error = np.array([
        abs(mesh_size[0] - extent['size_x']),
        abs(mesh_size[1] - extent['size_y']),
        abs(mesh_size[2] - extent['height_max']),
    ])
    center_error = np.linalg.norm(mesh_center[:2] - np.array([extent['center_x'], extent['center_y']]))
    z_error = abs(mesh_bbox_min[2])

    print(f"  尺寸误差: [{size_error[0]:.3f}, {size_error[1]:.3f}, {size_error[2]:.3f}] m")
    print(f"  平面中心误差: {center_error:.3f} m")
    print(f"  底面对地误差: {z_error:.3f} m")

    print("\n" + "=" * 60)
    print("验证完成")
    print("=" * 60)


if __name__ == '__main__':
    main()
