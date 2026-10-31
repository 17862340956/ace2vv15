# Ace 2V / PHP110 901 实验源码

目标：OnePlus PHP110 / MT6983 / Android 15 / PHP110_15.0.0.1301(CN01)。基线：OnePlusOSS 901 源码候选，revision `qilin-php510-901-exp1`。本包不含预编译 KO。

## 上传
把本目录全部内容上传到新的 GitHub 仓库根目录，包含隐藏目录 `.github/workflows/build.yml`。不要加入旧 build_fast.sh 或 tools/ddk。

## 构建
运行 `PHP110 DDK direct module - original workflow style`。Actions 使用 `ghcr.io/ylarod/ddk:android12-5.10` 容器，容器提供目标 KDIR、clang 和 Module.symvers；然后用 `make KDIR="$KDIR" KCFLAGS=-g` 直接构建单个外部 KO。第二个 job 用 pyelftools 检查 callback DWARF、CFI、模块身份并打包手机文件。

这不是完整 1301 OEM 内核构建证明；生成 KO 后，只有 `cpuinfo_spoof.ko`、`build_report.json`、`run.sh` 三个配套文件一起使用。
