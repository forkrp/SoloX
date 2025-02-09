<p align="center">
  <a>中文</a> | <a href="./README.md">English</a>
</p>

<p align="center">
<a href="#">
<img src="https://cdn.nlark.com/yuque/0/2022/png/153412/1643364757640-b4529458-ec8d-42cc-a2d8-c0ce60fdf50f.png" alt="SoloX" width="150">
</a>
<br>
<br>

</p>
<p align="center">
<a href="https://pypi.org/project/solox/" target="__blank"><img src="https://img.shields.io/pypi/v/solox" alt="solox preview"></a>
<a href="https://pepy.tech/project/solox" target="__blank"><img src="https://static.pepy.tech/personalized-badge/solox?period=total&units=international_system&left_color=grey&right_color=orange&left_text=downloads"></a>
<br>
</p>

## 🔎简介

SoloX - Android/iOS性能数据的实时采集工具。

我们致力于解决低效、繁琐的测试执行问题，我们的目标是在【Simple Test In SoloX】

<img src="https://cdn.nlark.com/yuque/0/2022/png/153412/1662348054846-b0164165-e83a-443e-9a05-8c1f9ddb355f.png?x-oss-process=image%2Fresize%2Cw_1500%2Climit_0"  width="100%" >

## 📦环境

- 安装 Python 3.10 + [**Download**](https://www.python.org/downloads/)

- 安装 adb和配置好环境变量 (SoloX自带的adb不一定适配你的电脑，建议自己安装) [**Download**](https://developer.android.com/studio/releases/platform-tools)

💡 Python 3.6 ~ 3.9 , 请安装solox版本低于2.5.4.

💡 如果Windows用户需要测试iOS，请先安装Itunes. [**参考**](https://github.com/alibaba/taobao-iphone-device)

## 📥安装

### 默认

```shell
pip install -U solox 
```

### 镜像

```shell
pip install -i  https://mirrors.ustc.edu.cn/pypi/web/simple -U solox
```

💡 如果你的网络无法通过 [pip install -U solox] 下载, 可以尝试使用镜像下载，但是可能不是最新版本.

## 🚀启动SoloX

### 默认

```shell
python -m solox
```

### 自定义

```shell
python -m solox --host={ip} --port={port}
```

## 🏴󠁣󠁩󠁣󠁭󠁿使用python收集

```python

from solox.public.apm import APM
from solox.public.common import Devices

# solox version >= 2.1.2

d = Devices()
pids = d.getPid(deviceId='ca6bd5a5', pkgName='com.bilibili.app.in') # for android

apm = APM(pkgName='com.bilibili.app.in',platform='Android', deviceId='ca6bd5a5', 
          surfaceview=True, noLog=True, pid=None)
# apm = APM(pkgName='com.bilibili.app.in', platform='iOS') only supports one device
# surfaceview： False = gfxinfo (手机开发者 - GPU渲染模式 - adb shell dumpsys gfxinfo)
# noLog : False (为false时才会存储测试数据到log文件中)

# ************* 收集单个性能指标 ************* #
cpu = apm.collectCpu() # %
memory = apm.collectMemory() # MB
flow = apm.collectFlow(wifi=True) # KB
fps = apm.collectFps() # HZ
battery = apm.collectBattery() # level:% temperature:°C current:mA voltage:mV power:w
gpu = apm.collectGpu() # % only supports ios

# ************* 收集全部的性能指标 ************* #
apm = APM(pkgName='com.bilibili.app.i',platform='Android', deviceId='ca6bd5a5', 
          surfaceview=True, noLog=False, pid=None, duration=20) # duration : second
# apm = APM(pkgName='com.bilibili.app.in', platform='iOS',  noLog=False, duration=20)    
result = apm.collectAll()
```
```shell
[I 230504 10:40:30 common:179] Clean up useless files ...
[I 230504 10:40:30 common:185] Clean up useless files success
[I 230504 10:40:38 apm:362] cpu: {'appCpuRate': 15.15, 'systemCpuRate': 98.18}
[I 230504 10:40:38 apm:387] battery: {'level': 61, 'temperature': 35.0}
[I 230504 10:40:38 apm:412] fps: {'fps': 57, 'jank': 0}
[I 230504 10:40:38 apm:401] network: {'upFlow': 0.0, 'downFlow': 0.0}
[I 230504 10:40:38 apm:373] memory: {'totalPass': 170.05, 'nativePass': 57.72, 'dalvikPass': 10.63}
[I 230504 10:40:39 apm:387] battery: {'level': 61, 'temperature': 35.0}
[I 230504 10:40:39 apm:412] fps: {'fps': 50, 'jank': 3}
[I 230504 10:40:39 apm:401] network: {'upFlow': 1.0, 'downFlow': 0.65}
[I 230504 10:40:40 apm:362] cpu: {'appCpuRate': 9.56, 'systemCpuRate': 98.68}
[I 230504 10:40:40 apm:373] memory: {'totalPass': 262.14, 'nativePass': 64.87, 'dalvikPass': 13.16}
[I 230504 10:40:40 apm:412] fps: {'fps': 50, 'jank': 3}
[I 230504 10:40:40 apm:387] battery: {'level': 61, 'temperature': 35.0}
[I 230504 10:40:41 apm:401] network: {'upFlow': 0.0, 'downFlow': 0.22}
[I 230504 10:40:41 apm:373] memory: {'totalPass': 262.34, 'nativePass': 65.58, 'dalvikPass': 13.32}
[I 230504 10:40:43 apm:401] network: {'upFlow': 0.0, 'downFlow': 0.0}
[I 230504 10:40:43 apm:362] cpu: {'appCpuRate': 4.7, 'systemCpuRate': 99.68}
[I 230504 10:40:44 apm:387] battery: {'level': 61, 'temperature': 35.0}
[I 230504 10:40:44 apm:412] fps: {'fps': 50, 'jank': 3}
[I 230504 10:40:44 apm:401] network: {'upFlow': 0.0, 'downFlow': 0.22}
[I 230504 10:40:44 apm:373] memory: {'totalPass': 261.59, 'nativePass': 64.71, 'dalvikPass': 13.46}
[I 230504 10:40:45 apm:362] cpu: {'appCpuRate': 4.75, 'systemCpuRate': 101.1}
[I 230504 10:40:45 apm:387] battery: {'level': 61, 'temperature': 35.0}
[I 230504 10:40:45 apm:412] fps: {'fps': 50, 'jank': 3}
[I 230504 10:40:45 apm:401] network: {'upFlow': 0.07, 'downFlow': 0.0}
[I 230504 10:40:46 apm:373] memory: {'totalPass': 261.62, 'nativePass': 64.7, 'dalvikPass': 13.49}
[I 230504 10:40:52 common:300] Generating test results ...
[I 230504 10:40:52 common:320] Generating test results success: D:\github\SoloX\report\apm_2023-05-04-10-40-52
[I 230504 10:40:52 common:219] Generating HTML ...
[I 230504 10:40:52 common:237] Generating HTML success : D:\github\SoloX\report\apm_2023-05-04-10-40-52\report.html
```

## 🏴󠁣󠁩󠁣󠁭󠁿使用API收集

### 后台启动服务
```
# solox version >= 2.1.5

macOS/Linux: nohup python3 -m solox &
Windows: start /min python3 -m solox &
```

### 通过api请求数据

```shell
Android: http://{ip}:{port}/apm/collect?platform=Android&deviceid=ca6bd5a5&pkgname=com.bilibili.app.in&target=cpu
iOS: http://{ip}:{port}/apm/collect?platform=iOS&pkgname=com.bilibili.app.in&target=cpu

target in ['cpu','memory','network','fps','battery','gpu']
```

## 🔥功能

* **无需ROOT/越狱:** Android设备无需ROOT，iOS设备无需越狱。高效解决Android & iOS性能测试分析难题。

* **数据完整性:** 可提供FPS、Jank、CPU、GPU、Memory、Battery 、Network等性能参数，这些您都可以轻松获得。

* **美观的报告看板:** 报告看板，您可以随时随地存储、可视化、编辑、管理和下载使用任何版本的SoloX收集的所有测试数据。

* **好用的监控设置:** 支持在监控过程中设置告警值、收集时长、访问其他PC机器的移动设备。

* **比对模式:** 支持两台移动设备同时对比测试。
  - 🌱2-devices: 使用两台不同的设备测试同一个app。
  - 🌱2-apps: 使用两台配置相同的设备测试两个不同的app。

## 浏览器

<img src="https://cdn.nlark.com/yuque/0/2023/png/153412/1677553244198-96ce5709-f33f-4038-888f-f330d1f74450.png" alt="Chrome" width="50px" height="50px" />

## 终端

- windows: PowerShell
- macOS：iTerm2 (https://iterm2.com/)

## 💕感谢

- https://github.com/alibaba/taobao-iphone-device
