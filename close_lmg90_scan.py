import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src", "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src", "..", "..")))

from src.Robotic_Arm.rm_robot_interface import *


ARM_IP = "192.168.1.18"
ARM_PORT = 8080
LEVEL = 3

BAUDRATE = 115200
TIMEOUT = 10

# port=0 控制器 RS485, port=1 末端接口板 RS485
PORTS = [1, 0]

# 常见 Modbus 地址，LMG-90 默认是 1，但可能被改过
DEVICE_IDS = list(range(1, 21))

# 乐白资料写 40000/0x9C40，但 SDK 可能用偏移地址 0
ADDRS = [0, 40000]

# 闭合值。如果你的夹爪方向相反，可以改成 1000 或实际标定的闭合值。
CLOSE_VALUE = 0


def main():
    print("[close] API version:", rm_api_version())

    robot = RoboticArm(rm_thread_mode_e(2))
    handle = robot.rm_create_robot_arm(ARM_IP, ARM_PORT, LEVEL)

    if handle.id == -1:
        print("[close] failed to connect right arm")
        return

    print("[close] connected right arm, id:", handle.id)

    try:
        for port in PORTS:
            print(f"\n[close] set modbus mode port={port}")
            ret = robot.rm_set_modbus_mode(port, BAUDRATE, TIMEOUT)
            print(f"[close] set_modbus_mode port={port} ret={ret}")

            if ret != 0:
                continue

            try:
                for device_id in DEVICE_IDS:
                    for addr in ADDRS:
                        print(
                            f"[close] try port={port} device={device_id} "
                            f"addr={addr} value={CLOSE_VALUE}"
                        )

                        params = rm_peripheral_read_write_params_t(
                            port,
                            addr,
                            device_id
                        )

                        ret = robot.rm_write_single_register(params, CLOSE_VALUE)
                        print(f"[close] ret={ret}")

                        if ret == 0:
                            print(f"[close] SUCCESS port={port} device={device_id} addr={addr}")
                            return

                        time.sleep(0.2)
            finally:
                ret = robot.rm_close_modbus_mode(port)
                print(f"[close] close_modbus_mode port={port} ret={ret}")

        print("[close] no success")
    finally:
        robot.rm_delete_robot_arm()
        print("[close] disconnected")


if __name__ == "__main__":
    main()
