import os
import re
import time
import shutil  # 导入 shutil 用于删除非空文件夹


def delete_excess_files(directory):
    """检查目录，保留最新的两个 .tar.gz 文件和日期时间格式文件夹，其余删除"""
    # 获取所有 .tar.gz 文件
    tar_gz_files = [f for f in os.listdir(directory) if f.endswith('.tar.gz')]
    # 按文件名（时间戳）排序，假设文件名以时间戳开头
    tar_gz_files.sort(key=lambda x: x.split('.')[0], reverse=True)

    # 获取所有日期时间格式文件夹（格式如 20250301_194522）
    date_folders = [f for f in os.listdir(directory) if re.match(r'^\d{8}_\d{6}$', f)]
    # 按文件夹名（时间戳）排序
    date_folders.sort(reverse=True)

    # 保留最新的两个 .tar.gz 文件，其余删除
    if len(tar_gz_files) > 2:
        for file in tar_gz_files[2:]:
            file_path = os.path.join(directory, file)
            try:
                os.remove(file_path)
                print(f"Deleted excess .tar.gz file: {file}")
            except OSError as e:
                print(f"Error deleting {file}: {e}")

    # 保留最新的两个日期时间格式文件夹，其余删除（支持非空文件夹）
    if len(date_folders) > 2:
        for folder in date_folders[2:]:
            folder_path = os.path.join(directory, folder)
            try:
                shutil.rmtree(folder_path)  # 删除非空文件夹
                print(f"Deleted excess folder: {folder}")
            except OSError as e:
                print(f"Error deleting {folder}: {e}")


def main():
    """主函数，检查当前目录的文件和文件夹"""
    directory = os.getcwd()  # 获取当前工作目录
    while True:
        delete_excess_files(directory)
        time.sleep(60)  # 每分钟检查一次


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Stopped by user")
    print("Program terminated.")