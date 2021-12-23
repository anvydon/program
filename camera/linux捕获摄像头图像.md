#### 问题描述

我希望能够使用终端上的网络摄像头拍照。然后该图像将保存到文件中。如何才能做到这一点？

#### 最佳解决方案

如果您正在寻找自动化webcam相当不错的东西。它有很多可爱的选项，可以通过互联网推送照片。

如果你想要更多的手动，我们谈论的是V4L /UVC支持的相机(大多数)你可以使用streamer从设备中捕获一个帧：

streamer -f jpeg -o image.jpeg

#### 次佳解决方案

还有另一个应用程序可用于从名为Fswebcam的网络摄像头捕获图像。你可以安装

`sudo apt-get install fswebcam`

您可以使用以下命令拍摄样本。

`fswebcam -r 640x480 --jpeg 85 -D 1 web-cam-shot.jpg`

在上面的代码语法中，-r代表图像分辨率，--jpeg代表图像的格式类型& 85质量标准，-D代表捕获前的延迟设置。

现在，您的图像最终以web-cam-shot.jpg名称保存。

希望有所帮助。

#### 第三种解决方案

使用avconv或ffmpeg，您也可以从设备中捕获帧。例如：

`avconv -f video4linux2 -s 640x480 -i /dev/video0 -ss 0:0:2 -frames 1 /tmp/out.jpg`

要么

`ffmpeg -f video4linux2 -s 640x480 -i /dev/video0 -ss 0:0:2 -frames 1 /tmp/out.jpg`

这将打开/dev/video0作为video4linux2兼容设备，设置分辨率为640x480，流2秒(00:00:02或简称2)，然后捕获one单帧，将其保存到/tmp/out.jpg。

检查您的设备是否为/dev/video0，因为它可能与您有所不同。

可用的分辨率取决于您的网络摄像头。我的功能达到了640×480，我用一个名为qv4l2的工具进行了检查，该工具用于配置video4linux2设备。

-ss参数用于允许设备正确启动。在我的测试中，在打开相机时有一个fade-in效果，因此，如果我只省略-ss 2，捕获的帧将会非常暗。
