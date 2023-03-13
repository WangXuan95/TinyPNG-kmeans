![语言](https://img.shields.io/badge/语言-python-7A50ED.svg) 

# TinyPNG-kmeans

一个 Python 程序，帮助你缩小 PNG 图像文件的大小 (类似 [tinypng.com](https://tinypng.com/)) 。优点有：

- 效果更好：相比 [tinypng.com](https://tinypng.com/) ，同样的画质下压缩率更高。
- 可调：通过调整参数，用画质换取更高的压缩率。
- 摆脱 [tinypng.com](https://tinypng.com/) 的文件数量限制。

　

## 原理简介

### 色域量化

与 [tinypng.com](https://tinypng.com/) 类似，本代码将色彩数=16777216 的24位真彩色像素量化为色彩数≤256的调色板像素，从而达到大于 3 倍的压缩比。不同的是，本代码用 K-Means 聚类算法进行量化。

### Deflate 极限压缩

本代码还调用了 [OptiPNG](https://optipng.sourceforge.net/) 。它会重新对 PNG 的 Deflate 压缩过程进行优化，从而达到更大的压缩比。

　

## 安装依赖

需要安装 Python 3.x 以及其配套的 Pillow (PIL) 、 numpy 、 scipy 、scikit-learn (sklearn) 库。

如果你已有 Python 3.x ，运行以下命令安装这些库：

```powershell
python -m pip install Pillow==8.4.0
python -m pip install numpy==1.20.3
python -m pip install scipy==1.8.0
python -m pip install scikit-learn==0.24.2
```

如果你还没有 Python ，你可以直接安装 [Anaconda](https://www.anaconda.com/products/distribution) ，它包含 python 和上述库。

另外，在使用时，要保证 `optipng.exe` 与 `tinypng.py` 在同一个目录下

　

## 使用方法

在 `tinypng.py` 所在的目录下运行命令：

```powershell
python tinypng.py <输入目录名> <输出目录名> <P>
```

它会把输入目录中的所有图像文件 (包括 png, jpg, tiff 等各种图像格式) 压缩成 png 格式，放在输出目录中 (对于一些本身就高度压缩的 jpg 图像，生成的 png 会比原始文件都大，程序会跳过这种文件) 。**P值**则是**色彩数**，取值范围是 `P∈[2,256]` ，越小则压缩率越高，图像失真也越大。

比如用以下命令来压缩 [image](./image) 目录中的图像，放到 [image_tiny]() 目录中，`P=100` ：

```powershell
python tinypng.py image image_tiny 100
```

> 对一般的图像、照片可以取 `P∈[100,256]` 。对色彩较少的图像（比如平面设计），可取 `P∈[2,99]` 来获得更好的效果。

　

## 效果展示

对 [image](./image) 目录中的图像，分别用 [tinypng.com](https://tinypng.com/) 和本代码 (取几种**不同P值**) 进行压缩，下表部分展示了总压缩率和平均失真。其中压缩率=原始图像文件大小/压缩后图像文件大小) 。而失真用 SSIM 值 (结构相似性) 来衡量，SSIM∈[0.0, 1.0] ，越大说明相似度越高，失真越小。

   表： [tinypng.com](https://tinypng.com/) 和本代码的对比

| 文件名            | [tinypng.com](https://tinypng.com/) | 本代码 P=256 | 本代码 P=150 | 本代码 P=110 | 本代码 P=50 |
| ----------------- | :---------------------------------: | :----------: | :----------: | :----------: | :---------: |
| **压缩率**        |                2.71                 |     2.88     |     3.37     |     3.69     |    4.93     |
| **画质 (SSIM值)** |               0.9770                |    0.9865    |    0.9812    |    0.9773    |   0.9647    |

从上表可以明显看出本代码相比 [tinypng.com](https://tinypng.com/) 的优势：在相同压缩率下图像失真更小，在相同失真下压缩率更高。

我也提供了计算 SSIM 的代码文件 ssim.py ，运行方法是：

```powershell
python ssim.py <原始图像目录> <原始图像格式> <压缩图像目录> <压缩图像格式>
```

比如以下命令会计算 [image](./image) 目录中的 png 图像和 [image_tiny]() 目录中的同名的 png 图像的 SSIM 值：

```powershell
python ssim.py image png image_tiny png
```

