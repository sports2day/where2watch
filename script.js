document.addEventListener("DOMContentLoaded", () => {
    loadEvents();
  });
  
  async function loadEvents() {
    const today = new Date().toISOString().split("T")[0];
    const url = `sports_schedule_${today}.json`;
  
    const sportColors = {
      Fußball: "#28a745",
      Radsport: "#fd7e14",
      Handball: "#007bff",
      Basketball: "#8e44ad",
      Tennis: "#c0392b",
      Unbekannt: "#6c757d"
    };
  
    const sportIcons = {
      Fußball: "⚽",
      Radsport: "🚴",
      Handball: "🤾",
      Basketball: "🏀",
      Tennis: "🎾",
      Unbekannt: "📺"
    };
  
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