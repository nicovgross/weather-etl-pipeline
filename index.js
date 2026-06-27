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

async function getCityData(city_name) {
    const now = new Date();
    now.setHours(now.getHours() - 1); 

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
    const daily = await db.query(dailyQuery, [city_name, now]);

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
        //console.log(weather.hourly[0]);

        const day = weather.hourly[0].time.getDate();
        let month = weather.hourly[0].time.getMonth() + 1;
        if(month / 10 < 1) { month = "0" + String(month) }
        const weekDay = weather.hourly[0].time.getDay();
        const weekDaytoString = WeekDayMap.get(weekDay).name;
        const weather_emoji = WeatherEmojiMap.get(weather.hourly[0].weather_description).emoji

        res.render("index.ejs", {citiesList : cities, 
            weather : weather,
            day : day,
            month : month,
            weekDay : weekDaytoString,
            weather_emoji : weather_emoji})
    } catch(err) {
        console.log(err)
    }
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
