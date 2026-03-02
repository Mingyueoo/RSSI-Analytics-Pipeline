# 项目修改总结

## 修改日期
2026-03-02

## 修改内容

### 1. 创建配置文件系统
- ✅ 创建 `config/config.yaml` - 集中管理所有配置
  - 路径配置（数据目录、结果目录等）
  - 设备 UUID 映射
  - 场景名称映射
  - 分析参数（时间容差、RSSI 范围）
  - 绘图样式和颜色配置

### 2. 创建工具模块
- ✅ 创建 `src/utils.py` - 配置加载和目录管理工具
  - `load_config()` - 加载 YAML 配置文件
  - `ensure_dirs()` - 自动创建必要的目录

### 3. 重构数据加载模块
- ✅ 修改 `src/data_loader.py`
  - 将主逻辑封装为 `process_rssi_data()` 函数
  - 使用配置文件中的路径
  - 使用配置文件中的时间容差参数
  - 支持作为模块导入或独立运行

### 4. 重构电池分析模块
- ✅ 修改 `src/battery_analyzer.py`
  - 添加 `initialize_plotting_style()` 初始化函数
  - 使用配置文件中的路径
  - 使用配置文件中的绘图样式和颜色
  - 使用配置文件中的 DPI 设置
  - `main()` 函数接受 `config` 参数

### 5. 重构模式分析模块
- ✅ 修改 `src/mode_analyzer.py`
  - 添加 `initialize_plotting_style()` 初始化函数
  - 使用配置文件中的设备映射
  - 使用配置文件中的场景映射
  - 使用配置文件中的路径和绘图配置
  - `main()` 函数接受 `config` 参数

### 6. 重构可视化模块
- ✅ 修改 `src/visualization.py`
  - 修改 `RSSIAnalyzer` 类接受 `config` 参数
  - 添加 `_initialize_plotting_style()` 方法
  - 使用配置文件中的设备映射
  - 使用配置文件中的场景映射
  - 使用配置文件中的路径和颜色配置
  - 所有保存路径使用配置

### 7. 创建 Python 包结构
- ✅ 创建 `src/__init__.py`
  - 导出所有主要函数和类
  - 定义包版本和作者信息

### 8. 创建统一主程序
- ✅ 创建 `main.py`
  - 统一调度所有分析模块
  - 支持运行完整流程
  - 支持单独运行各个模块
  - 完善的错误处理
  - 清晰的进度提示

### 9. 创建测试脚本
- ✅ 创建 `test_config.py`
  - 验证配置文件加载
  - 显示所有配置项
  - 测试目录创建

### 10. 创建文档
- ✅ 创建 `README.md` - 完整的使用文档
- ✅ 创建 `CHANGES.md` - 本修改总结文档

## 主要改进

### 1. 配置集中管理
- **之前**: 路径、设备名、场景名等硬编码在各个脚本中
- **现在**: 所有配置集中在 `config/config.yaml`，易于修改和维护

### 2. 代码复用性
- **之前**: 每个脚本独立运行，难以组合
- **现在**: 所有模块可以作为函数/类导入，也可以独立运行

### 3. 统一调度
- **之前**: 需要手动运行多个脚本
- **现在**: 通过 `main.py` 统一调度，一键运行完整流程

### 4. 灵活性
- **之前**: 修改配置需要编辑多个文件
- **现在**: 只需修改 `config.yaml` 一个文件

### 5. 可维护性
- **之前**: 代码分散，难以维护
- **现在**: 模块化结构，职责清晰

## 使用方法

### 运行完整分析流程
```bash
python main.py
```

### 运行单个模块
```bash
python main.py data      # 数据加载
python main.py rssi      # RSSI 分析
python main.py battery   # 电池分析
python main.py mode      # 模式分析
```

### 测试配置
```bash
python test_config.py
```

### 单独运行模块
```bash
python -m src.data_loader
python -m src.battery_analyzer
python -m src.mode_analyzer
python -m src.visualization
```

## 配置文件位置
- 主配置文件: `config/config.yaml`
- 可以通过修改此文件来自定义所有行为

## 注意事项

1. **依赖包**: 确保安装了 `pyyaml`
   ```bash
   pip install pyyaml
   ```

2. **数据文件**: 确保原始数据在 `data/raw/` 目录

3. **编码问题**: 如果在 Windows 控制台遇到中文显示问题，可以：
   - 使用英文版本的输出
   - 或设置控制台编码: `chcp 65001`

4. **路径**: 所有路径都是相对于项目根目录的相对路径

## 兼容性

- ✅ Python 3.7+
- ✅ Windows / Linux / macOS
- ✅ 向后兼容（保留了所有原有功能）

## 未来改进建议

1. 添加命令行参数解析（argparse）
2. 添加日志系统（logging）
3. 添加单元测试
4. 添加配置验证
5. 支持多个配置文件（开发/生产环境）
