import express from "express"
import pg from "pg"
import bodyParser from "body-parser";

const app = express();
const port = 3000;

app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static("public"));

const pg_db = process.env.POSTGRES_DB
const pg_pw = process.env.POSTGRES_PASSWORD

const db = new pg.Client({
    user: "postgres",
    host: "localhost",
    database: pg_db,
    password: pg_pw,
    port: 5432
});
db.connect();

const cities = {};
const result = await db.query("SELECT DISTINCT city_name, city_display_name FROM dim_city");
const rows = result.rows;
for(let row of rows) {
    cities[row.city_display_name] = row.city_name;
}

const WeekDay = [
    {index : 0, name : "Sun"},
    {index : 1, name : "Mon"},
    {index : 2, name : "Tue" },
    {index : 3, name : "Wed"},
    {index : 4, name : "Thu"},
    {index : 5, name : "Fri"},
    {index : 6, name : "Sat"}
];

const WeekDayMap = new Map(
  WeekDay.map(day => [day.index, day])
);

const WEATHER_EMOJI = [
    {description : "Mainly clear", emoji : "🌤️"},
    {description : "Clear sky", emoji : "☀️"},
    {description : "Partly cloudy", emoji : "⛅"},
    {description : "Overcast", emoji : "☁️"},
    {description : "Depositing rime fog", emoji : "🌫️"},
    {description : "Fog", emoji : "🌫️"},
    {description : "Light drizzle", emoji : "🌦️"},
    {description : "Moderate drizzle", emoji : "🌦️"},
    {description : "Dense drizzle", emoji : "🌧️"},
    {description : "Light rain", emoji : "🌦️"},
    {description : "Moderate rain", emoji : "🌧️"},
    {description : "Heavy rain", emoji : "🌧️"},
    {description : "Light freezing rain", emoji : "🧊🌧️"},
    {description : "Heavy freezing rain", emoji : "🧊🌧️"},
    {description : "Light snow", emoji : "🌨️"},
    {description : "Moderate snow", emoji : "🌨️"},
    {description : "Heavy snow", emoji : "❄️"},
    {description : "Snow grains", emoji : "❄️"},
    {description : "LightRain showers", emoji : "🌦️"},
    {description : "Moderate rain shower", emoji : "🌧️"},
    {description : "Heavy rain shower", emoji : "⛈️"},
    {description : "Light snow shower", emoji : "🌨️"},
    {description : "Heavy snow shower", emoji : "❄️🌨️"},
    {description : "Thunderstorm", emoji : "⛈️"},
    {description : "Thunderstorm with heavy hail", emoji : "⛈️🧊"}
];

const WeatherEmojiMap = new Map(
  WEATHER_EMOJI.map(weather => [weather.description, weather])
);

function getDailyWeather(dayData) {
    const count = {};

    dayData.forEach(item => {
        count[item.weather_description] =
            (count[item.weather_description] || 0) + 1;
    });

    return Object.entries(count)
        .sort((a, b) => b[1] - a[1])[0][0];
}

async function getCityData(city_name) {
    const now = new Date();
    now.setHours(now.getHours() - 4); 
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const hourlyQuery = `
        SELECT * FROM hourly_weather h
        JOIN dim_city c
            ON h.city_id = c.city_id
        WHERE city_name = $1 AND time >= $2
        ORDER BY time;
    `;

    const dailyQuery = `
        SELECT * FROM daily_weather d
        JOIN dim_city c
            ON d.city_id = c.city_id
        WHERE city_name = $1 AND time >= $2
        ORDER BY time;
    `;

    const hourly = await db.query(hourlyQuery, [city_name, now]);
    const daily = await db.query(dailyQuery, [city_name, today]);

    return {
        hourly: hourly.rows,
        daily: daily.rows
    };
}

app.get("/", (req, res) => {
    res.render("index.ejs", {citiesList : cities, weather: null});
});

app.post("/search", async (req, res) => {
    try {
        const city_name = req.body.city_name;
        const city_name_db = cities[city_name];
        const weather = await getCityData(city_name_db);

        const groupedByDay = weather.hourly.reduce((acc, item) => {
            // Criamos um objeto Date a partir do item.time (garante o funcionamento)
            const dateObj = new Date(item.time);
            
            // Usamos getgetUTCDate e getUTCMonth para pegar o dia real do servidor/UTC
            const day = dateObj.getUTCDate();
            const month = dateObj.getUTCMonth() + 1; // +1 porque os meses no JS começam em 0
            
            const dateKey = `${day}/${month}`;
            
            if (!acc[dateKey]) {
                acc[dateKey] = [];
            }
            
            acc[dateKey].push(item);
            return acc;
        }, {});

        const HourlyDailySplit = Object.values(groupedByDay);

        const info = [];
        for(let i=0; i<HourlyDailySplit.length; i++) {
            const daily_info ={};
            const time = HourlyDailySplit[i][0].time;
            daily_info.weekday = WeekDayMap.get(time.getUTCDay()).name;
            daily_info.day = Number(time.toISOString().substring(8, 10));
            let month = Number(time.toISOString().substring(5, 7));
            if(month / 10 < 1) { month = "0" + String(month) }
            daily_info.month = month;
            const description = getDailyWeather(HourlyDailySplit[i]);
            daily_info.emoji = WeatherEmojiMap.get(description).emoji;
            info.push(daily_info);
        }

        res.render("index.ejs", {citiesList : cities, 
            weather : weather,
            info : info,
            HourlyDailySplit : HourlyDailySplit})
    } catch(err) {
        console.log(err)
    }
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
