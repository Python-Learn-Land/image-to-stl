#!/usr/bin/python3
# -*- coding: utf-8 -*-
# STL生成模块
# 将CMYK颜色层转换为3D可打印的STL模型

# 导入项目模块
from ImageAnalyzer import ImageAnalyzer  # 图像处理与分析模块
from Models import ColorCorrection, LayerType, StlConfig, StlCollection  # 配置模型与枚举
from color_mixing import extract_and_invert_channels, extract_and_invert_channels_linear  # 颜色通道处理

# 导入第三方库
import numpy as np  # 数值计算库
from stl.mesh import Mesh  # STL网格生成库
from typing import Tuple  # 类型提示

def create_layer_mesh(height_map: np.ndarray,
                     height_step_mm: float,
                     pixel_size: float,
                     previous_heights: np.ndarray = None,
                     min_height: float = 0,
                     flat_top: bool = False,
                     face_up: bool = False,
                     ) -> Tuple[Mesh, np.ndarray]:
    """
    创建单层STL网格模型

    参数:
    height_map: 高度图(二维数组)
    height_step_mm: 高度变化步长(mm)
    pixel_size: 像素块物理尺寸(mm)
    previous_heights: 前一层的高度(用于叠加层)
    min_height: 最小高度(mm)
    flat_top: 是否生成平顶效果
    face_up: STL是否正面朝上

    返回:
    Tuple[Mesh, np.ndarray]: STL网格模型和当前层的总高度
    """
    y_pixels, x_pixels = height_map.shape  # 获取高度图的尺寸

    # 向量化高度计算
    # 如果没有前一层高度，则初始化为全0
    previous_heights = np.zeros_like(height_map) if previous_heights is None else previous_heights
    # 如果是平顶模式，计算最大高度
    max_height = np.max(previous_heights) + min_height if flat_top else 0

    # 计算当前层的高度
    if flat_top:
        # 平顶模式：从最大高度减去前一层高度
        z = np.full_like(height_map, max_height) - previous_heights
    else:
        # 非平顶模式：基于高度图计算
        z = height_map.copy()
        # 按高度步长进行量化
        if height_step_mm > 0:
            z = np.round(z / height_step_mm) * height_step_mm
        # 确保高度不小于最小高度
        z = np.maximum(z, min_height)

    # 计算当前层的总高度(前一层高度 + 当前层高度)
    next_heights = z + previous_heights

    # 生成网格坐标
    x_coords, y_coords = np.meshgrid(np.arange(x_pixels), np.arange(y_pixels))

    # 创建顶点数组 (y_pixels, x_pixels, 8个顶点, 3个坐标(x,y,z))
    vertices = np.zeros((y_pixels, x_pixels, 8, 3))

    # 底部4个顶点 (z=previous_heights)
    vertices[:, :, 0] = np.stack([x_coords * pixel_size, y_coords * pixel_size, previous_heights], axis=-1)  # 左下角
    vertices[:, :, 1] = np.stack([(x_coords + 1) * pixel_size, y_coords * pixel_size, previous_heights], axis=-1)  # 右下角
    vertices[:, :, 2] = np.stack([(x_coords + 1) * pixel_size, (y_coords + 1) * pixel_size, previous_heights], axis=-1)  # 右上角
    vertices[:, :, 3] = np.stack([x_coords * pixel_size, (y_coords + 1) * pixel_size, previous_heights], axis=-1)  # 左上角

    # 顶部4个顶点 (z=next_heights)
    vertices[:, :, 4] = np.stack([x_coords * pixel_size, y_coords * pixel_size, next_heights], axis=-1)  # 左下角
    vertices[:, :, 5] = np.stack([(x_coords + 1) * pixel_size, y_coords * pixel_size, next_heights], axis=-1)  # 右下角
    vertices[:, :, 6] = np.stack([(x_coords + 1) * pixel_size, (y_coords + 1) * pixel_size, next_heights], axis=-1)  # 右上角
    vertices[:, :, 7] = np.stack([x_coords * pixel_size, (y_coords + 1) * pixel_size, next_heights], axis=-1)  # 左上角

    # 如果STL是正面朝上，镜像x坐标
    if face_up:
        total_width = x_pixels * pixel_size  # 模型总宽度
        vertices[:, :, :, 0] = total_width - vertices[:, :, :, 0]  # 镜像x坐标

    # 将顶点数组展平为 (n_vertices, 3)
    vertices = vertices.reshape(-1, 3)

    # 生成面 (每个像素块有6个面，每个面由3个顶点组成)
    pixel_indices = np.arange(y_pixels * x_pixels * 8).reshape(y_pixels, x_pixels, 8)
    base_indices = pixel_indices[:, :, 0].reshape(-1)  # 每个像素块的第一个顶点索引

    # 面模板：定义了一个立方体的6个面(每个面有2个三角形)
    face_template = np.array([
        [0, 2, 1], [0, 3, 2],  # 底部面
        [4, 5, 6], [4, 6, 7],  # 顶部面
        [0, 1, 5], [0, 5, 4],  # 前面
        [2, 3, 7], [2, 7, 6],  # 后面
        [0, 4, 7], [0, 7, 3],  # 左面
        [1, 2, 6], [1, 6, 5]   # 右面
    ])

    # 为每个像素块创建索引偏移
    offsets = np.arange(0, len(base_indices) * 8, 8)[:, None, None]

    # 广播生成所有面的索引
    faces = (face_template[None, :, :] + offsets).reshape(-1, 3)

    faces = np.array(faces)

    # 创建STL网格并计算法向量
    stl_mesh = Mesh(np.zeros(len(faces), dtype=Mesh.dtype))
    stl_mesh.vectors = vertices[faces]  # 设置网格向量

    # 向量化计算法向量
    v0 = vertices[faces[:, 0]]  # 第一个顶点
    v1 = vertices[faces[:, 1]]  # 第二个顶点
    v2 = vertices[faces[:, 2]]  # 第三个顶点

    edge1 = v1 - v0  # 边1
    edge2 = v2 - v0  # 边2
    normals = np.cross(edge1, edge2)  # 叉乘计算法向量

    # 归一化非零法向量
    norms = np.linalg.norm(normals, axis=1)  # 计算法向量长度
    mask = norms > 0  # 非零法向量的掩码
    normals[mask] = normals[mask] / norms[mask, np.newaxis]  # 归一化
    normals[~mask] = [0, 0, 1]  # 零法向量的默认值

    stl_mesh.normals = normals  # 设置法向量

    return stl_mesh, next_heights

def create_base_plate(x_pixels: int, y_pixels: int, config: StlConfig) -> Mesh:
    """
    创建白色基础层的STL网格

    参数:
    x_pixels: 图像宽度(像素)
    y_pixels: 图像高度(像素)
    config: STL配置对象

    返回:
    Mesh: 白色基础层的STL网格
    """
    # 创建基础层高度图(全为基础厚度)
    height_map = np.full((y_pixels, x_pixels), config.base_height, dtype=float)

    # 使用create_layer_mesh创建基础层
    base_mesh, _ = create_layer_mesh(
        height_map=height_map,
        height_step_mm=config.height_step_mm,
        pixel_size=config.pixel_size,
        previous_heights=np.zeros((y_pixels, x_pixels)),  # 基础层没有前一层
        face_up=config.face_up,
    )

    return base_mesh

def create_color_layer(height_map: np.ndarray,
                      previous_heights: np.ndarray,
                      config: StlConfig,
                      layer_type: LayerType,
                      flat_top: bool = False) -> Tuple[Mesh, np.ndarray]:
    """
    创建颜色层的STL网格

    参数:
    height_map: 高度图(二维数组)
    previous_heights: 前一层的高度
    config: STL配置对象
    layer_type: 颜色层类型(LayerType枚举)
    flat_top: 是否生成平顶效果

    返回:
    Tuple[Mesh, np.ndarray]: 颜色层的STL网格和当前层的总高度
    """
    # 调用create_layer_mesh创建颜色层
    # 白色层有最小高度要求，其他颜色层没有
    return create_layer_mesh(
        height_map=height_map,
        height_step_mm=config.height_step_mm,
        pixel_size=config.pixel_size,
        previous_heights=previous_heights,
        min_height=config.intensity_min_height if layer_type == LayerType.WHITE else 0,  # 白色层最小高度
        face_up=config.face_up,
        flat_top=flat_top
    )


def to_stl_cym(img: ImageAnalyzer, config: StlConfig = None) -> StlCollection:
    """
    生成CMYK颜色层的STL模型集合

    参数:
    img: ImageAnalyzer对象，包含像素化处理后的图像
    config: STL配置对象

    返回:
    StlCollection: STL模型集合，包含基础层和所有颜色层
    """
    # 如果没有提供配置，则使用默认配置
    if config is None:
        config = StlConfig()

    # 验证图像格式是否正确(必须是3通道的CYM图像)
    if len(img.pixelated.shape) != 3 or img.pixelated.shape[2] != 3:
        raise ValueError("Image must have 3 channels (CYM)")  # 图像必须是3通道(CYM)

    # 提取颜色通道强度信息
    # 根据配置选择不同的颜色校正方法
    intensity_channels = extract_and_invert_channels(img, config) if config.color_correction == ColorCorrection.LUMINANCE else extract_and_invert_channels_linear(img, config)

    # 获取图像尺寸
    y_pixels, x_pixels = img.pixelated.shape[:2]

    # 创建白色基础层
    print("creating stl: white_base_mesh.stl")
    base_mesh = create_base_plate(x_pixels, y_pixels, config)
    base_heights = np.full((y_pixels, x_pixels), config.base_height, dtype=float)  # 基础层高度
    print("base_heights " + str(config.base_height))

    # 定义颜色层配置
    layers = {
        'cyan_mesh': (intensity_channels.c_channel, base_heights, LayerType.CYAN),  # 青色层
        'yellow_mesh': (intensity_channels.y_channel, None, LayerType.YELLOW),  # 黄色层
        'magenta_mesh': (intensity_channels.m_channel, None, LayerType.MAGENTA),  # 品红色层
        'clear_mesh': (intensity_channels.intensity_map, None, LayerType.CLEAR),  # 透明层
        'white_intensity_mesh': (intensity_channels.intensity_map, None, LayerType.WHITE)  # 白色强度层
    }

    # 初始化前一层高度和网格集合
    previous_heights = base_heights
    meshes = {'white_base_mesh': base_mesh}  # 包含基础层的网格字典

    # 循环创建所有颜色层
    for name, (height_map, _, layer_type) in layers.items():
        print("creating stl: " + name + ".stl")
        # 创建颜色层
        mesh, previous_heights = create_color_layer(
            height_map=height_map,
            previous_heights=previous_heights,
            config=config,
            layer_type=layer_type,
            flat_top=layer_type == LayerType.CLEAR,  # 透明层使用平顶模式
        )
        # 将创建的网格添加到集合中
        meshes[name] = mesh

    # 返回包含所有层的STL模型集合
    return StlCollection(meshes=meshes)