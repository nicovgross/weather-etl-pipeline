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

const doNotCapitalize = ["de", "da", "do"]

function formatCityName(city_name) {
    const new_name = city_name.replaceAll("_", " ");
    return new_name.split(' ')                          
    .map(word => doNotCapitalize.includes(word.toLowerCase()) 
    ? word.toLowerCase() 
    : (word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()))
    .join(' ');
}

const cities = {};
const result = await db.query("SELECT DISTINCT city_name FROM dim_city");
const rows = result.rows;
for(let row of rows) {
    cities[formatCityName(row.city_name)] = row.city_name;
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

async function getCityData(city_name) {
    const today = new Date();
    const day = today.getDate();
    const month = today.getMonth(); 
    const year = today.getFullYear();

    const hourlyQuery = `
        SELECT * FROM hourly_weather h
        JOIN dim_city c
            ON h.city_id = c.city_id
        WHERE city_name = $1 AND 
        EXTRACT(DAY from time) >= $2 AND
        EXTRACT(MONTH from time) >= $3 AND
        EXTRACT(YEAR from time) >= $4
        ORDER BY time;
    `;

    const dailyQuery = `
        SELECT * FROM daily_weather d
        JOIN dim_city c
            ON d.city_id = c.city_id
        WHERE city_name = $1 AND 
        EXTRACT(DAY from time) >= $2 AND
        EXTRACT(MONTH from time) >= $3 AND
        EXTRACT(YEAR from time) >= $4
        ORDER BY time;
    `;

    const hourly = await db.query(hourlyQuery, [city_name, day, month, year]);
    const daily = await db.query(dailyQuery, [city_name, day, month, year]);

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
        console.log(weather.hourly[0]);

        const day = weather.hourly[0].time.getDate();
        let month = weather.hourly[0].time.getMonth() + 1;
        if(month / 10 < 1) { month = "0" + String(month) }
        const weekDay = weather.hourly[0].time.getDay();
        const weekDaytoString = WeekDayMap.get(weekDay).name;

        res.render("index.ejs", {citiesList : cities, 
            weather : weather,
            day : day,
            month : month,
            weekDay : weekDaytoString})
    } catch(err) {
        console.log(err)
    }
    //res.redirect("/");
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
