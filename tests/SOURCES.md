# 测试集来源

- Assignment-2：<https://github.com/lichard97/Assignment-2>，基准提交 `7281b16677b11b8b22bfeba24fc32c0a709963b2`。原始 5 个 C 用例保留在 `Assignment-2-CFA/Test-Cases`。
- Assignment-3：<https://github.com/lichard97/Assignment-3>，基准提交 `76f95c3928316019a0def9c30e807c2c5d7b7dca`。原始 8 个 C 用例从 `Assignment-3-CFLR/Test-Cases` 原样复制到 `tests/reference/Assignment-3-CFLR/Test-Cases`。遵循原仓库 GPL-3.0 许可，许可文本见仓库根目录 `LICENSE`。
- `tests/regression`：本次补充的 6 个 C 回归用例，用于验证重复调用、分支汇合、递归截断、无出口和外部调用。
- `tests/verify_paths.py`：本次添加的集成验证脚本。

两份指定仓库在上述版本均不含图片中的 `Assignment-3-IR/Test-Cases`。本次使用真实存在的上述目录，未将它们冒充为该目录，也未取得另一个未指定仓库的测试集。

这些测试检验 CFGA 的控制流路径与调用返回匹配；不检验 Assignment-3 中 CFLR 的别名分析断言。Assignment-3 的别名测试函数在本任务中作为外部调用处理。
