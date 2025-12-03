# Color Lithophane 项目

这个项目可以帮助你准备和切片3D彩色照片浮雕(Lithophane)。

需要考虑的几个要点：
* 简单的CMYK颜色和简单的减色混合
* 支持0.2mm和0.4mm喷嘴

## 示例

![示例1](./examples/example_printed.png)

## 安装

1. 初始化UV环境：

```bash
uv venv
source .venv/bin/activate # 对于 Unix/MacOS
```

## 运行项目

从UV环境执行主脚本：

```bash
python src/main.py
```

## 生成选项

```bash
$ python src/main.py  --help
usage: main.py [-h] [--show-images] [--input INPUT] [--output-image OUTPUT_IMAGE] [--width WIDTH] [--resolution RESOLUTION]
               [--stl-output STL_OUTPUT]

将图像处理为CMYK 3D可打印层

options:
  -h, --help            显示帮助信息并退出
  --show-images         显示原始图像和处理后的图像
  --input, -i INPUT     输入图像文件路径
  --output-image, -o OUTPUT_IMAGE
                        输出像素化图像文件路径
  --width, -w WIDTH     所需的宽度（以毫米为单位）
  --resolution, -r RESOLUTION
                        分辨率（以毫米/像素/块为单位）
  --stl-output STL_OUTPUT
                        STL文件的输出目录
```


```
python src/main.py --input examples/color_test_chart.png --output-image examples/color_test_chart_show.png --width 100 --resolution 0.4 --stl-output stl-output/

```

## Bambu Studio 设置

1. 启动 Bambu Studio
2. 文件 → 导入 → 选择示例文件（支持 .stl, .obj, .3mf）
3. 选择所有4个生成的文件进行导入
   - 当提示将所有文件作为具有多个部分的单个对象加载时，点击"是"。

### 打印设置

配置以下设置以获得最佳结果：

- 喷嘴直径：0.4mm
- 第一层高度：0.2mm
- 后续层高度：0.1mm

## 项目待办事项

### 混合算法
- [x] 实现传输距离模型
- [ ] 实现更优的减色混合模型

### 可用性
- [ ] 为灯丝参数添加 yaml 配置
- [ ] 用喷嘴尺寸（0.2mm 和 0.4mm）替换分辨率参数
- [ ] 为无效的输入图像实现错误处理
- [ ] 为长时间操作添加进度条
- [ ] 优化大图像的内存使用

### 沟通
- [ ] 为参数提供更好的文档
- [ ] 创建常用灯丝库
- [ ] 创建带有样本打印的示例库
- [ ] 添加校准图案生成功能
- [ ] 创建故障排除指南

### 通用
- [ ] 为核心功能添加测试套件
- [ ] 添加对Web服务器托管的支持
- [ ] 重构/清理代码