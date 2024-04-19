import os
import serial
import csv
import time
from path import Path
import constants_green as const
import matplotlib.pyplot as plt
import numpy as np
import random
import pandas as pd
from scipy.io import loadmat
from scipy.fft import fft, fftfreq
from math import log10

# plt.style.use("paperacm.mplstyle")

robots = const.LIST_ROBOTS
configs = const.LIST_CONFIG  # ["aligned", "unaligned"]
light_conds = (
    const.LIST_LIGHT_CONDS
)  # ["417LX", "500LX"]  # ["417LX", "500LX", "700LX"]
bits = const.LIST_BITS
distances = const.LIST_DISTANCES
bit_to_freq = {"2": "2.5 Hz", "4": "5 Hz", "5": "6.7 Hz", "8": "10 Hz"}
bit_to_freq_int = {"2": 2.5, "4": 5, "5": 6.67, "8": 10}


def get_accuracy(path, bit):
    total = 0

    with open(path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if bit == int(row[0]):
                total += 1
    # print(100 * total / const.TOTAL_READINGS)
    return 100 * total / const.TOTAL_READINGS


def get_accuracy_dynamic(path, bit):
    total = 0

    with open(path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if bit == int(row[0]):
                total += 1
    # print(100 * total / const.TOTAL_READINGS)
    return 100 * total / const.TOTAL_READINGS_MOTION


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
            print("Receiving and saving GREEN...")
            start_time = time.time()
            while total_readings > counter:
                rx_raw = ser_rx.readline()
                rx_data = rx_raw.decode().strip()
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


def get_bits(port, baudrate, timeout, path, total_readings):
    counter = 0
    ser_rx = serial.Serial(port, baudrate, timeout=timeout)
    ser_rx.reset_input_buffer()
    with open(path, "w", newline="") as csvfile:
        fieldnames = ["bit"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        print("Receiving and saving GREEN...")
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
        done = 1


def get_color_data(port_usb, baudrate, timeout, path_usb, total_readings_usb):
    counter = 0
    ser_rx_usb = serial.Serial(port_usb, baudrate, timeout=timeout)
    ser_rx_usb.reset_input_buffer()
    start_time = time.time()

    with open(path_usb, "w", newline="") as csvfile:
        fieldnames = ["color_sensor"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        print("Saving color data GREEN...")
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


def get_bits_color(port, port_usb, baudrate, timeout, path, path_usb, total_readings):
    counter = 0
    ser_rx = serial.Serial(port, baudrate, timeout=timeout)
    ser_rx.reset_input_buffer()

    ser_rx_usb = serial.Serial(port_usb, baudrate, timeout=timeout)
    ser_rx_usb.reset_input_buffer()
    color_sensor_data = []
    start_time = time.time()

    with open(path, "w", newline="") as csvfile:
        fieldnames = ["bit"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        print("Receiving and saving GREEN...")
        while total_readings > counter:
            rx_raw = ser_rx.readline()
            if len(rx_raw.decode().strip()) > 0:
                rx_data = [
                    int(i) if len(i) > 0 else None
                    for i in rx_raw.decode().strip().split(",")
                ]
                writer.writerow({"bit": rx_data[0]})

            rx_raw_usb = ser_rx_usb.readline()
            if len(rx_raw_usb.decode().strip()) > 0:
                color_sensor_data.append(rx_raw_usb.decode().strip().split(","))
            counter += 1

    with open(path_usb, "w", newline="") as csvfile:
        fieldnames = ["color_sensoe"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        print("Saving color sensor data...")
        writer.writerow({"bit": color_sensor_data})

    elpased_time = time.time() - start_time
    print(elpased_time)


def get_data_from_files_dynamic(path):
    data_bits = {}
    data_cs = {}
    path_PH = Path(path)
    files = [dir for dir in sorted(os.listdir(path_PH)) if os.path.isdir(path_PH)]

    # Initialize dict
    for robot in robots:
        data_bits[robot] = {}
        data_cs[robot] = {}
        for config in configs:
            data_bits[robot][config] = {}
            data_cs[robot][config] = {}
            for bit in bits:
                data_bits[robot][config][bit] = {}
                data_cs[robot][config][bit] = {}
                for light_cond in light_conds:
                    data_bits[robot][config][bit][light_cond] = {}
                    data_cs[robot][config][bit][light_cond] = {}
                    for distance in distances:
                        data_bits[robot][config][bit][light_cond][distance] = []
                        data_cs[robot][config][bit][light_cond][distance] = []

    for file in files:
        list_file = file.strip().split("_")
        # print(list_file)
        if list_file[0] != "CS":
            bit = list_file[0][-1]
            n_test = int(list_file[1][-1])
            light_cond = list_file[3]
            distance = list_file[4][-2:]
            robot = list_file[5][5:]
            config = list_file[6][6:-4]
            acc = get_accuracy_dynamic(path + "/" + file, int(bit))
            # print(n_test, bit, light_cond, distance, robot, config, acc)

            data_bits[robot][config][bit][light_cond][distance].append(acc)

        if list_file[0] == "CS":
            temp_data_cs = []
            with open(path_PH + "/" + file, newline="") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    temp_data_cs.append(int(row[0]))
            list_file = list_file[1:]
            bit = list_file[0][-1]
            n_test = int(list_file[1][-1])
            light_cond = list_file[3]
            distance = list_file[4][-2:]
            robot = list_file[5][5:]
            config = list_file[6][6:]
            print(config)
            data_cs[robot][config][bit][light_cond][distance].append(temp_data_cs)

    return data_bits, data_cs


def get_data_from_files(path):
    data_bits = {}
    data_cs = {}
    path_PH = Path(path)
    files = [dir for dir in sorted(os.listdir(path_PH)) if os.path.isdir(path_PH)]

    # Initialize dict
    for robot in robots:
        data_bits[robot] = {}
        data_cs[robot] = {}
        for config in configs:
            data_bits[robot][config] = {}
            data_cs[robot][config] = {}
            for bit in bits:
                data_bits[robot][config][bit] = {}
                data_cs[robot][config][bit] = {}
                for light_cond in light_conds:
                    data_bits[robot][config][bit][light_cond] = {}
                    data_cs[robot][config][bit][light_cond] = {}
                    for distance in distances:
                        data_bits[robot][config][bit][light_cond][distance] = []
                        data_cs[robot][config][bit][light_cond][distance] = []

    for file in files:
        list_file = file.strip().split("_")
        # print(list_file)
        if list_file[0] != "CS":
            bit = list_file[0][-1]
            n_test = int(list_file[1][-1])
            light_cond = list_file[3]
            distance = list_file[4][-2:]
            robot = list_file[5][5:]
            config = list_file[6][6:].split(".")
            config = config[0]
            acc = get_accuracy(path + "/" + file, int(bit))
            # print(bit, light_cond, distance, robot, config, acc)

            data_bits[robot][config][bit][light_cond][distance].append(acc)

        if list_file[0] == "CS":
            temp_data_cs = []
            with open(path_PH + "/" + file, newline="") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    temp_data_cs.append(int(row[0]))
            list_file = list_file[1:]
            bit = list_file[0][-1]
            n_test = int(list_file[1][-1])
            light_cond = list_file[3]
            distance = list_file[4][-2:]
            robot = list_file[5][5:]
            config = list_file[6][6:].split(".")
            config = config[0]

            data_cs[robot][config][bit][light_cond][distance].append(temp_data_cs)

    return data_bits, data_cs


def get_bin_stats(data):

    for robot in robots:
        for config in configs:
            fig, axs = plt.subplots(2, 2, layout="constrained")
            fig.suptitle(f"Robot {robot} {config}", fontsize=16)
            x = np.arange(1, 1 + len(distances))  # the label locations
            for bit in bits:
                pos0 = 10
                width = 2  # the width of the bars
                multiplier = -(len(light_conds) - 1) / 2
                idx = bits.index(bit)
                axx, axy = idx // 2, idx % 2
                for light_cond in light_conds:
                    arr_mean_lc = []
                    arr_std_lc = []
                    for distance in distances:
                        list_acc = data[robot][config][bit][light_cond][distance]
                        if len(list_acc) > 0:
                            # print(list_acc)
                            arr_acc = np.array(list_acc)
                            acc_mean = np.round(np.mean(arr_acc), 1)
                            acc_std = np.round(np.std(arr_acc), 1)
                            arr_mean_lc.append(acc_mean)
                            arr_std_lc.append(acc_std)
                    if len(arr_mean_lc) > 0:
                        while len(arr_mean_lc) != len(distances):
                            arr_mean_lc.append(0)
                        offset = width * multiplier
                        rects = axs[axx, axy].bar(
                            pos0 * x + offset,
                            arr_mean_lc,
                            width,
                            yerr=arr_std_lc,
                            label=light_cond,
                        )
                        axs[axx, axy].bar_label(rects, padding=3)
                        multiplier += 1

                axs[axx, axy].set_xlabel(
                    "Distance (cm)", fontdict={"fontsize": 12, "fontweight": "medium"}
                )
                axs[axx, axy].set_ylabel(
                    "Accuracy (%)", fontdict={"fontsize": 12, "fontweight": "medium"}
                )
                axs[axx, axy].set_title(
                    f"Frequency: {bit}",
                    fontdict={"fontsize": 14, "fontweight": "medium"},
                )
                axs[axx, axy].set_xticks([int(dist) for dist in distances], distances)
                if robot == "RED":
                    axs[axx, axy].legend(loc="upper right", ncols=1)
                else:
                    axs[axx, axy].legend(loc="lower right", ncols=1)
                axs[axx, axy].set_xlim(0, 1.2 * int(distances[-1]))
                axs[axx, axy].set_ylim(0, 120)
    plt.show()
    plt.close()


def get_general_stats(path):

    path_PH = Path(path)
    files = [dir for dir in sorted(os.listdir(path_PH)) if os.path.isdir(path_PH)]

    robots = const.LIST_ROBOTS
    configs = const.LIST_CONFIG  # ["aligned", "unaligned"]
    light_conds = (
        const.LIST_LIGHT_CONDS
    )  # ["417LX", "500LX"]  # ["417LX", "500LX", "700LX"]
    bits = const.LIST_BITS
    distances = const.LIST_DISTANCES
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
        # print(list_file)
        if list_file[0] != "CS":
            bit = list_file[0][-1]
            n_test = int(list_file[1][-1])
            light_cond = list_file[3]
            distance = list_file[4][-2:]
            robot = list_file[5][5:]
            config = list_file[6][6:-4]
            acc = get_accuracy(path + "/" + file, int(bit))
            # print(bit, light_cond, distance, robot, config, acc)

            data[robot][config][bit][light_cond][distance].append(acc)

    for robot in robots:
        for config in configs:
            fig, axs = plt.subplots(2, 2, layout="constrained")
            fig.suptitle(f"Robot {robot} {config}", fontsize=16)
            x = np.arange(1, 1 + len(distances))  # the label locations
            for bit in bits:
                pos0 = 10
                width = 2  # the width of the bars
                multiplier = -(len(light_conds) - 1) / 2
                idx = bits.index(bit)
                axx, axy = idx // 2, idx % 2
                for light_cond in light_conds:
                    arr_mean_lc = []
                    arr_std_lc = []
                    for distance in distances:
                        list_acc = data[robot][config][bit][light_cond][distance]
                        if len(list_acc) > 0:
                            # print(list_acc)
                            arr_acc = np.array(list_acc)
                            acc_mean = np.round(np.mean(arr_acc), 1)
                            acc_std = np.round(np.std(arr_acc), 1)
                            arr_mean_lc.append(acc_mean)
                            arr_std_lc.append(acc_std)
                    if len(arr_mean_lc) > 0:
                        while len(arr_mean_lc) != len(distances):
                            arr_mean_lc.append(0)
                        offset = width * multiplier
                        rects = axs[axx, axy].bar(
                            pos0 * x + offset,
                            arr_mean_lc,
                            width,
                            yerr=arr_std_lc,
                            label=light_cond,
                        )
                        axs[axx, axy].bar_label(rects, padding=3)
                        multiplier += 1

                axs[axx, axy].set_xlabel(
                    "Distance (cm)", fontdict={"fontsize": 12, "fontweight": "medium"}
                )
                axs[axx, axy].set_ylabel(
                    "Accuracy (%)", fontdict={"fontsize": 12, "fontweight": "medium"}
                )
                axs[axx, axy].set_title(
                    f"Frequency: {bit}",
                    fontdict={"fontsize": 14, "fontweight": "medium"},
                )
                axs[axx, axy].set_xticks([int(dist) for dist in distances], distances)
                if robot == "RED":
                    axs[axx, axy].legend(loc="upper right", ncols=1)
                else:
                    axs[axx, axy].legend(loc="lower right", ncols=1)
                axs[axx, axy].set_xlim(0, 1.2 * int(distances[-1]))
                axs[axx, axy].set_ylim(0, 120)
    plt.show()
    plt.close()


def plot_color_data(data_cs, robot, config, bit, light_cond, distance, n_test):

    color_data = data_cs[robot][config][str(bit)][light_cond][str(distance)][n_test - 1]

    plt.plot(color_data, color="b")
    plt.title(f"Color sensor data for Robot {robot}, bit: {bit}, distance: {distance}")
    plt.xlabel("Time ")
    plt.ylabel("Color value")
    plt.show()


def calculate_snr(signal, bit):
    signal = np.array(signal)
    list_widths = [64]  # [64, 128]
    sfreq = 1 / 0.025
    if bit == "5":
        f_fund = 1000 / (25 * 30)
        list_widths = [60]
    else:
        f_fund = 1.25  # 1/(25ms*32)
    # number of signals
    n_signals = [8]  # [8, 16]
    list_snr = []

    max_snr, max_init, max_width, max_n_signal = 0, 0, 0, 0
    for width in list_widths:
        df_fft = pd.DataFrame(
            [], index=np.round(fftfreq(width, 1 / sfreq)[0 : width // 2], 2)
        )
        # print(df_fft)
        for n_s in n_signals:
            max_init_point = len(signal) - n_s * width + width // 2
            for init in range(100, max_init_point - width, 200):
                for i in range(n_s):
                    data = signal[init + i * width : init + width + i * width]
                    data = data - data.mean()
                    df_fft[i] = abs(fft(data, norm="forward")[0 : width // 2])
                    # print(df_fft[i])

                ## To visualize harmonics
                # df_fft.plot()
                # plt.show()

                # Harmonics are signal, other are noise
                # harms = [
                #     i / 100
                #     for i in range(
                #         int(f_fund * 100), int(sfreq / 2) * 100, int(f_fund * 100)
                #     )
                # ]
                # harms = [bit_to_freq_int[bit]]
                harms = np.round(
                    np.arange(f_fund, sfreq / 2 - 0.00001, f_fund), 2
                ).tolist()
                # harms = [1.25, 1.25 * 3, 1.25 * 5, 1.25 * 7, 1.25 * 9]
                noise = ~df_fft.index.isin(harms)

                # print("Fundamental: ", end="")
                # print(df_fft.loc[1.25])
                # print("Noise: ", end="")
                # print(df_fft.loc[noise].sum())
                tmp_snr = 10 * log10(
                    (df_fft.loc[harms].sum() / df_fft.loc[noise].sum()).mean()
                )
                if max_snr < tmp_snr and str(tmp_snr) != "inf":
                    list_snr.append(tmp_snr)
                    max_snr = tmp_snr
                    max_init = init
                    max_width = width
                    max_n_signal = n_s
                # SNR in dB
                # print("SNR (dB)=", end="")
                # print(10*log10((df_fft.loc[1.25]/df_fft.loc[noise].sum()).mean()))
                # print(10 * log10((df_fft.loc[harms].sum() / df_fft.loc[noise].sum()).mean()))
    return max_snr


def calculate_ptp(signal):

    return 1


def random_snr_data(bit, distance):

    rnd = {
        "2": {"10": 60, "20": 35, "30": 10, "40": 2, "50": 0.1},
        "4": {"10": 62, "20": 37, "30": 12, "40": 4, "50": 0.3},
        "5": {"10": 64, "20": 39, "30": 14, "40": 6, "50": 0.5},
        "8": {"10": 66, "20": 41, "30": 16, "40": 8, "50": 0.7},
    }
    return rnd[bit][distance]


def calculate_snr_dynamic(signal, bit):
    signal = np.array(signal)
    list_widths = [64]  # [64, 128]
    sfreq = 1 / 0.025
    if bit == "5":
        f_fund = 1000 / (25 * 30)
        list_widths = [60]
    else:
        f_fund = 1.25  # 1/(25ms*32)
    # number of signals
    n_signals = [8]  # [8, 16]
    list_snr = []

    max_snr, max_init, max_width, max_n_signal = 0, 0, 0, 0
    for width in list_widths:
        df_fft = pd.DataFrame(
            [], index=np.round(fftfreq(width, 1 / sfreq)[0 : width // 2], 2)
        )
        # print(df_fft)
        for n_s in n_signals:
            max_init_point = len(signal) - n_s * width + width // 2
            for init in range(0, max_init_point, 1):
                for i in range(n_s):
                    data = signal[init + i * width : init + width + i * width]
                    data = data - data.mean()
                    df_fft[i] = abs(fft(data, norm="forward")[0 : width // 2])
                    # print(df_fft[i])

                ## To visualize harmonics
                # df_fft.plot()
                # plt.show()

                # Harmonics are signal, other are noise
                # harms = [
                #     i / 100
                #     for i in range(
                #         int(f_fund * 100), int(sfreq / 2) * 100, int(f_fund * 100)
                #     )
                # ]
                # harms = [bit_to_freq_int[bit]]
                harms = np.round(
                    np.arange(f_fund, sfreq / 2 - 0.01, f_fund), 2
                ).tolist()
                # harms = [1.25, 1.25 * 3, 1.25 * 5, 1.25 * 7, 1.25 * 9]
                noise = ~df_fft.index.isin(harms)

                # print("Fundamental: ", end="")
                # print(df_fft.loc[1.25])
                # print("Noise: ", end="")
                # print(df_fft.loc[noise].sum())
                tmp_snr = 10 * log10(
                    (df_fft.loc[harms].sum() / df_fft.loc[noise].sum()).mean()
                )
                if max_snr < tmp_snr and str(tmp_snr) != "inf":
                    list_snr.append(tmp_snr)
                    max_snr = tmp_snr
                    max_init = init
                    max_width = width
                    max_n_signal = n_s
                # SNR in dB
                # print("SNR (dB)=", end="")
                # print(10*log10((df_fft.loc[1.25]/df_fft.loc[noise].sum()).mean()))
                # print(10 * log10((df_fft.loc[harms].sum() / df_fft.loc[noise].sum()).mean()))

    return max_snr


def get_snr_stats(data_bits, data_cs):
    markers = ["o", "*", "^", "x"]

    fig, axs = plt.subplots(1, len(const.LIST_ROBOTS))
    fig.suptitle(f"SNR vs distance", fontsize=16)
    i = 0
    for robot in robots:
        axs[i].set_title("Robot " + robot)
        for config in configs:
            for bit in bits:
                snr_bits_red, int_dist_red = [], []
                snr_bits_green, int_dist_green = [], []
                int_dist = [int(i) for i in const.LIST_DISTANCES]
                snr_bits = []
                for light_cond in light_conds:
                    for distance in distances:
                        color_data = data_cs[robot][config][bit][light_cond][distance]
                        bit_data = data_bits[robot][config][bit][light_cond][distance]
                        # print(bit_data)
                        # print(len(color_data))
                        if len(color_data) > 0:
                            # print(len(color_data))
                            # snr_mean = 0
                            # for j in range(len(color_data)):
                            snr = calculate_snr(color_data[0], bit)
                            # print(snr)
                            # random_snr_data( bit, distance)
                            #    snr_mean += snr
                            # snr_mean = snr_mean / len(color_data)
                            # print(snr_mean)
                            if len(bit_data) > 0:
                                if np.mean(np.array(bit_data)) > const.ACC_THRESHOLD:
                                    int_dist_green.append(int(distance))
                                    snr_bits_green.append(snr)
                                    int_dist_red.append(int(distance))
                                    snr_bits_red.append(snr)
                                else:
                                    int_dist_red.append(int(distance))
                                    snr_bits_red.append(snr)
                            else:
                                snr_bits.append(snr)
                if len(snr_bits_green) > 0 or len(snr_bits_red) > 0:
                    axs[i].plot(
                        int_dist_red,
                        snr_bits_red,
                        marker=markers[bits.index(bit)],
                        color="r",
                        label="Freq:" + str(bit_to_freq[bit]) + ". Disconnected",
                    )
                    axs[i].plot(
                        int_dist_green,
                        snr_bits_green,
                        marker=markers[bits.index(bit)],
                        color="g",
                        label="Freq:" + str(bit_to_freq[bit]) + ". Connected",
                    )

                    axs[i].set_ylim([-3, 13])
                else:
                    while len(snr_bits) != len(int_dist):
                        snr_bits.append(0)
                    axs[i].plot(
                        int_dist,
                        snr_bits,
                        marker=markers[bits.index(bit)],
                        color="b",
                        label="Freq:" + str(bit_to_freq[bit]),
                    )
        axs[i].legend(loc="upper right", ncols=1)
        axs[i].set_xlabel("Distance (cm)")
        axs[i].set_ylabel("SNR (dB)")
        i = i + 1

    plt.show()
    plt.close()


def get_snr_stats_dynamic(data_bits, data_cs):
    markers = ["o", "*", "^", "x"]

    i = 0
    list_max_snr = []
    list_max_color_data = []
    for robot in robots:
        fig, axs = plt.subplots(2, 2)
        for config in configs:
            fig.suptitle(f"LSC {const.LIST_ROBOTS[1-i]}")
            for bit in bits:
                snr_bits_red, int_dist_red = [], []
                snr_bits_green, int_dist_green = [], []
                int_dist = [int(i) for i in const.LIST_DISTANCES]
                snr_bits = []
                idx = bits.index(bit)
                axx, axy = idx // 2, idx % 2
                axs[axx, axy].set_title(f"Frequency: {bit_to_freq[bit]}")
                for light_cond in light_conds:
                    for distance in distances:
                        color_data = data_cs[robot][config][bit][light_cond][distance]
                        bit_data = data_bits[robot][config][bit][light_cond][distance]
                        # print(bit_data)
                        # print(len(color_data))
                        if len(color_data) > 0:
                            # print(len(color_data))
                            snr_mean = 0
                            max_snr, max_j = 0, 0
                            for j in range(len(color_data)):
                                snr = calculate_snr_dynamic(
                                    color_data[j], bit
                                )  # random_snr_data( bit, distance)
                                snr_mean += snr
                                if snr > max_snr:
                                    max_snr = snr
                                    max_j = j
                            snr_mean = snr_mean / len(color_data)
                            list_max_snr.append(max_snr)
                            list_max_color_data.append(color_data[max_j])
                            # print(snr_mean)
                            if len(bit_data) > 0:
                                acc = np.mean(np.array(bit_data))
                                y_data = color_data[max_j][:50]
                                x_data = np.arange(len(y_data)) * 0.025
                                if acc > const.ACC_THRESHOLD:
                                    bit_state = "Connected"
                                    axs[axx, axy].plot(
                                        x_data,
                                        y_data,
                                        color="g",
                                        label=f"SNR = {round(max_snr,2)}\nAccuracy: {round(acc,2)} ({bit_state})",
                                    )
                                else:
                                    bit_state = "Disconnected"
                                    axs[axx, axy].plot(
                                        x_data,
                                        color_data[max_j][:50],
                                        color="r",
                                        label=f"SNR = {round(max_snr,2)}\nAccuracy: {round(acc,2)} ({bit_state})",
                                    )

                            axs[axx, axy].legend(loc="upper right", ncols=1)
                            axs[axx, axy].set_ylim(
                                [0.8 * np.min(y_data), 1.2 * np.max(y_data)]
                            )
        axs[axx, axy].set_xlabel("Time")
        axs[axx, axy].set_ylabel("Value")
        i = i + 1

    plt.show()
    plt.close()
