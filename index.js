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

const query = "SELECT time, avg_temp, city_name FROM daily_weather d JOIN dim_city c ON d.city_id = c.city_id WHERE city_name = $1"

async function getCity(city_name) {
    const result = await db.query(query, [city_name]);
    const rows = result.rows;
    console.log(rows);
}

app.get("/", (req, res) => {
    res.render("index.ejs", {citiesList : cities});
});

app.post("/search", async (req, res) => {
    try {
        const city_name = req.body.city_name;
        const city_name_db = cities[city_name];
        await getCity(city_name_db);
    } catch(err) {
        console.log(err)
    }
    res.redirect("/");
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
