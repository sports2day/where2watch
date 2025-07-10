document.addEventListener("DOMContentLoaded", () => {
    createSportFilterMenu();
    loadEvents();
    enableSportFilter();
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
  Unbekannt: "#6c757d"
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
  Unbekannt: "📺"
};


async function createSportFilterMenu() {
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
    main.insertBefore(filterContainer, document.getElementById("eventsContainer"));
}

async function enableSportFilter() {
    document.getElementById("sportFilter").addEventListener("click", (e) => {
      if (!e.target.matches("button")) return;
  
      const selected = e.target.dataset.sport;
      document.querySelectorAll(".sport-filter button").forEach(btn =>
        btn.classList.remove("filter-active")
      );
      e.target.classList.add("filter-active");
  
      document.querySelectorAll(".sport-section").forEach(section => {
        const sport = section.querySelector("h2").textContent.trim();
        if (selected === "all" || sport.includes(selected)) {
          section.style.display = "";
        } else {
          section.style.display = "none";
        }
      });
    });
  }
  
async function loadEvents() {
    const today = new Date().toISOString().split("T")[0];
    const url = `sports_schedule_${today}.json`;
    //const url = 'sports_schedule_2025-07-10.json';


    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP error ${response.status}`);
        const data = await response.json();

        const container = document.getElementById("eventsContainer");
        container.innerHTML = "";

        if (!data.events || data.events.length === 0) {
            container.innerHTML = "<p>Heute sind keine Daten verfügbar.</p>";
            return;
        }

        const groupedEvents = {};
        for (const event of data.events) {
            const sport = event.sport || "Unbekannt";
            if (!groupedEvents[sport]) groupedEvents[sport] = [];
            groupedEvents[sport].push(event);
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

                const title = document.createElement("div");
                title.className = "card-title";
                title.textContent = event.title;

                const sender = document.createElement("div");
                sender.className = "card-sender";
                sender.textContent = event.sender || "";

                card.append(time, title, sender);
                grid.appendChild(card);
            }

            section.appendChild(grid);
            container.appendChild(section);
        }

    } catch (error) {
        console.error("❌ Fehler beim Laden der Daten:", error);
        document.getElementById("eventsContainer").innerHTML =
            "<p>Heute sind keine Daten verfügbar.</p>";
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
  
  