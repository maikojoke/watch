import subprocess
import time
import warnings

# 忽略特定警告 (DeprecationWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)


def run_program(script, max_retries=3):
    """运行脚本并处理错误，最大重试次数"""
    attempt = 0
    while attempt < max_retries:
        try:
            subprocess.check_call(['python', script])
            print(f"'{script}' executed successfully at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            return
        except subprocess.CalledProcessError as e:
            attempt += 1
            print(f"Error executing '{script}': {e}. Retrying {attempt}/{max_retries}...")
            time.sleep(2)
    print(f"'{script}' failed after {max_retries} attempts.")
    raise RuntimeError(f"Failed to execute '{script}' after {max_retries} retries.")


def main():
    """主调度函数，运行一次脚本序列"""
    scripts = [
        '1Xshell_Xftp_get_bak.py',
        '2extract_targz.py',
        '3Re_modify_bak.py',
        '4Unpacking_bak.py',
        '5targz_to_file.py',
        '6BloodSugar.device.py',
        '7XiaomiFit.device.py',
        '8XiaomiFit.main.py',
        '10Delete_file.py'
    ]

    print("0RunCode started, running scripts once...")
    print(f"\nStarting script sequence at {time.strftime('%Y-%m-%d %H:%M:%S')}")

    for script in scripts:
        try:
            run_program(script)
        except RuntimeError as e:
            print(f"Skipping '{script}' due to repeated failures.")
            continue

    print("Script sequence completed.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user")
    print("Program terminated.")