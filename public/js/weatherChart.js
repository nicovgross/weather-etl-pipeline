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

for(let i=1; i<HourlyDailySplit.length; i++) {
        const card = document
            .getElementById(`forecastChart-${i}`)
            .closest(".forecastItem");
        
        createChart(
            `forecastChart-${i}`,
            HourlyDailySplit[i],
            document.querySelector(`.weatherTabsForecast-${i}`)
        );
}