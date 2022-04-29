![语言](https://img.shields.io/badge/语言-python-7A50ED.svg) 

## TinyPNG-kmeans

另一个 PNG 图像压缩器，压缩率\&质量可调，效果好于 [tinypng.com](https://tinypng.com/) ！ 摆脱 [tinypng.com](https://tinypng.com/) 的文件数量限制。

与 [tinypng.com](https://tinypng.com/) 类似，本代码将色彩数=16777216的真彩色图像（24位）量化为色彩数≤256的调色板图像，来达到大于 3 倍的压缩比。不同的是，我用的量化算法是 K-Means ，效果好于 [tinypng.com](https://tinypng.com/) ：在相同压缩率下图像失真更小，在相同失真下压缩率更高。

### 安装依赖

首先需要安装 Python 3.x 以及其配套的 Pillow (PIL) 、 numpy 、 scipy 、scikit-learn (sklearn) 库。

如果你已有 Python 3.x ，运行以下命令安装这些库：

```powershell
python -m pip install Pillow==8.4.0
python -m pip install numpy==1.20.3
python -m pip install scipy==1.8.0
python -m pip install scikit-learn==0.24.2
```

如果你还没有 Python ，你可以直接安装 [Anaconda](https://www.anaconda.com/products/distribution) ，它包含 python 和上述库。

### 使用方法

运行以下命令：

```powershell
python tinypng.py <输入目录名> <输出目录名> <P>
```

它会把输入目录中的所有图像文件（包括 png, jpg, tiff 等各种图像格式）压缩成 png 格式，放在输出目录中（对于一些本身就高度压缩的 jpg 图像，生成的 png 会比原始文件都大，程序会跳过这种文件）。**P值**则是**色彩数**，取值范围是 `P∈[2,256]` ，越小则压缩率越高，图像失真也越大。

比如用以下命令来压缩我提供的示例图像（在 [image](./image) 目录中），放到 [image_tiny]() 目录中，`P=100` ：

```powershell
python tinypng.py image image_tiny 100
```

> 对一般的图像、照片可以取 `P∈[100,256]` ，对色彩较少的图像（比如平面设计），可取 `P∈[2,99]` 来获得更好的效果。

### 效果展示

对 [image](./image) 目录中的图像，分别用 [tinypng.com](https://tinypng.com/) 和本代码（取几种**不同P值**）进行压缩，下表部分展示了它们的压缩率（压缩率=原始图像文件大小/压缩后图像文件大小）。

   *表：**压缩率***

| 文件名     | [tinypng.com](https://tinypng.com/) | 本代码 P=256 | 本代码 P=150 | 本代码 P=110 | 本代码 P=50 |
| ---------- | :---------------------------------: | :----------: | :----------: | :----------: | :---------: |
| img12.png  |                3.31                 |     3.54     |     4.28     |     4.86     |    7.11     |
| img13.png  |                3.01                 |     2.87     |     3.45     |     3.65     |    4.92     |
| img23.png  |                1.95                 |     2.65     |     3.06     |     3.57     |    4.56     |
| img24.png  |                2.62                 |     2.77     |     3.24     |     3.60     |    4.58     |
| img25.png  |                2.40                 |     2.57     |     2.67     |     2.60     |    2.96     |
| **总平均** |              **2.71**               |   **2.72**   |   **3.18**   |   **3.51**   |  **4.64**   |

为了衡量图像失真，我计算并展示了原始 PNG 图像和压缩后的 PNG 图像的 SSIM 值（结构相似性）如下表。SSIM∈[0.0, 1.0] ，越大说明相似度越高，失真越小。

   *表：**失真**（SSIM值）*

| 文件名     | [tinypng.com](https://tinypng.com/) | 本代码 P=256 | 本代码 P=150 | 本代码 P=110 | 本代码 P=50 |
| ---------- | :---------------------------------: | :----------: | :----------: | :----------: | :---------: |
| img12.png  |               0.9708                |    0.9864    |    0.9807    |    0.9764    |   0.9647    |
| img13.png  |               0.9968                |    0.9972    |    0.9957    |    0.9947    |   0.9908    |
| img23.png  |               0.9685                |    0.9931    |    0.9898    |    0.9864    |   0.9799    |
| img24.png  |               0.9738                |    0.9847    |    0.9788    |    0.9740    |   0.9609    |
| img25.png  |               0.9986                |    0.9990    |    0.9987    |    0.9994    |   0.9989    |
| **总平均** |             **0.9770**              |  **0.9865**  |  **0.9812**  |  **0.9773**  | **0.9647**  |

可以明显看出本代码相比 [tinypng.com](https://tinypng.com/) 的优势：在相同压缩率下图像失真更小，在相同失真下压缩率更高。

我也提供了计算 SSIM 的代码文件 ssim.py ，运行方法是：

```powershell
python ssim.py <原始图像目录> <原始图像格式> <压缩图像目录> <压缩图像格式>
```

比如以下命令会计算 [image](./image) 目录中的 png 图像和 [image_tiny]() 目录中的同名的 png 图像的 SSIM 值：

```powershell
python ssim.py image png image_tiny png
```

