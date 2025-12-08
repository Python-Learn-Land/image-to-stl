# STL 文件说明

该文件解释了 image-to-stl 程序生成的 STL 文件及其用途。

## 生成的 STL 文件

程序会生成 6 个 STL 文件（如 `stl-output/` 目录中所示）：

1. **white_base_mesh.stl** - 白色基础层
   这是3D模型的最底层，为后续所有颜色层提供一个平坦的基础。这个基础层的厚度是可配置的。

2. **cyan_mesh.stl** - 青色层
   该层代表CMYK颜色模型中的青色通道。网格的高度对应于每个像素中的青色强度。

3. **magenta_mesh.stl** - 品红色层
   该层代表CMYK颜色模型中的品红色通道。网格的高度对应于每个像素中的品红色强度。

4. **yellow_mesh.stl** - 黄色层
   该层代表CMYK颜色模型中的黄色通道。网格的高度对应于每个像素中的黄色强度。

5. **white_intensity_mesh.stl** - 白色强度层
   该层添加白色强度，以调整最终打印图像的整体亮度。高度对应于每个像素的亮度/明度。

6. **clear_mesh.stl** - 透明层
   这是最顶层，通过填补不同颜色强度之间的间隙来创建平坦的表面。它确保最终打印的对象具有光滑的顶部表面。

## 打印工作流程

要打印完整的3D图像，这些层应按以下顺序打印：

1. white_base_mesh.stl (第一层 - 底部)
2. cyan_mesh.stl (青色层)
3. magenta_mesh.stl (品红色层)
4. yellow_mesh.stl (黄色层)
5. white_intensity_mesh.stl (白色强度层)
6. clear_mesh.stl (最后一层 - 顶部)

每个颜色层使用相应的彩色灯丝打印，透明层使用透明灯丝打印。