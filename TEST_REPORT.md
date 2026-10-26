# Assignment-2 测试报告

- 姓名：李昌恒
- 学号：3220262758
- 验证日期：2026-10-26（Asia/Shanghai）
- 环境：WSL Ubuntu 22.04，GNU C++ 11.4，CMake 3.28.3，SVF 3.1，Clang/LLVM 16.0.4。
- 结论：实际 C++ 项目构建成功；本仓库 5 个原始用例和 6 个回归用例共 11/11 个测试通过，均已重复运行核对输出一致性。

## 验证方法

使用 Clang 16 的 `-O0 -g -emit-llvm -c` 将 C 用例编译为 bitcode；运行实际构建的 `cfga -dump-icfg`。验证脚本解析 SVF 生成的 `icfg_initial.dot`，识别普通边、调用边、返回边及其调用点，使用独立的 Python 搜索计算参考路径集合，与 `.bc.res.txt` 完整比较，同时校验固定的预期路径数与路径去重。

`multi-call` 和 `nested-repeat` 确认顺序调用没有被跳过；`branch`、`branch-merge` 确认分支路径保留且返回点匹配；递归用例检验既定的递归截断策略；`no-exit` 确认没有 main 出口时结果为空。

## 测试结果

| Test set | Case | Paths | Result |
|---|---|---:|---|
| Assignment-2 | branch.c | 2 | PASS |
| Assignment-2 | buffer.c | 4 | PASS |
| Assignment-2 | loop.c | 1 | PASS |
| Assignment-2 | multi-call.c | 1 | PASS |
| Assignment-2 | simple-call.c | 1 | PASS |
| regression | nested-repeat.c | 1 | PASS |
| regression | branch-merge.c | 2 | PASS |
| regression | recursive-repeat.c | 4 | PASS |
| regression | mutual-recursion.c | 3 | PASS |
| regression | no-exit.c | 0 | PASS |
| regression | external.c | 1 | PASS |

## 适用范围

这些是有限 ICFG 路径测试，不求解分支条件，也不枚举循环任意次数和无界递归。循环中的重复 `(节点, 调用栈)` 状态被截断；递归中的重复活动调用点被截断。因此，例如 buffer 的 4 条结构路径不等价于 4 条满足参数和循环条件的真实运行轨迹。实际测试集路径与来源见 tests/SOURCES.md。

## 复现

在仓库根目录按 README.md 配置 SVF_DIR 和 LLVM_DIR 并构建，然后执行：

```bash
python3 tests/verify_paths.py \
  --cfga ./Assignment-2-CFA/cfga \
  --clang "$LLVM_DIR/bin/clang" \
  --out ../verification
```

每个测试目录保存 bitcode、SVF 图、路径结果和工具日志；最终汇总为 verification/results.md。
