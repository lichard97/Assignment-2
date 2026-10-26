## Assignments for Introduction to Static Program Analysis.

**姓名：李昌恒**

**学号：3220262758**

### Assignment-2 完成说明

- 完成文件：`Assignment-2-CFA/CFGA.cpp` 中的 `CFGAnalysis::analyze`。
- 从 `main` 的入口节点开始 DFS，到 `main` 的出口节点记录完整节点序列，调用已有的 `recordPath` 和 `dumpPaths` 输出结果。
- 遍历 `CallCFGEdge` 时，将调用点 ID 压入 `callStack`；仅在 `RetCFGEdge` 的调用点与栈顶相同时返回，遍历后恢复栈，避免不同调用点之间错误返回。
- 用当前路径上的 `(节点 ID, 调用栈)` 状态检测循环；回溯时删除状态，使分支汇合后仍能分别记录路径，也允许同一函数被不同调用点重复调用。
- 每次分析前清空已有结果和调用栈，输出沿用原项目的 `<input-bitcode>.res.txt` 格式。

图片中的 `Assignment-3-CFA/CFGA.cpp` 在这两个仓库中不存在，对应的实际待补全文件为本仓库的 `Assignment-2-CFA/CFGA.cpp`。图片中的 `Assignment-3-IR/Test-Cases` 也不存在；测试使用本仓库 `Assignment-2-CFA/Test-Cases` 的 5 个用例，并补充另一个仓库 `Assignment-3-CFLR/Test-Cases` 的 8 个用例。没有修改 Assignment-3 的 CFLR 作业实现。

### 路径语义与边界

本实现枚举 ICFG 中有限的控制流路径，不求解分支条件，也不展开循环的任意迭代次数。同一调用上下文中重复出现的节点会被截断，因此循环测试保留不经过回边的路径；它不表示循环的所有运行轨迹。对于递归，仅允许每个调用点在当前调用栈中出现一次，重复调用点的递归边被截断，以保证分析终止；这不是无界递归的完备可达性分析。返回后可再次使用该调用点。

外部函数遵循 SVF 建立的普通调用到返回边。间接调用能覆盖的目标取决于输入 ICFG；本作业未额外运行指针分析来解析函数指针。

### 构建与运行

依赖：Linux / WSL、CMake >= 3.23、C++17 编译器、SVF 3.1、LLVM 16 和 Z3。以下路径应替换为实际安装位置：

```bash
export SVF_DIR=/path/to/svf31
export LLVM_DIR="$SVF_DIR/llvm-16.0.0.obj"
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build -j4

"$LLVM_DIR/bin/clang" -O0 -g -emit-llvm -c \
  Assignment-2-CFA/Test-Cases/multi-call.c -o multi-call.bc
./Assignment-2-CFA/cfga multi-call.bc
cat multi-call.bc.res.txt
```

原项目的 `./build.sh` 也可以用于构建。若输入的 bitcode 带有目录，结果文件同样位于该目录。

### 自动验证

本仓库已附上 Assignment-3 的原始测试集副本，无需另行下载即可运行：

```bash
python3 tests/verify_paths.py \
  --cfga ./Assignment-2-CFA/cfga \
  --clang "$LLVM_DIR/bin/clang" \
  --out ../verification
```

如需使用独立克隆的 Assignment-3，可增加 `--assignment3 ../Assignment-3`。测试集来源与版本见 `tests/SOURCES.md`。

验证脚本使用真实的 `cfga` 程序和 SVF 输出的 `icfg_initial.dot`，独立解析调用边、返回边及对应调用点，比较参考路径集合与结果文件，并检查预期路径数和重复运行的一致性。另外包含嵌套重复调用、分支汇合、自递归、互递归、无出口和外部调用 6 个回归用例。共 19 个用例已全部通过；详细运行结果见 `TEST_REPORT.md`。

### 原项目说明

- After completing the code assignemts in the corresponding subdirectories, you can go to the root direction, i.e., `Assignments/`, and type:

	- `./build.sh`: to compile and build the code in all subdirectories; or
	- `./build.sh [list_of_directories]`: to compile and build the code in the subdirectories you specified.

- After running `./build.sh`, an executable is expected to be in each corresponding subdirectory.

- Then, you can use the test cases in `Assignment.../Test-Cases` to check whether you code is correct.

#### Note:
Every time you upload your assignments, please attach your **NAME** and **STUDENT ID** to this README file!
