# @Version :1.0
# @Author  : Mingyue
# @File    : data_loader.py.py
# @Time    : 01/03/2026 19:27
import pandas as pd
from utils import load_config


def process_rssi_data(config=None):
    """
    处理 RSSI 数据对齐
    
    Args:
        config (dict): 配置字典，如果为 None 则自动加载
        
    Returns:
        pd.DataFrame: 处理后的结果数据框
    """
    if config is None:
        config = load_config()
    
    print("=== 开始数据对齐处理 ===")
    
    # 读取数据（不自动解析日期，保持原始字符串格式）
    raw_data_dir = config['paths']['raw_data_dir']
    logs = pd.read_csv(f"{raw_data_dir}/rssi_history.csv")
    gt = pd.read_csv(f"{raw_data_dir}/ground_truth.csv")
    
    # 使用 pd.to_datetime() 统一转换为 datetime64[ns] 格式
    logs["Timestamp"] = pd.to_datetime(logs["Timestamp"])
    gt["gt_start"] = pd.to_datetime(gt["gt_start"])
    gt["gt_end"] = pd.to_datetime(gt["gt_end"])
    
    # 验证时间格式转换
    print("\n=== 时间格式转换验证 ===")
    print(f"RSSI Timestamp 数据类型: {logs['Timestamp'].dtype}")
    print(f"Ground Truth gt_start 数据类型: {gt['gt_start'].dtype}")
    print(f"Ground Truth gt_end 数据类型: {gt['gt_end'].dtype}")
    
    print("\n=== 时间格式示例 ===")
    print("RSSI 时间示例:")
    print(logs["Timestamp"].head(3))
    print("\nGround Truth 时间示例:")
    print(gt[["gt_start", "gt_end"]].head(3))
    
    # 获取时间容差配置
    time_tolerance = config['analysis']['time_tolerance_seconds']
    print(f"\n使用时间容差: ±{time_tolerance}s")
    
    results = []
    for _, row in gt.iterrows():
        uuid = row["uuid"]
        start = row["gt_start"]
        end = row["gt_end"]
    
        # 提取该 trial 的日志 (使用配置的时间容差)
        mask = (
            (logs["UUID"] == uuid) &
            (logs["Timestamp"] >= start - pd.Timedelta(seconds=time_tolerance)) &
            (logs["Timestamp"] <= end + pd.Timedelta(seconds=time_tolerance))
        )
        subset = logs[mask]
    
        if len(subset) == 0:
            results.append({
                "trial_id": row["trial_id"],
                "uuid": uuid,
                "detected": False,
                "detected_start": None,
                "detected_end": None,
                "detected_duration_s": 0,
                "median_RSSI": None,
                "max_RSSI": None
            })
        else:
            results.append({
                "trial_id": row["trial_id"],
                "uuid": uuid,
                "detected": True,
                "detected_start": subset["Timestamp"].min(),
                "detected_end": subset["Timestamp"].max(),
                "detected_duration_s": (subset["Timestamp"].max() - subset["Timestamp"].min()).total_seconds(),
                "median_RSSI": subset["RSSI"].median(),
                "max_RSSI": subset["RSSI"].max()
            })
    
    results_df = pd.DataFrame(results)
    
    # 确保日期时间列保持完整格式
    if not results_df.empty:
        # 将datetime列格式化为完整的ISO格式字符串
        datetime_columns = ['detected_start', 'detected_end']
        for col in datetime_columns:
            if col in results_df.columns:
                # 将datetime对象转换为完整的ISO格式字符串
                results_df[col] = results_df[col].dt.strftime('%Y-%m-%dT%H:%M:%S.%f').str.replace('000000', '000000')
    
    # 保存结果到配置指定的目录
    processed_data_dir = config['paths']['processed_data_dir']
    output_path = f"{processed_data_dir}/evaluation_results.csv"
    results_df.to_csv(output_path, index=False)
    
    print(f"\n=== 处理完成 ===")
    print(f"处理了 {len(gt)} 个试验")
    print(f"结果已保存到 {output_path}")
    
    return results_df


if __name__ == "__main__":
    # 如果直接运行此脚本
    process_rssi_data()
