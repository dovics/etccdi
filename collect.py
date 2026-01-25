import os
import re
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path

# 配置路径
RESULT_DATA_DIR = r"result_data"


def get_git_commit_hash():
    """获取当前 git commit hash"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def parse_date_from_filename(filename):
    """从文件名中解析日期时间
    格式: output_YYYYMMDD_HHMMSS_git_hash.zip
    """
    match = re.search(r'output_(\d{8})_(\d{6})', filename)
    if match:
        date_str = match.group(1)  # YYYYMMDD
        time_str = match.group(2)  # HHMMSS
        dt = datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")
        return dt
    return None


def get_latest_output_zip(folder_path):
    """获取文件夹中最新的 output_*.zip 文件"""
    pattern = re.compile(r'output_\d{8}_\d{6}_[a-f0-9]+\.zip')
    zip_files = []

    for file in os.listdir(folder_path):
        if pattern.match(file):
            dt = parse_date_from_filename(file)
            if dt:
                zip_files.append((dt, os.path.join(folder_path, file), file))

    if not zip_files:
        return None

    # 按日期排序，返回最新的
    zip_files.sort(key=lambda x: x[0], reverse=True)
    return zip_files[0]  # (datetime, full_path, filename)


def collect_latest_outputs():
    """收集所有文件夹中最新的 output_*.zip 文件"""
    result_data_path = Path(RESULT_DATA_DIR)

    # 获取当前时间和 commit hash
    now = datetime.now()
    commit_hash = get_git_commit_hash()
    timestamp = now.strftime("%Y%m%d_%H%M%S")

    # 生成输出文件名
    output_zip = Path(RESULT_DATA_DIR) / f"collected_outputs_{timestamp}_{commit_hash}.zip"

    # 存储所有找到的最新文件
    latest_files = []

    # 遍历所有子文件夹
    for folder in sorted(result_data_path.iterdir()):
        if folder.is_dir() and folder.name not in ['all', '__pycache__']:
            print(f"检查文件夹: {folder.name}")

            latest = get_latest_output_zip(folder)
            if latest:
                dt, full_path, filename = latest
                print(f"  找到最新文件: {filename} ({dt.strftime('%Y-%m-%d %H:%M:%S')})")
                latest_files.append((folder.name, full_path, filename, dt))
            else:
                print(f"  未找到 output_*.zip 文件")

    if not latest_files:
        print("未找到任何 output_*.zip 文件")
        return

    print(f"\n共找到 {len(latest_files)} 个最新文件")

    # 创建新的 zip 文件
    print(f"\n正在创建 {output_zip} ...")
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for folder_name, full_path, filename, dt in latest_files:
            # 在 zip 中以文件夹名命名，如 ACCESS-CM2.zip
            arcname = f"{folder_name}.zip"
            print(f"  添加: {arcname} (原文件: {filename})")
            zipf.write(full_path, arcname)

    print(f"\n完成! 已创建 {output_zip}")
    print(f"包含 {len(latest_files)} 个文件")


if __name__ == "__main__":
    collect_latest_outputs()
