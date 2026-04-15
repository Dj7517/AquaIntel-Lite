import os
from dotenv import load_dotenv

load_dotenv()

TANK_CAPACITY_LITERS = int(os.getenv("TANK_CAPACITY_LITERS", 10000))
IDEAL_LITERS_PER_PERSON_PER_DAY = int(os.getenv("IDEAL_LITERS_PER_PERSON_PER_DAY", 135))
APP_TITLE = os.getenv("APP_TITLE", "AquaIntel Lite")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

CLUSTER_LABELS = {
    0: ("🟢 Efficient", "#22c55e"),
    1: ("🟡 Moderate", "#f59e0b"),
    2: ("🔴 High Usage", "#ef4444"),
}
