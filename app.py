import time
import threading
import uvicorn

from gpiozero import (
    DigitalInputDevice
)

from hardware.sensors import (
    read_ldr,
    read_adt7410,
    pir
)

from hardware.servo import (
    open_curtain,
    close_curtain,
    servo
)
from hardware.buzzer import buzzer

from states import (
    start, 
    alarm_hour, 
    alarm_minute, 
    alarm_active, 
    movement_count, 
    temp_history, 
    light_history, 
    sleep_report, 
    last_motion_state
)

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

STOP_BUTTON_PIN = 26

stop_button = DigitalInputDevice(
    STOP_BUTTON_PIN,
    pull_up=True
)

app = FastAPI()

app.mount(
    "/sleep_monitor/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(
    directory="templates"
)

# =====================================
# SCORE
# =====================================

def calculate_score():

    if len(temp_history) == 0:
        return None

    avg_temp = (
        sum(temp_history)
        / len(temp_history)
    )

    avg_light = (
        sum(light_history)
        / len(light_history)
    )

    score = 0

    # movement (40)

    if movement_count <= 50:
        score += 40
    elif movement_count <= 100:
        score += 30
    elif movement_count <= 200:
        score += 20
    else:
        score += 10

    # temp (30)

    if 20 <= avg_temp <= 28:
        score += 30
    elif 12 <= avg_temp <= 19 or 29 <= avg_temp <= 35:
        score += 0
    else:
        score -= 5

    # light (30)

    if avg_light < 150:
        score += 30
    elif avg_light < 400:
        score += 10
    elif avg_light < 500:
        score += 5
    elif avg_light < 600:
        score += 0
    else:
        score -= 5

    return {
        "score": score,
        "movement": movement_count,
        "avg_temp": round(avg_temp, 2),
        "avg_light": round(avg_light, 2)
    }

# =====================================
# SENSOR THREAD
# =====================================

def sensor_thread():

    global movement_count
    global last_motion_state

    while True:

        if start:

            temp_history.append(
                read_adt7410()
            )

            light_history.append(
                read_ldr()
            )

            motion = bool(pir.value)

            if motion and not last_motion_state:
                movement_count += 1

            last_motion_state = motion

        time.sleep(0.2)

# =====================================
# ALARM THREAD
# =====================================

def alarm_thread():

    global start
    global alarm_active
    global sleep_report

    while True:

        if start:

            now = time.localtime()

            if (
                now.tm_hour == alarm_hour
                and
                now.tm_min == alarm_minute
            ):

                alarm_active = True

                open_curtain()

                sleep_report = (
                    calculate_score()
                )

                start = False

        if alarm_active:

            buzzer.on()
            time.sleep(0.3)

            buzzer.off()
            time.sleep(0.7)

        else:
            time.sleep(1)

def stop_button_thread():
    global alarm_active
    while True:
        if (
            alarm_active
            and
            stop_button.value
        ):
            alarm_active = False
            buzzer.off()
            print(
                "Alarm stopped by button"
            )
            time.sleep(0.1)
        time.sleep(0.1)

# =====================================
# API
# =====================================

@app.get("/sleep/start")
def start_sleep(
    hour: int,
    minute: int
):

    global start
    global alarm_hour
    global alarm_minute

    global movement_count
    global temp_history
    global light_history

    movement_count = 0
    temp_history = []
    light_history = []

    alarm_hour = hour
    alarm_minute = minute

    close_curtain()

    start = True

    return {
        "start": True
    }


@app.get("/alarm/stop")
def stop_alarm():

    global alarm_active

    alarm_active = False

    buzzer.off()

    return {"ok": True}


@app.get("/status")
def status():
    if start:
        temperature = read_adt7410()
        light = read_ldr()
    else:
        temperature = None
        light = None

    return {
        "start": start,
        "alarm_active": alarm_active,
        "temperature": temperature,
        "light": light,
        "movement": movement_count
    }


@app.get("/report")
def report():

    return sleep_report


@app.get(
    "/sleep_monitor",
    response_class=HTMLResponse
)
async def index(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

# =====================================
# THREAD
# =====================================
threading.Thread(
    target=stop_button_thread,
    daemon=True
).start()

threading.Thread(
    target=sensor_thread,
    daemon=True
).start()

threading.Thread(
    target=alarm_thread,
    daemon=True
).start()

open_curtain()

# =====================================

if __name__ == "__main__":

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )