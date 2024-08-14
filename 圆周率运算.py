import multiprocessing
import time
import signal
import sys
import os
from mpmath import mp

stop_event = multiprocessing.Event()
processes = []


def compute_pi_chudnovsky(digit_precision, start_index, queue):
    mp.dps = digit_precision
    while not stop_event.is_set():
        try:
            pi_value = str(mp.pi)[2:]  # 获取π的小数部分（去掉 "3."）
            queue.put((start_index, pi_value))
        except KeyboardInterrupt:
            break


def collect_digits(queue):
    pi_digits = "3."
    file_path = "pi_digits.txt"
    try:
        while not stop_event.is_set() or not queue.empty():
            try:
                index, digits = queue.get(timeout=1)
                pi_digits += digits
                print(f"当前计算π的总位数: {len(pi_digits) - 2}")
                # 实时写入文件以防数据丢失
                with open("pi_digits.txt", "w") as file:
                    file.write(pi_digits)
            except multiprocessing.queues.Empty:
                continue
    except PermissionError as e:
        print(f"写入文件失败: {e}")
        print(f"请检查文件权限和路径: {os.path.abspath(file_path)}")
    finally:
        # 最后一次确保数据完整性
        try:
            with open(file_path, "w") as file:
                file.write(pi_digits)
            print(f"当前π的值已保存到文件 '{file_path}' 中。")
        except PermissionError:
            print(f"无法写入文件 {file_path}。请检查文件是否被其他程序占用。")


def signal_handler(sig, frame):
    print('收到中断信号，正在清理...')
    stop_event.set()
    for p in processes:
        p.terminate()
    sys.exit(0)


def run_test(duration,process_count=1):
    digit_precision = multiprocessing.cpu_count() * 1000 * 2
    print(f"精细度: {digit_precision}")
    queue = multiprocessing.Queue()

    for i in range(process_count):
        p = multiprocessing.Process(
            target=compute_pi_chudnovsky, args=(digit_precision, i, queue))
        p.start()
        processes.append(p)

    collector = multiprocessing.Process(target=collect_digits, args=(queue,))
    collector.start()

    if duration:
        time.sleep(duration)
    else:
        input("按任意键停止测试...\n")

    stop_event.set()
    collector.terminate()
    collector.join()
    for p in processes:
        p.terminate()
        p.join()


def main_menu():
    signal.signal(signal.SIGINT, signal_handler)
    while True:
        print("\n圆周率运算，请选择操作：")
        print("1 - 设置计算的时间")
        print("2 - 无限的运行计算")
        print("3 - 更多线程运算规则")
        print("0 - 退出计算")
        choice = input("请输入选项（回车键,10秒运算）：")
        if choice == '1':
            run_time = float(input("请输入运行时间（秒）："))
            run_test(run_time)
        elif choice == '2':
            run_test(None)
        elif choice == '3':
            print("\n更多线程运算规则，请选择操作：")
            print("1 - 单进程计算")
            print("2 - 多进程计算")
            print("3 - 自定义进程计算")
            print("0 - 返回上级")
            choice3 = input("请输入选项（回车键,单线程计算）：")
            if choice3 == '1':
                break
            elif choice3 == '2':
                break
            elif choice3 == '3':
                break
            elif choice == '0':
                main_menu()

        elif choice == '0':
            print("退出程序。")
            break
        else:
            run_test(10)


if __name__ == "__main__":
    main_menu()
