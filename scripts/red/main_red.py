import constants_red as const
from Utils_red import get_bits, get_accuracy, get_stats


if __name__ == "__main__":

    if not const.STATS:
        get_bits(
            const.PORT,
            const.BAUDRATE,
            const.TIMEOUT,
            const.PATH_FILE_BITS,
            const.TOTAL_READINGS,
        )
        accuracy = get_accuracy(const.PATH_FILE_BITS)
        print("Accuracy:", accuracy)
    else:
        get_stats(const.ROOT_DIR)
