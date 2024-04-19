## To get BIT
PORT = "COM8"
PORT_USB = "COM4"
BAUDRATE = 115200
TIMEOUT = 5

## To save files
TOTAL_READINGS = 100  # change the number of readings
TOTAL_READINGS_USB = 3300  # change the number of readings
TOTAL_READINGS_DYNAMIC = 273
REAL_BIT = 8  # change the bit we are evaluating
N_TEST = 2  # change de number of test
LIGHT_CONDITION = "Lab_500LX"  # change the light conditions (40000 - 60000)
DISTANCE = 100  # change the distance between LSC and color sensor
ROBOT = "RED"  # RED OR GREEN
CONFIG = "aligned"  # aligned or unaligned
STATE = "static"
LUXB_F_S = "73000_73000_H1"

ROOT_DIR = "./logs/18_04_24_th2"
FILENAME = (
    "Bit"
    + str(REAL_BIT)
    + "_Test"
    + str(N_TEST)
    + "_LC"
    + LIGHT_CONDITION
    + "_Distance"
    + str(DISTANCE)
    + "_Robot"
    + ROBOT
    + "_CONFIG"
    + CONFIG
    + ".csv"
)

PATH_FILE_BITS = ROOT_DIR + "/" + FILENAME
PATH_FILE_CS = ROOT_DIR + "/CS_" + FILENAME
STATS = 0
