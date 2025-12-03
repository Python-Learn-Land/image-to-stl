# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述
这是一个彩色石版画项目，将2D图像转换为CMYK 3D可打印层（STL文件）。

## 主要依赖
- numpy-stl==2.16.3
- numpy>=2.1.3
- opencv-contrib-python>=4.10.0.84
- opencv-python>=4.10.0.84
- pydantic>=2.10.2
- pyyaml>=6.0.2
- scipy>=1.14.1
- stl>=0.0.3

## 设置与开发
```bash
# 初始化虚拟环境
uv venv
source .venv/bin/activate  # 对于Unix/MacOS系统

# 运行主应用程序
python src/main.py

# 查看可用选项
python src/main.py --help
```

## 代码结构
```
├── src/
│   ├── main.py              # 主入口点，处理CLI和工作流程
│   ├── ImageAnalyzer.py     # 图像处理和分析
│   ├── Models.py            # 用于配置的Pydantic模型
│   ├── filaments.py         # 灯丝库和参数
│   ├── to_stl.py            # 为CMYK层生成STL文件
│   ├── color_mixing.py      # 颜色混合算法
│   ├── generate_test_img.py # 测试图像生成
│   └── __init__.py
├── examples/                # 示例图像
├── stl-output/              # STL文件的默认输出目录
├── README.md                # 项目文档
├── pyproject.toml           # 依赖和项目配置
└── filaments.yaml           # 灯丝参数
```

## 主要工作流程 (src/main.py)
1. 解析CLI参数
2. 初始化ImageAnalyzer，将输入图像处理为CMYK层
3. 使用to_stl_cym()为每个颜色层生成STL文件
4. 将STL文件输出到指定目录

## 常用命令
```bash
# 使用默认设置运行
python src/main.py

# 使用自定义输入和输出运行
python src/main.py -i input/image.jpg -o output/processed.png --stl-output my-stls/

# 使用不同分辨率（0.2mm喷嘴）运行
python src/main.py -r 0.2 -i examples/test.png

# 显示处理后的图像
python src/main.py --show-images -i examples/girl-with-pearl-earings.png
```

## 项目待办 (来自README.md)
- 实现更优的减色混合模型
- 为灯丝参数添加yaml配置
- 将分辨率替换为喷嘴尺寸（0.2mm和0.4mm）
- 为无效输入图像实现错误处理
- 为长时间操作添加进度条
- 优化大图像的内存使用
- 为核心功能添加测试套件
- 重构/清理代码