#!/usr/bin/env python3
"""
Heightmap 可视化工具

从 heightmap.npy 文件生成多种形式的地形可视化图像

用法:
    python visualize_heightmap.py --input heightmap.npy
    python visualize_heightmap.py --input heightmap.npy --save_output terrain_viz.png
    python visualize_heightmap.py --input heightmap.npy --view_type 3d
"""

import numpy as np
import argparse
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def visualize_heightmap_2d(heightmap, save_path=None, cmap='terrain', title='Heightmap 2D View'):
    """
    2D 热力图可视化

    参数:
        heightmap: heightmap 数组
        save_path: 保存路径, None 表示不保存
        cmap: 颜色映射
        title: 图像标题
    """
    plt.figure(figsize=(12, 8))
    im = plt.imshow(heightmap, cmap=cmap, origin='lower', aspect='equal')
    plt.colorbar(im, label='Height (m)')
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('X (grid points)')
    plt.ylabel('Y (grid points)')
    plt.grid(True, alpha=0.3)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ 2D 热力图已保存到: {save_path}")

    plt.show()


def visualize_heightmap_3d(heightmap, save_path=None, cmap='terrain', title='Heightmap 3D View'):
    """
    3D 表面可视化，注意比例和现实情况不符

    参数:
        heightmap: heightmap 数组
        save_path: 保存路径, None 表示不保存
        cmap: 颜色映射
        title: 图像标题
    """
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')

    # 创建网格
    rows, cols = heightmap.shape
    x = np.arange(cols)
    y = np.arange(rows)
    X, Y = np.meshgrid(x, y)

    # 绘制 3D 表面
    surf = ax.plot_surface(X, Y, heightmap, cmap=cmap, alpha=0.9,
                          linewidth=0, antialiased=True)

    # 设置颜色条
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label='Height (m)')

    # 设置标签
    ax.set_xlabel('X (grid points)', fontsize=12)
    ax.set_ylabel('Y (grid points)', fontsize=12)
    ax.set_zlabel('Height (m)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')

    # 设置视角
    ax.view_init(elev=30, azim=45)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ 3D 表面图已保存到: {save_path}")

    plt.show()


def visualize_heightmap_contour(heightmap, save_path=None, cmap='terrain', title='Heightmap Contour View'):
    """
    等高线可视化

    参数:
        heightmap: heightmap 数组
        save_path: 保存路径, None 表示不保存
        cmap: 颜色映射
        title: 图像标题
    """
    plt.figure(figsize=(12, 8))

    # 创建等高线图
    contour = plt.contour(heightmap, levels=20, cmap=cmap, linewidths=1.5)
    plt.clabel(contour, inline=True, fontsize=10, fmt='%.2f m')

    # 添加填充
    plt.contourf(heightmap, levels=20, cmap=cmap, alpha=0.6)
    plt.colorbar(label='Height (m)')

    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('X (grid points)')
    plt.ylabel('Y (grid points)')
    plt.grid(True, alpha=0.3)
    plt.axis('equal')

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ 等高线图已保存到: {save_path}")

    plt.show()


def visualize_heightmap_stats(heightmap):
    """
    打印 heightmap 统计信息

    参数:
        heightmap: heightmap 数组
    """
    print("=" * 60)
    print("Heightmap 统计信息")
    print("=" * 60)
    print(f"形状: {heightmap.shape}")
    print(f"尺寸: {heightmap.shape[0]} × {heightmap.shape[1]}")
    print(f"最小高度: {heightmap.min():.3f} m")
    print(f"最大高度: {heightmap.max():.3f} m")
    print(f"平均高度: {heightmap.mean():.3f} m")
    print(f"高度标准差: {heightmap.std():.3f} m")
    print(f"非零点数: {np.count_nonzero(heightmap)}")
    print(f"非零比例: {np.count_nonzero(heightmap) / heightmap.size * 100:.2f}%")
    print("=" * 60)


def visualize_all(heightmap, output_dir=None, base_name='heightmap', cmap='terrain'):
    """
    生成所有类型的可视化

    参数:
        heightmap: heightmap 数组
        output_dir: 输出目录, None 表示不保存
        base_name: 基础文件名
        cmap: 颜色映射
    """
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 打印统计信息
    visualize_heightmap_stats(heightmap)

    # 2D 热力图
    save_path = os.path.join(output_dir, f'{base_name}_2d.png') if output_dir else None
    visualize_heightmap_2d(heightmap, save_path=save_path, cmap=cmap, title='Heightmap 2D View')

    # 3D 表面图
    save_path = os.path.join(output_dir, f'{base_name}_3d.png') if output_dir else None
    visualize_heightmap_3d(heightmap, save_path=save_path, cmap=cmap, title='Heightmap 3D View')

    # 等高线图
    save_path = os.path.join(output_dir, f'{base_name}_contour.png') if output_dir else None
    visualize_heightmap_contour(heightmap, save_path=save_path, cmap=cmap, title='Heightmap Contour View')


def main():
    parser = argparse.ArgumentParser(description='Heightmap 可视化工具')
    parser.add_argument('--input', type=str, default='heightmap.npy',
                        help='输入的 heightmap.npy 文件路径')
    parser.add_argument('--view_type', type=str, default='all',
                        choices=['2d', '3d', 'contour', 'all', 'stats'],
                        help='可视化类型: 2d, 3d, contour, all, stats')
    parser.add_argument('--save_output', type=str, default=None,
                        help='保存路径 (仅用于单视图模式)')
    parser.add_argument('--output_dir', type=str, default=None,
                        help='输出目录 (用于 all 模式)')
    parser.add_argument('--base_name', type=str, default='heightmap',
                        help='基础文件名 (用于 all 模式)')
    parser.add_argument('--cmap', type=str, default='terrain',
                        help='颜色映射 (terrain, viridis, plasma, magma, coolwarm 等)')
    parser.add_argument('--horizontal_scale', type=float, default=0.02,
                        help='水平分辨率 [meters] (用于统计信息)')
    parser.add_argument('--vertical_scale', type=float, default=0.005,
                        help='垂直分辨率 [meters] (用于统计信息)')

    args = parser.parse_args()

    # 检查文件是否存在
    if not os.path.exists(args.input):
        print(f"错误: 文件 '{args.input}' 不存在")
        return

    # 加载 heightmap
    print(f"正在加载 heightmap: {args.input}")
    heightmap = np.load(args.input)

    # 转换为实际高度值 (如果存储的是 int16)
    if heightmap.dtype == np.int16:
        heightmap = heightmap.astype(np.float32) * args.vertical_scale
        print("检测到 int16 格式,已转换为实际高度值")

    print(f"Heightmap 加载完成: shape={heightmap.shape}")

    # 根据视图类型进行可视化
    if args.view_type == 'stats':
        visualize_heightmap_stats(heightmap)
    elif args.view_type == '2d':
        visualize_heightmap_2d(heightmap, save_path=args.save_output, cmap=args.cmap)
    elif args.view_type == '3d':
        visualize_heightmap_3d(heightmap, save_path=args.save_output, cmap=args.cmap)
    elif args.view_type == 'contour':
        visualize_heightmap_contour(heightmap, save_path=args.save_output, cmap=args.cmap)
    elif args.view_type == 'all':
        visualize_all(heightmap, output_dir=args.output_dir, base_name=args.base_name, cmap=args.cmap)


if __name__ == '__main__':
    main()