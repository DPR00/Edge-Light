## To get BIT
PORT = "COM11"  # "COM8"
PORT_USB = "COM27"
BAUDRATE = 115200
TIMEOUT = 5

## To save files
TOTAL_READINGS_MOTION = 13
TOTAL_READINGS = 100  # change the number of readings
TOTAL_READINGS_USB = 3300  # change the number of readings
TOTAL_READINGS_DYNAMIC = 273
REAL_BIT = 8  # change the bit we are evaluating
N_TEST = 2  # change de number of test
LIGHT_CONDITION = "Lab_500LX"  # change the light conditions (40000 - 60000)
DISTANCE = 100  # change the distance between LSC and color sensor
ROBOT = "GREEN"  # RED (front) OR GREEN (back)
CONFIG = "aligned"  # aligned or unaligned. #E1: extreme. E2: a little bit to the left. aligned: center
STATE = "static"  # dynamic or static
LUXB_F_S = "73500_66000_H1"
# Outdoors
# 2 - 15 - Test 3
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

LIST_ROBOTS = ["RED", "GREEN"]
LIST_CONFIG = ["aligned"]
LIST_BITS = ["2", "4", "5", "8"]
LIST_DISTANCES = ["10", "15", "20", "25", "30", "35", "40", "45", "50"]
LIST_LIGHT_CONDS = [
    "500LX"
]  # ["40000LX"]. Change to 40000LX to plot the results ofr the outdoor experiments
ACC_THRESHOLD = 90
#
