import threading
import constants_green as const
from Utils_green import (
    get_bits,
    get_accuracy,
    get_bin_stats,
    get_general_stats,
    get_snr_stats,
    plot_color_data,
    get_data_from_files,
)


if __name__ == "__main__":

    if not const.STATS:
        get_bits(
            const.PORT,
            const.BAUDRATE,
            const.TIMEOUT,
            const.PATH_FILE_BITS,
            const.TOTAL_READINGS,
        )
        accuracy = get_accuracy(const.PATH_FILE_BITS, const.REAL_BIT)
        print("Accuracy:", accuracy)

    else:
        data_bits, data_cs = get_data_from_files(const.ROOT_DIR)
        # plot_color_data(
        #     data_cs,
        #     const.ROBOT,
        #     const.CONFIG,
        #     const.REAL_BIT,
        #     const.LIST_LIGHT_CONDS[0],
        #     const.DISTANCE,
        #     const.N_TEST,
        # )
        # get_bin_stats(data_bits)
        get_snr_stats(data_bits, data_cs)
        # get_general_stats(const.ROOT_DIR)
