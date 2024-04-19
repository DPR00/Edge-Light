import os
import serial
import csv
import time
from path import Path
import constants_red as const
import matplotlib.pyplot as plt
import numpy as np


def get_accuracy(path=const.PATH_FILE_BITS):
    total = 0

    with open(path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        const.TOTAL_READINGS = len(list(reader))

    with open(path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if const.REAL_BIT == int(row[0]):
                total += 1
    # print(100 * total / const.TOTAL_READINGS)
    return 100 * total / const.TOTAL_READINGS


def get_bits(port, baudrate, timeout, path, total_readings):
    counter = 0
    ser_rx = serial.Serial(port, baudrate, timeout=timeout)
    ser_rx.reset_input_buffer()

    with open(path, "w", newline="") as csvfile:
        fieldnames = ["bit"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        print("Receiving and saving RED...")
        start_time = time.time()
        while total_readings > counter:
            rx_raw = ser_rx.readline()
            if len(rx_raw.decode().strip()) > 0:
                rx_data = [
                    int(i) if len(i) > 0 else None
                    for i in rx_raw.decode().strip().split(",")
                ]
                writer.writerow({"bit": rx_data[0]})
            counter += 1
        elpased_time = time.time() - start_time
        print(elpased_time)


def get_dynamic_data(port, baudrate, timeout, path_bits, path_cs, total_readings):
    counter = 0
    go_cs, go_bit = 0, 0
    ser_rx = serial.Serial(port, baudrate, timeout=timeout)
    ser_rx.reset_input_buffer()
    with open(path_bits, "w", newline="") as bit_csvfile:
        fieldnames = ["bit"]
        bit_writer = csv.DictWriter(bit_csvfile, fieldnames=fieldnames)
        with open(path_cs, "w", newline="") as cs_csvfile:
            fieldnames = ["color"]
            cs_writer = csv.DictWriter(cs_csvfile, fieldnames=fieldnames)
            print("Receiving and saving RED...")
            start_time = time.time()
            while total_readings > counter:
                rx_raw = ser_rx.readline()
                rx_data = rx_raw.decode().strip()
                # print(rx_data)
                if len(rx_data) > 0 and len(rx_data) < 4 and go_cs:
                    cs_writer.writerow({"color": rx_data})
                    counter += 1
                if len(rx_data) > 0 and len(rx_data) < 4 and go_bit:
                    bit_writer.writerow({"bit": rx_data})
                    counter += 1
                if rx_data == "color":
                    go_cs = 1
                    go_bit = 0
                if rx_data == "bits":
                    go_bit = 1
                    go_cs = 0
            elpased_time = time.time() - start_time
            print(elpased_time)


def get_color_data(port_usb, baudrate, timeout, path_usb, total_readings_usb):
    counter = 0
    ser_rx_usb = serial.Serial(port_usb, baudrate, timeout=timeout)
    ser_rx_usb.reset_input_buffer()
    start_time = time.time()

    with open(path_usb, "w", newline="") as csvfile:
        fieldnames = ["color_sensor"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        print("Saving color data RED...")
        while const.TOTAL_READINGS_USB > counter:
            # print(counter)
            rx_raw_usb = ser_rx_usb.readline()
            if len(rx_raw_usb.decode().strip()) > 0:
                rx_data = [
                    int(i) if len(i) > 0 else None
                    for i in rx_raw_usb.decode().strip().split(",")
                ]
                writer.writerow({"color_sensor": rx_data[0]})

            counter += 1

    elpased_time = time.time() - start_time
    print(elpased_time)


def get_stats(path):

    path_PH = Path(path)
    files = [dir for dir in sorted(os.listdir(path_PH)) if os.path.isdir(path_PH)]

    robots = ["RED", "GREEN"]
    configs = ["aligned", "unaligned"]
    light_conds = ["417LX", "500LX", "700LX"]
    bits = ["2", "4", "5", "8"]
    distances = ["10", "20", "30", "40", "50"]
    data = {}

    # Initialize dict
    for robot in robots:
        data[robot] = {}
        for config in configs:
            data[robot][config] = {}
            for bit in bits:
                data[robot][config][bit] = {}
                for light_cond in light_conds:
                    data[robot][config][bit][light_cond] = {}
                    for distance in distances:
                        data[robot][config][bit][light_cond][distance] = []

    for file in files:
        list_file = file.strip().split("_")

        bit = list_file[0][-1]
        n_test = int(list_file[1][-1])
        light_cond = list_file[3]
        distance = list_file[4][-2:]
        robot = list_file[5][5:]
        config = list_file[6][6:-4]
        acc = get_accuracy(path + "/" + file)

        data[robot][config][bit][light_cond][distance].append(acc)

    print(data)
    for robot in robots:
        for config in configs:
            i = 0
            fig, axs = plt.subplots(2, 2, layout="constrained")
            x = np.arange(1, 1 + len(distances))  # the label locations
            pos0 = 10
            width = 2  # the width of the bars
            multiplier = -1
            for bit in bits:
                idx = bits.index(bit)
                for light_cond in light_conds:
                    arr_mean_lc = []
                    arr_std_lc = []
                    for distance in distances:
                        list_acc = data[robot][config][bit][light_cond][distance]
                        if len(list_acc) > 0:
                            arr_acc = np.array(list_acc)
                            acc_mean = np.round(np.mean(arr_acc), 1)
                            acc_std = np.round(np.std(arr_acc), 1)
                            arr_mean_lc.append(acc_mean)
                            arr_std_lc.append(acc_std)
                    if len(arr_mean_lc) > 0:

                        offset = width * multiplier
                        rects = axs[idx // 2, idx % 2].bar(
                            pos0 * x + offset,
                            arr_mean_lc,
                            width,
                            yerr=arr_std_lc,
                            label=light_cond,
                        )
                        axs[idx // 2, idx % 2].bar_label(rects, padding=3)
                        multiplier += 1

                axs[idx // 2, idx % 2].set_xlabel("Distance (cm)")
                axs[idx // 2, idx % 2].set_ylabel("Accuracy (%)")
                axs[idx // 2, idx % 2].set_title(f"Robot {robot} {config}: BIT {bit}")
                axs[idx // 2, idx % 2].set_xticks(
                    [int(dist) for dist in distances], distances
                )
                axs[idx // 2, idx % 2].legend(loc="upper right", ncols=1)
                axs[idx // 2, idx % 2].set_xlim(0, 1.2 * int(distances[-1]))
                axs[idx // 2, idx % 2].set_ylim(0, 120)
            plt.show()
    plt.close()
