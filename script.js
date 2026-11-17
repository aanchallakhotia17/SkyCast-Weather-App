
const searchForm = document.getElementById("searchForm");
const cityInput = document.getElementById("cityInput");
const searchButton = document.getElementById("searchButton");
const message = document.getElementById("message");

const cityName = document.getElementById("cityName");
const temperature = document.getElementById("temperature");
const feelsLike = document.getElementById("feelsLike");
const weatherCondition = document.getElementById("weatherCondition");
const currentIcon = document.getElementById("currentIcon");
const humidity = document.getElementById("humidity");
const windSpeed = document.getElementById("windSpeed");
const pressure = document.getElementById("pressure");
const currentDate = document.getElementById("currentDate");

currentDate.textContent = new Date().toLocaleDateString("en-IN", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric"
});

function displayWeather(weather) {
    cityName.textContent = weather.city;
    temperature.textContent = weather.temperature;
    feelsLike.textContent = `${weather.feelsLike}°C`;
    weatherCondition.textContent = weather.condition;
    humidity.textContent = `${weather.humidity}%`;
    windSpeed.textContent = `${weather.windSpeed} km/h`;
    pressure.textContent = `${weather.pressure} hPa`;

    currentIcon.textContent = "";
    currentIcon.setAttribute("aria-label", weather.condition);

    const icon = document.createElement("img");
    icon.src = `https://openweathermap.org/img/wn/${weather.icon}@2x.png`;
    icon.alt = weather.condition;
    icon.width = 90;
    icon.height = 90;

    currentIcon.appendChild(icon);
}

searchForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const city = cityInput.value.trim();

    if (!city) {
        message.textContent = "Please enter a city name.";
        return;
    }

    searchButton.disabled = true;
    searchButton.textContent = "Loading...";
    message.textContent = "Fetching current weather...";

    try {
        const response = await fetch(
            `/api/weather?city=${encodeURIComponent(city)}`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Unable to fetch weather.");
        }

        displayWeather(data);
        message.textContent = `Live weather loaded for ${data.city}.`;
        message.style.color = "#70d6ff";

    } catch (error) {
        message.textContent = error.message;
        message.style.color = "#ffca80";

    } finally {
        searchButton.disabled = false;
        searchButton.textContent = "Search";
    }
});

message.textContent = "Search a city to see its current weather.";

const loadHistoryButton = document.getElementById("loadHistory");
const historyBody = document.getElementById("historyBody");
const historyMessage = document.getElementById("historyMessage");

loadHistoryButton.addEventListener("click", async () => {
    historyMessage.textContent = "Loading history...";
    historyBody.replaceChildren();

    try {
        const response = await fetch("/api/history");
        const records = await response.json();

        if (!response.ok) {
            throw new Error(records.error || "Could not load history.");
        }

        if (records.length === 0) {
            historyMessage.textContent = "No searches saved yet.";
            return;
        }

        records.forEach(record => {
            const row = document.createElement("tr");

            [
                record.city,
                `${record.temperature} °C`,
                `${record.humidity}%`,
                record.weather_condition,
                new Date(record.searched_at).toLocaleString("en-IN")
            ].forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = value ?? "";
                row.appendChild(cell);
            });

            historyBody.appendChild(row);
        });

        historyMessage.textContent =
            `${records.length} saved search(es) found.`;
    } catch (error) {
        historyMessage.textContent = error.message;
    }
});

const forecastContainer = document.getElementById("forecastContainer");
const forecastCity = document.getElementById("forecastCity");
const forecastMessage = document.getElementById("forecastMessage");

async function loadForecast(city) {
    forecastMessage.textContent = "Loading live forecast...";
    forecastContainer.replaceChildren();

    try {
        const response = await fetch(
            `/api/forecast?city=${encodeURIComponent(city)}`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Forecast load nahi hua.");
        }

        forecastCity.textContent = `Forecast for ${data.city}`;

        if (!data.forecast || data.forecast.length === 0) {
            forecastMessage.textContent = "Forecast data available nahi hai.";
            return;
        }

        data.forecast.forEach(day => {
            const card = document.createElement("article");
            card.className = "forecast-card";

            const date = document.createElement("p");
            date.className = "forecast-date";
            date.textContent = new Date(
                `${day.date}T12:00:00`
            ).toLocaleDateString("en-IN", {
                weekday: "short",
                day: "numeric",
                month: "short"
            });

            const icon = document.createElement("img");
            icon.src = `https://openweathermap.org/img/wn/${day.icon}@2x.png`;
            icon.alt = day.condition;

            const condition = document.createElement("p");
            condition.className = "forecast-condition";
            condition.textContent = day.condition;

            const temperatures = document.createElement("p");
            temperatures.className = "forecast-temperatures";
            temperatures.textContent = `${day.max}°C / ${day.min}°C`;

            card.append(date, icon, condition, temperatures);
            forecastContainer.appendChild(card);
        });

        forecastMessage.textContent =
            "Live forecast loaded successfully.";

    } catch (error) {
        forecastMessage.textContent = error.message;
    }
}

// Load forecast whenever a city is searched
searchForm.addEventListener("submit", function () {
    const city = cityInput.value.trim();

    if (city) {
        loadForecast(city);
    }
});