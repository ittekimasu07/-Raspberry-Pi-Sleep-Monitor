function startSleep(){

    const time =
        document.getElementById(
            "alarm_time"
        ).value;

    if(!time){

        alert(
            "アラーム時刻設定"
        );

        return;
    }

    const parts =
        time.split(":");

    const hour =
        parts[0];

    const minute =
        parts[1];

    fetch(
        `/sleep/start?hour=${hour}&minute=${minute}`
    )
    .then(
        r => r.json()
    )
    .then(
        () => {

            alert(
                "睡眠モード開始済"
            );
        }
    );
}

function stopAlarm(){

    fetch(
        "/alarm/stop"
    );
}

function updateStatus(){

    fetch(
        "/status"
    )
    .then(
        r => r.json()
    )
    .then(
        data => {

            document.getElementById(
                "temperature"
            ).innerText =
                data.temperature;

            document.getElementById(
                "light"
            ).innerText =
                data.light;

            document.getElementById(
                "movement"
            ).innerText =
                data.movement;

            document.getElementById(
                "sleep_mode"
            ).innerText =
                data.sleep_mode
                ? "ON"
                : "OFF";

            const banner =
                document.getElementById(
                    "status_banner"
                );

            if(
                data.alarm_active
            ){

                banner.innerText =
                    "アラームが鳴っている";
            }

            else if(
                data.sleep_mode
            ){

                banner.innerText =
                    "睡眠中";
            }

            else{

                banner.innerText =
                    "準備できて";
            }
        }
    );
}

function updateReport(){

    fetch(
        "/report"
    )
    .then(
        r => r.json()
    )
    .then(
        data => {

            if(
                !data
            ){
                return;
            }

            document.getElementById(
                "score"
            ).innerText =
                data.score;

            document.getElementById(
                "avg_temp"
            ).innerText =
                data.avg_temp;

            document.getElementById(
                "avg_light"
            ).innerText =
                data.avg_light;

            document.getElementById(
                "report_movement"
            ).innerText =
                data.movement;

            let text =
                "不良";

            if(
                data.score >= 80
            ){

                text =
                    "素晴らしい";
            }

            else if(
                data.score >= 60
            ){

                text =
                    "良い";
            }

            document.getElementById(
                "score_text"
            ).innerText =
                text;
        }
    )
    .catch(
        () => {}
    );
}

setInterval(
    updateStatus,
    1000
);

setInterval(
    updateReport,
    3000
);

updateStatus();
updateReport();