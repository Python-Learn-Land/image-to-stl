#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 彩色石版画项目主入口
# 将2D图像转换为CMYK 3D可打印层(STL文件)

# 导入项目模块
from ImageAnalyzer import ImageAnalyzer  # 图像处理与分析模块
from Models import ColorCorrection, LuminanceConfig  # 配置模型
from filaments import FilamentLibrary  # 灯丝库管理
from to_stl import LayerType, to_stl_cym, StlConfig  # STL生成模块
from color_mixing import hex_to_rgb  # 颜色转换工具

# 导入系统与第三方库
import os  # 文件系统操作
import cv2  # OpenCV图像处理库
import argparse  # 命令行参数解析
from pathlib import Path  # 路径处理


# 配置命令行参数
parser = argparse.ArgumentParser(description='将2D图像转换为CMYK 3D可打印层(STL文件)')

# 图像显示选项
parser.add_argument('--show-images', action='store_true', default=False,
                   help='显示原始和处理后的图像')
# 输入输出路径选项
parser.add_argument('--input', '-i', default='examples/girl-with-pearl-earings.png',
                   help='输入图像文件路径')
parser.add_argument('--output-image', '-o', default='',
                   help='输出像素化图像文件路径')
# 物理尺寸与分辨率选项
parser.add_argument('--width', '-w', type=float, default=50,
                   help='期望的最终宽度(mm)')
parser.add_argument('--resolution', '-r', type=float, default=0.4,
                   help='分辨率，每个像素块的物理尺寸(mm)')
# STL输出配置
parser.add_argument('--stl-output', default='stl-output',
                   help='STL文件的输出目录')
parser.add_argument('--face-up', action='store_true', default=False,
                   help='生成的STL是否正面朝上(默认: 朝下)')
# 颜色层厚度配置
parser.add_argument('--cym-target-thickness', type=float, default=0.07,
                   help='CMY颜色层的目标厚度(mm)')
parser.add_argument('--white-target-thickness', type=float, default=0.16,
                   help='白色层的目标厚度(mm)')

# 解析命令行参数
args = parser.parse_args()

# 将命令行参数赋值给变量，提高代码可读性
show_images = args.show_images  # 是否显示图像
ifile = args.input  # 输入图像路径
ofile = args.output_image  # 输出像素化图像路径
desired_width_mm = args.width  # 最终物理宽度(mm)
resolution_mm = args.resolution  # 分辨率(mm/像素块)
face_up = args.face_up  # STL是否正面朝上

# 创建STL输出目录，如果不存在则自动创建
stl_output_dir = args.stl_output
os.makedirs(stl_output_dir, exist_ok=True)

# 根据期望宽度和分辨率计算像素块数量
n_blocks = int(desired_width_mm / resolution_mm)

# 初始化图像分析器，加载输入图像
img = ImageAnalyzer(ifile)
# 获取图像基本信息
img_info = img.get_image_info()
x_pixels = img_info.get('width')  # 图像原始宽度(像素)
y_pixels = img_info.get('height')  # 图像原始高度(像素)

# 计算每个像素块的尺寸(像素)
block_size = int(x_pixels / n_blocks)

# 保持原始宽高比的情况下计算最终物理高度(mm)
physical_height_mm = (y_pixels / x_pixels) * desired_width_mm

# 输出转换信息
print(f"图像将被分割为 {n_blocks}x{int(n_blocks * (y_pixels/x_pixels))} 个像素块")
print(f"每个像素块的物理尺寸: {resolution_mm}mm x {resolution_mm}mm")
print(f"最终打印尺寸: {desired_width_mm}mm x {physical_height_mm:.1f}mm")

# 加载灯丝库配置文件
yaml_path = Path("filaments.yaml")
library = FilamentLibrary.from_yaml(yaml_path)


# 对图像进行像素化处理，将图像分割为指定大小的像素块
img.pixelate(block_size)

# 如果指定了输出图像路径，则保存像素化处理后的图像
if not ofile == '' and not ofile is None:
    img.save_processed_image(ofile)

# 如果启用了图像显示选项，则显示原始图像和处理后的图像
if show_images:
    # 将RGB图像转换为BGR格式(OpenCV默认使用BGR)
    cv2.imshow('Original Image', cv2.cvtColor(img.original, cv2.COLOR_RGB2BGR))
    cv2.waitKey(0)  # 等待用户按键
    cv2.imshow('Processed Image', cv2.cvtColor(img.pixelated, cv2.COLOR_RGB2BGR))
    cv2.waitKey(0)  # 等待用户按键
    cv2.destroyAllWindows()  # 关闭所有OpenCV窗口

# 创建STL配置对象
stl_config = StlConfig(
    pixel_size=resolution_mm,  # 像素块物理尺寸(mm)
    base_height=0.2,  # 基础厚度(mm)
    intensity_min_height=0.2,  # 最小亮度高度(mm)
    height_step_mm=0.1,  # 高度变化步长(mm)
    face_up=face_up,  # STL是否正面朝上
    # 亮度配置
    luminance_config = LuminanceConfig(
        cym_target_thickness=args.cym_target_thickness,  # CMY颜色层目标厚度
        white_target_thickness=args.white_target_thickness,  # 白色层目标厚度
    ),
    color_correction=ColorCorrection.LUMINANCE,  # 颜色校正类型
    # 灯丝库配置
    filament_library={
        LayerType.CYAN: library.get_filament("bambu_cyan_pla"),     # 青色灯丝
        LayerType.YELLOW: library.get_filament("bambu_yellow_pla"),   # 黄色灯丝
        LayerType.MAGENTA: library.get_filament("bambu_magenta_pla"),  # 品红色灯丝
        LayerType.WHITE: library.get_filament("bambu_white_pla"),      # 白色灯丝
    }
)
# 输出STL配置信息
print(f"\nSTL Configuration:\n{stl_config.model_dump_json(indent=2)}")

# 主函数入口
if __name__ == "__main__":
    # 生成CMYK各颜色层的STL文件
    stl_collection = to_stl_cym(
        img,  # 图像处理对象
        config=stl_config  # STL配置
    )

    # 将STL文件保存到指定目录
    stl_collection.save_to_folder(stl_output_dir)
