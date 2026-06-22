console.log("weatherChart loaded");

const hourlyData = window.weatherData;

console.log(hourlyData);

const labels = hourlyData.map(item => {
    const date = new Date(item.time);

    return date.toLocaleTimeString("pt-BR", {
        hour: "2-digit",
        minute: "2-digit"
    });
});

const temperatures = hourlyData.map(
    item => item.temperature_c
);

const ctx = document
    .getElementById("weatherChart")
    .getContext("2d");

let chart = new Chart(ctx, {
    type: "line",
    data: {
        labels,
        datasets: [{
            label: "Temperature (°C)",
            data: temperatures,
            borderWidth: 2,
            borderColor: '#000000',
            tension: 0.3
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