let currentSportFilter = localStorage.getItem("lastSport") || "all";
let allEventsRaw = [];
let sportIcons = {};
let sportColors = {};

async function loadSportMeta() {
  try {
    const response = await fetch("tools/config/sport_meta.json");
    const data = await response.json();

    for (const [sport, meta] of Object.entries(data)) {
      sportIcons[sport] = meta.icon;
      sportColors[sport] = meta.color;
    }
  } catch (error) {
    console.error("❌ Fehler beim Laden der Sport-Metadaten:", error);
  }
}


document.addEventListener("DOMContentLoaded", async () => {
  await loadSportMeta();
  await waitForElement("#eventsContainer");
  await waitForElement("#searchInput");

  createSportFilterMenu();
  loadEvents();
  enableSportFilter();

  // Letzten Filter aus localStorage setzen
  const stored = localStorage.getItem("lastSport");
  if (stored && stored !== "all") {
    const btn = document.querySelector(`[data-sport="${stored}"]`);
    if (btn) btn.click();
  }
});


function debounce(func, delay = 300) {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), delay);
  };
}

async function waitForElement(selector, timeout = 3000) {
  return new Promise((resolve, reject) => {
    const interval = 50;
    let elapsed = 0;

    const check = () => {
      const el = document.querySelector(selector);
      if (el) return resolve(el);

      elapsed += interval;
      if (elapsed >= timeout) return reject(`⏰ Element ${selector} nicht gefunden`);
      setTimeout(check, interval);
    };

    check();
  });
}

function createSportFilterMenu() {
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
  const eventsContainer = document.getElementById("eventsContainer");

  if (main && eventsContainer) {
    main.insertBefore(filterContainer, eventsContainer);
  }
}

function filterEvents() {
  const searchInput = document.getElementById("searchInput");
  if (!searchInput) return;

  const search = searchInput.value.toLowerCase();
  const container = document.getElementById("eventsContainer");
  if (!container) return;

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
  const filter = document.getElementById("sportFilter");
  if (filter) {
    filter.addEventListener("click", (e) => {
      if (!e.target.matches("button")) return;

      currentSportFilter = e.target.dataset.sport;
      localStorage.setItem("lastSport", currentSportFilter);

      document.querySelectorAll(".sport-filter button").forEach(btn =>
        btn.classList.remove("filter-active")
      );
      e.target.classList.add("filter-active");

      filterEvents();
    });
  }

  const search = document.getElementById("searchInput");
  if (search) {
    search.addEventListener("input", debounce(filterEvents, 300));
  }
}

async function loadEvents() {
  const today = new Date().toLocaleDateString('sv-SE', {
  timeZone: 'Europe/Berlin',
});
  const url =  `sports_schedule_${today}.json`; 

  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error ${response.status}`);
    const data = await response.json();

    allEventsRaw = data.events || [];
    filterEvents();
  } catch (error) {
    console.error("❌ Fehler beim Laden der Daten:", error);
    const container = document.getElementById("eventsContainer");
    if (container) {
      container.innerHTML = "<p>Heute sind keine Daten verfügbar.</p>";
    }
  }
}

async function renderEvents(groupedEvents) {
  const container = document.getElementById("eventsContainer");
  if (!container) return;
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

      // Immer interner Link zur Eventseite – basiert auf 'slug'
      const title = document.createElement("a");
      title.className = "card-title";
      title.textContent = event.title;
      title.href = event.slug ? `events/${event.slug}.html` : "#";
      title.target = "_self";
      title.rel = "noopener noreferrer";
      title.style.textDecoration = "none";
      title.style.color = "#0077ff";

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

// Scroll-to-Top Button anzeigen/verstecken
document.addEventListener("DOMContentLoaded", () => {
  const scrollButton = document.getElementById("scrollTop");
  if (scrollButton) {
    scrollButton.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  window.addEventListener("scroll", () => {
    if (scrollButton) {
      scrollButton.classList.toggle("show", window.scrollY > 300);
    }
  });
});
