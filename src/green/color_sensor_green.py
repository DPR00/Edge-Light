import constants_green as const
from Utils_green import get_color_data


if __name__ == "__main__":

    if not const.STATS:
        get_color_data(
            const.PORT_USB,
            const.BAUDRATE,
            const.TIMEOUT,
            const.PATH_FILE_CS,
            const.TOTAL_READINGS_USB,
        )
        print("Done")

    # else:
    # get_stats(const.ROOT_DIR)
