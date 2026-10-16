# Manim 制作指南

用于数学、几何、算法流程和科研方法的编程动画。官方来源见 [来源记录](3blue1brown-sources.md)。先确定讲解目标和分镜，再写场景。

## 1. 确定版本

| 项目 | Manim Community | ManimGL |
|---|---|---|
| 维护方 | Manim Community | Grant Sanderson / 3b1b |
| 仓库 | `ManimCommunity/manim` | `3b1b/manim` |
| Python 包 | `manim` | `manimgl` |
| 导入 | `from manim import ...` | `from manimlib import ...` |
| 常用命令 | `python -m manim scene.py SceneName` | `manimgl scene.py SceneName` |
| 采用条件 | 新建本 skill 的解释动画，默认选用 | 用户指定、已有 GL 工程、复现作者自身工作流 |

记录实际版本与渲染器。读旧博客或 3b1b 视频源码时先检查版本，不能直接把 GL 代码粘到 Community 工程。Community 自身也有 OpenGL 渲染器；选择 `--renderer opengl` 并不会将它变成 ManimGL。

## 2. 环境检查与最小起步

先检查项目已有环境，选择合适的 Python 创建项目独立环境。以下命令为 Windows PowerShell 示例，其他系统使用相应的虚拟环境路径。

检查项：Python 路径与版本、Manim 分支及版本、中文字体、目标渲染器。只有需要 `MathTex/Tex` 时才检查 TeX 编译器及 `dvisvgm`。Community 的文字使用 Pango；中文可以通过 `Text` 直接渲染。当前版 Community 通过 PyAV 处理音视频，不把“PATH 中没有 ffmpeg”自动判为无法运行；本 skill 使用 FFmpeg 后处理时另行检查。版本变化后以该版本官方安装资料与实际冒烟渲染为准。

本 skill 提供自写的 [二维投影场景](../assets/manim_scene.py) 与 [测试版本要求](../assets/requirements-manim.txt)。它包括中文、固定点云、转轴、投影和残差；使用 `Text`，不需要 TeX。数学量从固定示意点实际计算。

在制作项目中复制模板，环境已有依赖时直接低清渲染。下列命令以项目当前目录为基准；若已有环境或使用其他目录，替换路径：

```powershell
$basePython = (Get-Command python -ErrorAction Stop).Source
& $basePython -m venv '.venv'
$scenePython = (Resolve-Path -LiteralPath '.venv\Scripts\python.exe').Path
& $scenePython -m pip install -r '.\requirements-manim.txt'
& $scenePython -m manim --version
& $scenePython -m manim -ql --renderer cairo --media_dir '.\media' '.\manim_scene.py' ProjectionExplainer
```

这是假定已将两个资产文件复制到项目的命令，不是请求分析或写分镜时的自动安装动作。可以按官方流程使用现有 `uv` 完成独立环境与依赖安装；使用 PowerShell 时保留原生程序的参数边界，使用调用运算符与参数数组直接运行程序。测试版本文件用于复现实测模板，升级时重新渲染验证。

## 3. 解释动作对应到代码

先按 [让动作承担推理](motion-design.md) 把旁白中的操作落实为状态变化。主要机制场景使用可独立渲染的 Scene 类，便于局部试制和替换。先做最难的一镜，再扩充全片。

| 教学目的 | Community 常用对象／机制 | 要核对的关系 |
|---|---|---|
| 逐块建立流程 | `VGroup`、`Create`、`FadeIn`、`LaggedStart` | 每个模块出现时说明它解决什么问题 |
| 保留对象的身份 | `Transform`、`ReplacementTransform` | 是否让观众追踪同一个对象 |
| 公式项对应 | `MathTex`、`TransformMatchingTex` | 匹配的符号是否表示同一数学量 |
| 变量驱动多视图 | `ValueTracker`、`always_redraw`、`add_updater` | 图形、数值、标记来自同一个变量 |
| 坐标变换／投影 | `NumberPlane`、`Axes`、向量和点 | 转轴与移动点要区分；投影和残差方向正确 |
| 场与迭代轨迹 | `ArrowVectorField`、路径／点 | 示意与真实计算清楚标注 |
| 放大局部 | `MovingCameraScene`、camera frame | 保留位置参照；字幕随镜头保持可读 |
| 三维空间解释 | `ThreeDScene`、`ThreeDAxes` | 相机、世界坐标与屏幕标签明确 |

以上接口属于 Community，按安装版本查官方 API。不要为每个普通标题加入 `Write` 或大幅旋转；`Create` 表示构造，`Transform` 表示对象改变，运动要承担解释。

## 4. 联动状态

用一个 tracker 描述可变条件，依赖对象从它的值计算。例如一个点移动时，连线端点、投影点、面积与显示数值应一起更新。

```python
alpha = ValueTracker(0)
moving_point = always_redraw(
    lambda: Dot(plane.c2p(*(p + alpha.get_value() * (q - p))))
)
self.add(moving_point)
self.play(alpha.animate.set_value(1), run_time=3, rate_func=linear)
moving_point.clear_updaters()
```

连续物理或数学参数需要观察均匀变化时用 `linear`；入场、强调可以使用适当的缓动。生成大点云或热力图时预计算固定样本，避免每帧重新运行模型；通常移动已有对象比重建整张复杂图更合适。

`always_redraw` 适合小图形。文本或复杂对象每帧重建成本较大，数值可以使用 `DecimalNumber` 更新；停止联动后清除 updater，再做替换或退出动画。

## 5. 中文、公式和颜色

- 中文口播对应文字使用 `Text/MarkupText`，明确选择已安装字体并检查实际输出；可用 `manimpango.list_fonts()` 查看名字。本模板优先查找 Microsoft YaHei，再尝试其他中文字体。
- 数学公式用 `MathTex`。在安装 TeX 与 `dvisvgm` 后先渲染一个短公式，确认实际路径；将符号拆为语义单位，例如 `MathTex(r"x_t", "=", r"(1-t)x_0", "+", r"t\epsilon")`，按角色着色。
- `TransformMatchingTex` 可以表达相同变量的延续。只对真实对应项做变换，解释抵消时让抵消项可见；不要靠动画暗示不成立的等式。
- 中文不要随意塞进默认 `MathTex`。确需中文 TeX 时单独设置支持中文的模板及编译器并实测，否则用 `Text` 标签配数学公式。
- 公式字体、中文字重、颜色和留白要服务目标屏幕。黑底和衬线公式可作为风格起点，手机观看应检查字号。重点角色在图形和公式中同色，同时保留名字或形状。

## 6. 旁白与分段剪辑

将长旁白拆成对应操作的短节拍；必要时每句独立音频。动作占用其中一段，留下读图停顿，不用“每段开头固定动画几秒，其余全部等待”的通用封装代替节拍设计。从实际 `self.time` 记录语音起止与动作区间，或用输出片段的实际时长拼装字幕和章节；以帧时钟为准。

没有 TeX 且环境能产出数学 SVG 时，可将每个语义项独立生成 SVG，再用 `SVGMobject` 分组、着色和显式匹配。保持上下标、基线和符号含义，先做短试镜。整体公式 PNG 可用于引用或定格；关键变量替换与系数对应保留为独立对象。

每个机制场景保留进入定位、关键变化和结束读图三段。先用 `self.play(..., run_time=...)` 与 `self.wait(...)` 排出预期节拍，再根据实际音轨修订；每个片段记录其讲稿、预计时长和成片起点。

Manim 可以加入声音，但无需把配音、字幕和整片剪辑全部塞入 Scene。遵循作者所述的片段制作方式：Manim 输出机制片段，剪辑阶段配旁白、字幕和上下文。已有配音工具时沿用它；只要求分镜时交付分镜，不自动生成音频。

## 7. 渲染与验收

1. 使用 `-ql` 完成低清粗片，修正几何、文字与镜头顺序。
2. 对关键变化抽取开始／中间／结束帧，检查身份、方向、遮挡和字幕区域，再播放该段检查动态。公式多时检查符号是否误配。
3. 口播确定后校准停留与动作；检查实际同步，避免口播介绍对象时该对象尚未出现。
4. 已通过粗片后按目标质量渲染。例如 Community 的 `-qh` 通常是 1080p60；若目标30 fps，显式使用 `--fps 30`，并检查当前版 CLI 设置。保持成片各片段尺寸、帧率和音频规格一致。
5. 交付场景源代码、环境版本／依赖文件、成片及需要的素材来源。低清样例、静音片段与配音成片分别说明。

本 skill 的普通 Manim 场景按序列渲染。浏览器演示的任意时间拖动是另一种交互能力，不以它作为所有 Manim Scene 的要求。

## 本次模板验证

2026-10-09 在独立环境使用 Python 3.12.0、Manim Community 0.22.0、Cairo、Microsoft YaHei，成功渲染 `ProjectionExplainer` 为约14.93秒的854×480静音预览，并按0.5秒采样检查30个状态。主方向从固定点云计算；投影点落在主轴，残差与主轴正交，数值误差小于 `1e-12`。

此验证覆盖中文、二维场景、tracker、updater、坐标旋转、投影、残差和MP4输出。模板没有使用 `MathTex`、三维相机或配音；对应功能需要在实际项目中单独验证。
