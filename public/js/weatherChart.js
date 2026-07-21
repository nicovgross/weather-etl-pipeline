//const hourlyData = window.weatherData;
//const HourlyDailySplit = window.HourlyDailySplit;
////console.log(hourlyData)
//
//const labels = hourlyData.map(item => {
//    const date = new Date(item.time);
//
//    return date.toLocaleTimeString("pt-BR", {
//        hour: "2-digit",
//        minute: "2-digit"
//    });
//}).slice(0, 24);
//
//const temperatures = hourlyData.map(
//    item => item.temperature_c
//).slice(0, 24);
//
//const datasets = {
//
//    temp: {
//        label: "Temperature (°C)",
//        data: hourlyData.map(item => item.temperature_c).slice(0, 24)
//    },
//
//    "rain-prob": {
//        label: "Rain Probability (%)",
//        data: hourlyData.map(item => item.precipitation_probability_pct).slice(0, 24)
//    },
//
//    "rain-mm": {
//        label: "Precipitation (mm)",
//        data: hourlyData.map(item => item.precipitation_mm).slice(0, 24)
//    }
//};
//
//const ctx = document
//    .getElementById("weatherChart")
//    .getContext("2d");
//
//let chart = new Chart(ctx, {
//    type: "line",
//    data: {
//        labels,
//
//        datasets: [{
//            label: datasets.temp.label,
//            data: datasets.temp.data,
//            borderWidth: 2,
//            borderColor: '#000000',
//            tension: 0
//        }]
//    },
//    options: {
//        responsive: true,
//        maintainAspectRatio: false,
//        plugins: {
//        legend: {
//            display: false // This completely hides the legend
//            }
//        }
//    }
//});
//
//const buttons = document.querySelectorAll(".weatherTabs button");
//
//buttons.forEach(button => {
//
//    button.addEventListener("click", () => {
//
//        const type = button.dataset.type;
//
//        chart.data.datasets[0].label =
//            datasets[type].label;
//
//        chart.data.datasets[0].data =
//            datasets[type].data;
//
//
//        chart.update();
//
//        buttons.forEach(btn =>
//            btn.classList.remove("active")
//        );
//
//        button.classList.add("active");
//
//    });
//
//});
//


function createChart(canvasId, hourlyData, tabContainer) {
        
        const labels = hourlyData.map(item =>
            item.time.substring(11, 16)
        );

        const datasets = {

            temp: {
                label: "Temperature (°C)",
                data: hourlyData.map(item => item.temperature_c)
            },

            "rain-prob": {
                label: "Rain Probability (%)",
                data: hourlyData.map(item => item.precipitation_probability_pct)
            },

            "rain-mm": {
                label: "Precipitation (mm)",
                data: hourlyData.map(item => item.precipitation_mm)
            }
        };

        const ctx = document
            .getElementById(canvasId)
            .getContext("2d");

        let chart = new Chart(ctx, {
            type: "line",
            data: {
                labels,

                datasets: [{
                    label: datasets.temp.label,
                    data: datasets.temp.data,
                    borderWidth: 2,
                    borderColor: '#000000',
                    tension: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                legend: {
                    display: false // This completely hides the legend
                    }
                }
            }
        });

        const buttons = tabContainer.querySelectorAll("button");

        buttons.forEach(button => {

            button.addEventListener("click", () => {

                const type = button.dataset.type;

                chart.data.datasets[0].label =
                    datasets[type].label;

                chart.data.datasets[0].data =
                    datasets[type].data;


                chart.update();

                buttons.forEach(btn =>
                    btn.classList.remove("active")
                );

                button.classList.add("active");

            });

        });
}

const HourlyDailySplit = window.HourlyDailySplit;

const Today = window.HourlyData.slice(0, 24);

const card = document
    .getElementById(`forecastChart-0`)
    .closest(".forecastItem");

createChart(
    `forecastChart-0`,
    Today,
    document.querySelector(".weatherTabs")
);

console.log(HourlyDailySplit[1].time)


for(let i=1; i<HourlyDailySplit.length; i++) {
        const card = document
            .getElementById(`forecastChart-${i}`)
            .closest(".forecastItem");
        
        createChart(
            `forecastChart-${i}`,
            HourlyDailySplit[i],
            document.querySelector(".weatherTabs")
        );

}