#  AudioTrigger
## 💡 AudioTrigger是什么？
一个基于 **Windows 审计事件**与**任务计划**的游戏音频自动切换工具。
### ✨ 特点
- **零后台，零占用**，配置完即可关闭，功能完全由原生系统 + `SoundVolumeView` 实现
- **切换默认音频设备**
- **GUID精准识别**音频设备

## ❓ 为什么使用AudioTrigger？
对于平时用音响外放，个别游戏需要戴耳机的用户来说，每次都要手动切换音频设备，时间长了也会厌烦，是时候搞一点**自动化**了。
为了解决这个问题，我验证过两条可行路径：
- **系统自带的“应用音量和设备首选项”**。对于自动切换音源来说，它没有任何问题。然而，如果你需要使用英伟达录制或者重放功能，由于英伟达**只录制默认音频设备**，这会导致游戏声音录不进去。
- **SoundSwitch软件**。它可以提供一键切换默认音频设备的功能，比起手动点击切换方便了不少。它的不足有两点，一是**依然要手动操作**，二是会**占用后台**。
---
## ⚙️ AudioTrigger做了什么？
**前端设定任务内容** ➡️ **任务计划程序写入两条关于某游戏（程序）开启/关闭的计划** ➡️ **监控到游戏（程序）启动/关闭，触发任务** ➡️ **向SoundVolumeView下发切换默认音频设备的命令**
---
## 🛠️ 使用准备
- **操作系统**：Windows 10 / 11（需要**管理员权限**）
- **核心科技**：本项目基于 NirSoft 的经典命令行小工具 `SoundVolumeView` 实现默认设备切换。
- **关于SoundVolumeView**：出于开源版权规范，仓库源码中不直接附带该 `.exe`。请在 [SoundVolumeView 官网](https://www.nirsoft.net/utils/sound_volume_view.html) 下载64位版本，并将其与 `AudioTrigger.pyw` 放在同一个文件夹下。对于普通用户，我已经在 **Releases** 版本中集成了 `SoundVolumeView.exe`，直接下载使用即可。
---
## 📖 使用说明
### 普通用户（直接下载解压即用）
1. 去本仓库右侧的 **Releases** 页面，下载最新的 `AudioTrigger` 解压包。
2. 解压后，确保 `AudioTrigger.exe` 和 `SoundVolumeView.exe` 在**同一个文件夹**里。
3. 右键选择 **以管理员身份运行** `AudioTrigger.exe`（或者直接在兼容性里改成管理员启动，又或者直接双击启动，会有弹窗，因为没有管理员它是打不开的）。
4. 在右下角选择你的 **游戏设备(耳机)** 与 **日常设备(音箱)**。
5. 点击 **添加程序** 选中游戏（程序），再点击 ▶ 将其移入右侧 **自动处理列表**。
6. 直接关闭软件，这配置面板除非需要配置否则**根本不用再打开**。
### 开发者（从源码运行）
```bash
# 克隆仓库
git clone [https://github.com/Aby0N0/AudioTrigger.git](https://github.com/Aby0N0/AudioTrigger.git)
cd AudioTrigger
# 安装UI依赖
pip install customtkinter
# 运行源码
python AudioTrigger.pyw
# 别忘了自备SoundVolumeView
# （[https://www.nirsoft.net/utils/sound_volume_view.html](https://www.nirsoft.net/utils/sound_volume_view.html)）
```
---
## 📜 声明与致谢
- **开源协议**：本项目基于 **MIT License** 免费开源。
- **外部依赖**：特别感谢 **Nir Sofer** 开发的 `SoundVolumeView` 提供可靠的命令行音频切换支持。

<br>
<br>

---

# 🎧 AudioTrigger (English)
## 💡 What is AudioTrigger?
An automatic game audio switching tool based on **Windows Audit Events** and **Task Scheduler**.
### ✨ Features
- **Zero background process, zero footprint**. Once configured, it can be closed. The functionality is completely handled by the native system + `SoundVolumeView`.
- **Switches the default audio device.**
- **Precise device identification** via GUID.
---
## ❓ Why use AudioTrigger?
For users who normally use speakers but need headphones for specific games, manually switching audio devices every time can get annoying. It's time for some **automation**.
To solve this problem, I tested two alternative methods:
- **Windows built-in "App volume and device preferences"**. This works fine for automatically switching audio sources. However, if you use NVIDIA's recording or Instant Replay features, since NVIDIA **only records the default audio device**, your game audio won't be captured.
- **SoundSwitch software**. It provides a convenient hotkey to switch the default audio device, which is better than clicking through menus. But it has two drawbacks: first, it **still requires manual operation**, and second, it **occupies background resources**.
---
## ⚙️ How does AudioTrigger work?
**Set task details in the frontend** ➡️ **Write two tasks into the Windows Task Scheduler regarding the launch/close of a specific game (program)** ➡️ **Monitor the game's startup/shutdown to trigger the tasks** ➡️ **Send a command to SoundVolumeView to switch the default audio device**
---
## 🛠️ Prerequisites
- **OS**: Windows 10 / 11 (**Administrator privileges required**)
- **Core Technology**: This project is built on NirSoft's classic command-line utility, `SoundVolumeView`, to execute the default device switch.
- **About SoundVolumeView**: Due to open-source copyright guidelines, this repository does not include the `.exe` directly. Please download the 64-bit version from the [SoundVolumeView Official Website](https://www.nirsoft.net/utils/sound_volume_view.html) and place it in the same folder as `AudioTrigger.pyw`. For regular users, I have already integrated `SoundVolumeView.exe` in the **Releases** version—just download and use it directly.
---
## 📖 Usage Instructions
### Regular Users (Download, extract, and use)
1. Go to the **Releases** page on the right side of this repository and download the latest `AudioTrigger` zip file.
2. After extracting, make sure `AudioTrigger.exe` and `SoundVolumeView.exe` are in the **same folder**.
3. Right-click and select **Run as administrator** for `AudioTrigger.exe` (or set it to require admin rights in the compatibility tab, or just double-click it and accept the UAC prompt—it won't work without admin privileges).
4. In the bottom right corner, select your **Gaming Device (Headphones)** and your **Daily Device (Speakers)**.
5. Click **Add Program (添加程序)** to select your game, then click the ▶ button to move it into the **Auto Processing List (自动处理列表)** on the right.
6. Simply close the software. You **never need to open this configuration panel again** unless you want to add or change rules.
### Developers (Run from source)
```bash
# Clone the repository
git clone [https://github.com/Aby0N0/AudioTrigger.git](https://github.com/Aby0N0/AudioTrigger.git)
cd AudioTrigger
# Install UI dependencies
pip install customtkinter
# Run the source code
python AudioTrigger.pyw
# Don't forget to prepare SoundVolumeView yourself
# ([https://www.nirsoft.net/utils/sound_volume_view.html](https://www.nirsoft.net/utils/sound_volume_view.html))
```
---
## 📜 Disclaimer & Acknowledgements
- **Open Source License**: This project is free and open-source under the **MIT License**.
- **External Dependencies**: Special thanks to **Nir Sofer** for developing `SoundVolumeView`, which provides reliable command-line audio switching support.
