let currentSportFilter = localStorage.getItem("lastSport") || "all";
let allEventsRaw = [];

document.addEventListener("DOMContentLoaded", () => {
  createSportFilterMenu();
  loadEvents();
  enableSportFilter();

  // Set active filter from localStorage
  const stored = localStorage.getItem("lastSport");
  if (stored && stored !== "all") {
    const btn = document.querySelector(`[data-sport="${stored}"]`);
    if (btn) btn.click(); // Triggert gleich die Filterung
  }
});


const sportColors = {
  Fußball: "#28a745",
  Radsport: "#fd7e14",
  Handball: "#007bff",
  Basketball: "#8e44ad",
  Tennis: "#c0392b",
  Snooker: "#17a2b8",
  WEC: "#6f42c1",
  Mountainbike: "#20c997",
  Motorsports: "#dc3545",
  Leichtathletik: "#ffc107",
  Superbike: "#ff5722",
  FormelE: "#00bcd4",
  Unknown: "#6c757d"
};

const sportIcons = {
  Fußball: "⚽",
  Radsport: "🚴",
  Handball: "🤾",
  Basketball: "🏀",
  Tennis: "🎾",
  Snooker: "🎱",
  WEC: "🏎️",
  Mountainbike: "🚵",
  Motorsports: "🏁",
  Leichtathletik: "🏃",
  Superbike: "🏍️",
  FormelE: "⚡",
  Unknown: "📺"
};

function debounce(func, delay = 300) {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), delay);
  };
}

async function createSportFilterMenu() {
  const searchBox = document.createElement("input");
  searchBox.type = "text";
  searchBox.placeholder = "🔍 Suche nach Team, Sender oder Sportart...";
  searchBox.id = "searchInput";
  searchBox.className = "search-box";

  const filterContainer = document.createElement("div");
  filterContainer.id = "sportFilter";
  filterContainer.className = "sport-filter";

  const allBtn = document.createElement("button");
  allBtn.textContent = "Alle";
  allBtn.dataset.sport = "all";
  allBtn.className = "filter-active";
  filterContainer.appendChild(allBtn);

  Object.entries(sportIcons).forEach(([sport, icon]) => {
    const btn = document.createElement("button");
    btn.textContent = `${icon} ${sport}`;
    btn.dataset.sport = sport;
    filterContainer.appendChild(btn);
  });

  const main = document.querySelector("main");
  main.insertBefore(searchBox, document.getElementById("eventsContainer"));
  main.insertBefore(filterContainer, document.getElementById("eventsContainer"));
}

function filterEvents() {
  const search = document.getElementById("searchInput").value.toLowerCase();
  const container = document.getElementById("eventsContainer");
  container.innerHTML = "";

  if (!allEventsRaw || allEventsRaw.length === 0) {
    container.innerHTML = "<p>Heute sind keine Daten verfügbar.</p>";
    return;
  }

  const filteredGrouped = {};

  for (const event of allEventsRaw) {
    const sport = event.sport || "Unbekannt";
    const matchesSearch =
      event.title?.toLowerCase().includes(search) ||
      event.sender?.toLowerCase().includes(search) ||
      sport.toLowerCase().includes(search);

    const matchesSport =
      currentSportFilter === "all" || sport === currentSportFilter;

    if (matchesSearch && matchesSport) {
      if (!filteredGrouped[sport]) filteredGrouped[sport] = [];
      filteredGrouped[sport].push(event);
    }
  }

  renderEvents(filteredGrouped);
}


function enableSportFilter() {
  document.getElementById("sportFilter").addEventListener("click", (e) => {
    if (!e.target.matches("button")) return;

    currentSportFilter = e.target.dataset.sport;
    localStorage.setItem("lastSport", currentSportFilter);

    document.querySelectorAll(".sport-filter button").forEach(btn =>
      btn.classList.remove("filter-active")
    );
    e.target.classList.add("filter-active");

    filterEvents();
  });

  document.getElementById("searchInput").addEventListener("input", debounce(filterEvents, 300));
}



async function loadEvents() {
  const today = new Date().toISOString().split("T")[0];
  const url = `sports_schedule_${today}.json`;

  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error ${response.status}`);
    const data = await response.json();

    allEventsRaw = data.events || [];
    filterEvents(); // Filter gleich beim Laden anwenden
  } catch (error) {
    console.error("❌ Fehler beim Laden der Daten:", error);
    document.getElementById("eventsContainer").innerHTML =
      "<p>Heute sind keine Daten verfügbar.</p>";
  }
}


async function renderEvents(groupedEvents) {
  const container = document.getElementById("eventsContainer");
  container.innerHTML = "";

  if (!groupedEvents || Object.keys(groupedEvents).length === 0) {
    container.innerHTML = "<p>Heute sind keine Daten verfügbar.</p>";
    return;
  }

  for (const [sport, events] of Object.entries(groupedEvents)) {
    events.sort((a, b) => (a.time || "").localeCompare(b.time || ""));

    const section = document.createElement("div");
    section.className = "sport-section";

    const header = document.createElement("h2");
    header.innerHTML = `${sportIcons[sport] || "📺"} ${sport}`;
    header.style.borderLeft = `6px solid ${sportColors[sport] || "#6c757d"}`;
    section.appendChild(header);

    const grid = document.createElement("div");
    grid.className = "card-grid";

    for (const event of events) {
      const card = document.createElement("div");
      card.className = "card";
      card.style.borderLeft = `5px solid ${sportColors[sport] || "#6c757d"}`;

      const time = document.createElement("div");
      time.className = "card-time";
      time.textContent = event.time || "";

      const title = document.createElement(event.link ? "a" : "div");
      title.className = "card-title";
      title.textContent = event.title;
      
      if (event.link) {
        title.href = event.link;
        title.target = "_blank";
        title.rel = "noopener noreferrer";
        title.style.textDecoration = "none";
        title.style.color = "#0077ff";
      }
      

      const sender = document.createElement("div");
      sender.className = "card-sender";
      sender.textContent = event.sender || "";

      card.append(time, title, sender);
      grid.appendChild(card);
    }

    section.appendChild(grid);
    container.appendChild(section);
  }
}

// Show or hide the scroll-to-top button depending on scroll position
window.addEventListener("scroll", () => {
  const scrollBtn = document.getElementById("scrollTop");
  if (!scrollBtn) return;
  if (window.scrollY > 300) {
    scrollBtn.classList.add("show");
  } else {
    scrollBtn.classList.remove("show");
  }
});

// Scroll smoothly to the top when the button is clicked
document.addEventListener("DOMContentLoaded", () => {
  const scrollBtn = document.getElementById("scrollTop");
  if (scrollBtn) {
    scrollBtn.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
});

