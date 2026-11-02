/**
 * AI Trip Planner - Frontend Application Logic
 * Manages form interactions, map visualizations, tab navigation,
 * AI concierge chat, and state persistence.
 */

// Global map instances
let tripMap = null;
let mapMarkers = [];
let routePolyline = null;

// Synchronize days range and number display
function updateDaysDisplay(val) {
    const daysRange = document.getElementById("days-range");
    const daysInput = document.getElementById("days");
    const daysBadge = document.getElementById("days-badge");

    if (daysRange) daysRange.value = val;
    if (daysInput) daysInput.value = val;
    if (daysBadge) daysBadge.textContent = `${val} Day${val > 1 ? "s" : ""}`;
}

// Preset destination quick-fill
function setDestination(dest, days, style, budget) {
    const destInput = document.getElementById("destination");
    if (destInput) {
        destInput.value = dest;
        updateDaysDisplay(days);

        const styleSelect = document.getElementById("travel_style");
        if (styleSelect) {
            for (let opt of styleSelect.options) {
                if (opt.text.toLowerCase().includes(style.toLowerCase())) {
                    styleSelect.value = opt.value;
                    break;
                }
            }
        }

        const budgetSelect = document.getElementById("budget_tier");
        if (budgetSelect) budgetSelect.value = budget;

        const formElem = document.getElementById("planner-form");
        if (formElem) {
            formElem.scrollIntoView({ behavior: "smooth" });
            destInput.focus();
        }
    }
}

// Toggle advanced AI settings
function toggleAdvancedSettings() {
    const panel = document.getElementById("advanced-settings");
    const chevron = document.getElementById("advanced-chevron");
    if (panel) {
        const isHidden = panel.classList.contains("hidden");
        if (isHidden) {
            panel.classList.remove("hidden");
            if (chevron) chevron.classList.add("rotate-180");
        } else {
            panel.classList.add("hidden");
            if (chevron) chevron.classList.remove("rotate-180");
        }
    }
}

// Handle Trip Planning Form Submission
async function handleTripSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const destInput = document.getElementById("destination");

    if (!destInput || !destInput.value.trim()) {
        showToast("Please enter a destination", "error");
        return;
    }

    // Collect interest checkboxes
    const interestCheckboxes = document.querySelectorAll("input[name='interest_pill']:checked");
    const selectedInterests = Array.from(interestCheckboxes).map(cb => cb.value);

    const payload = {
        destination: destInput.value.trim(),
        days: parseInt(document.getElementById("days").value, 10) || 3,
        travelers_count: parseInt(document.getElementById("travelers_count").value, 10) || 1,
        travel_style: document.getElementById("travel_style").value,
        budget_tier: document.getElementById("budget_tier").value,
        currency: document.getElementById("currency").value,
        pace: document.getElementById("pace").value,
        dietary_restrictions: [document.getElementById("dietary").value],
        interests: selectedInterests.length > 0 ? selectedInterests : ["Culture", "Food", "Sightseeing"],
        ai_provider: document.getElementById("ai_provider").value,
        api_key: document.getElementById("api_key") ? document.getElementById("api_key").value.trim() : ""
    };

    // Show loading modal with progressive feedback
    const overlay = document.getElementById("loading-overlay");
    const loadingStep = document.getElementById("loading-step");
    const progressBar = document.getElementById("progress-bar");
    if (overlay) overlay.classList.remove("hidden");

    const steps = [
        { text: `Gathering local insider highlights for ${payload.destination}...`, width: "35%" },
        { text: "Mapping coordinates and optimal transit routes...", width: "65%" },
        { text: "Calculating day-by-day budget and packing essentials...", width: "90%" }
    ];

    let stepIdx = 0;
    const interval = setInterval(() => {
        if (stepIdx < steps.length) {
            if (loadingStep) loadingStep.textContent = steps[stepIdx].text;
            if (progressBar) progressBar.style.width = steps[stepIdx].width;
            stepIdx++;
        }
    }, 900);

    try {
        const response = await fetch("/api/plan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        clearInterval(interval);

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || "Failed to generate itinerary");
        }

        const data = await response.json();
        if (progressBar) progressBar.style.width = "100%";
        if (loadingStep) loadingStep.textContent = "Done! Opening your itinerary...";

        setTimeout(() => {
            window.location.href = data.redirect_url;
        }, 500);

    } catch (err) {
        clearInterval(interval);
        if (overlay) overlay.classList.add("hidden");
        showToast(err.message || "An error occurred while creating trip", "error");
    }
}

// Switch between itinerary tabs (Timeline, Map, Budget, Packing)
function switchTab(tabName) {
    const tabs = ["timeline", "map", "budget", "packing"];
    tabs.forEach(t => {
        const pane = document.getElementById(`tab-content-${t}`);
        const btn = document.getElementById(`tab-btn-${t}`);
        if (pane) {
            if (t === tabName) {
                pane.classList.remove("hidden");
            } else {
                pane.classList.add("hidden");
            }
        }
        if (btn) {
            if (t === tabName) {
                btn.className = "tab-btn pb-4 px-1 border-b-2 border-sky-600 text-sky-600 flex items-center gap-2";
            } else {
                btn.className = "tab-btn pb-4 px-1 border-b-2 border-transparent text-slate-500 hover:text-slate-700 flex items-center gap-2";
            }
        }
    });

    if (tabName === "map" && tripMap) {
        setTimeout(() => {
            tripMap.invalidateSize();
        }, 150);
    }
}

// Initialize Leaflet Map
function initTripMap() {
    const mapContainer = document.getElementById("trip-map");
    const jsonElem = document.getElementById("trip-json");
    if (!mapContainer || !jsonElem) return;

    try {
        const trip = JSON.parse(jsonElem.textContent);
        const center = trip.map_center || { lat: 48.8566, lng: 2.3522, zoom: 12 };

        tripMap = L.map("trip-map").setView([center.lat, center.lng], center.zoom || 12);

        // OpenStreetMap Tile Layer
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 18
        }).addTo(tripMap);

        const latLngs = [];
        let markerCount = 1;

        trip.days.forEach(day => {
            day.activities.forEach(act => {
                if (act.lat && act.lng) {
                    const latLng = [act.lat, act.lng];
                    latLngs.push(latLng);

                    // Custom numbered marker icon
                    const iconHtml = `<div class="custom-pin w-7 h-7">${markerCount}</div>`;
                    const customIcon = L.divIcon({
                        className: "custom-div-icon",
                        html: iconHtml,
                        iconSize: [28, 28],
                        iconAnchor: [14, 14],
                        popupAnchor: [0, -14]
                    });

                    const popupContent = `
                        <div class="space-y-1">
                            <span class="inline-block px-1.5 py-0.5 rounded text-[10px] font-bold bg-sky-100 text-sky-800">Day ${day.day_number} • ${act.time_slot}</span>
                            <h4 class="font-bold text-slate-900 text-sm">${act.title}</h4>
                            <p class="text-xs text-slate-500">${act.location_name}</p>
                            <p class="text-xs text-slate-600 mt-1 line-clamp-3">${act.description}</p>
                            ${act.insider_tip ? `<div class="text-[11px] text-amber-700 font-medium mt-1">💡 ${act.insider_tip}</div>` : ""}
                        </div>
                    `;

                    const marker = L.marker(latLng, { icon: customIcon })
                        .bindPopup(popupContent)
                        .addTo(tripMap);

                    marker.dayNumber = day.day_number;
                    mapMarkers.push(marker);
                    markerCount++;
                }
            });
        });

        // Add polyline connecting sequence of sights
        if (latLngs.length > 1) {
            routePolyline = L.polyline(latLngs, {
                color: "#0284c7",
                weight: 3.5,
                opacity: 0.7,
                dashArray: "6, 8"
            }).addTo(tripMap);

            tripMap.fitBounds(L.latLngBounds(latLngs).pad(0.15));
        }

    } catch (e) {
        console.error("Map initialization failed", e);
    }
}

// Filter map markers by day
function filterMapMarkers(dayFilter) {
    if (!tripMap) return;

    const latLngs = [];
    mapMarkers.forEach(marker => {
        if (dayFilter === "all" || marker.dayNumber.toString() === dayFilter.toString()) {
            marker.addTo(tripMap);
            latLngs.push(marker.getLatLng());
        } else {
            tripMap.removeLayer(marker);
        }
    });

    if (routePolyline) {
        if (dayFilter === "all") {
            routePolyline.addTo(tripMap);
        } else {
            tripMap.removeLayer(routePolyline);
        }
    }

    if (latLngs.length > 0) {
        tripMap.fitBounds(L.latLngBounds(latLngs).pad(0.15));
    }
}

// Persistent Packing List Checkbox State
function savePackingState(tripId) {
    const checkboxes = document.querySelectorAll("#tab-content-packing input[type='checkbox']");
    const state = {};
    checkboxes.forEach(cb => {
        state[cb.id] = cb.checked;
    });
    localStorage.setItem(`wanderai_packing_${tripId}`, JSON.stringify(state));
}

function loadPackingState(tripId) {
    const raw = localStorage.getItem(`wanderai_packing_${tripId}`);
    if (!raw) return;
    try {
        const state = JSON.parse(raw);
        Object.entries(state).forEach(([id, checked]) => {
            const cb = document.getElementById(id);
            if (cb) cb.checked = checked;
        });
    } catch (e) {
        console.error("Could not load packing state", e);
    }
}

// AI Concierge Chat Drawer
function toggleChatDrawer() {
    const drawer = document.getElementById("chat-drawer");
    if (drawer) {
        drawer.classList.toggle("translate-x-full");
    }
}

function sendQuickPrompt(promptText) {
    const input = document.getElementById("chat-input");
    if (input) {
        input.value = promptText;
        const form = document.getElementById("chat-form");
        if (form) form.dispatchEvent(new Event("submit"));
    }
}

async function handleChatSubmit(e, tripId) {
    e.preventDefault();
    const input = document.getElementById("chat-input");
    const container = document.getElementById("chat-messages");
    if (!input || !container) return;

    const msg = input.value.trim();
    if (!msg) return;

    // Append user message
    const userMsgElem = document.createElement("div");
    userMsgElem.className = "bg-slate-900 text-white p-3 rounded-2xl rounded-tr-none ml-6 leading-relaxed";
    userMsgElem.textContent = msg;
    container.appendChild(userMsgElem);
    input.value = "";
    container.scrollTop = container.scrollHeight;

    // Append typing indicator
    const typingElem = document.createElement("div");
    typingElem.id = "typing-indicator";
    typingElem.className = "bg-slate-100 text-slate-500 p-3 rounded-2xl rounded-tl-none mr-6 flex items-center gap-1.5";
    typingElem.innerHTML = `<span class="inline-block w-2 h-2 rounded-full bg-slate-400 animate-pulse"></span><span class="inline-block w-2 h-2 rounded-full bg-slate-400 animate-pulse delay-100"></span><span class="inline-block w-2 h-2 rounded-full bg-slate-400 animate-pulse delay-200"></span>`;
    container.appendChild(typingElem);
    container.scrollTop = container.scrollHeight;

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ trip_id: tripId, message: msg })
        });
        const data = await res.json();

        typingElem.remove();

        const botMsgElem = document.createElement("div");
        botMsgElem.className = "bg-sky-50 text-slate-800 p-3.5 rounded-2xl rounded-tl-none border border-sky-100 leading-relaxed";
        
        // Render simple markdown formatted response
        let replyHtml = data.reply
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\*(.*?)\*/g, "<em>$1</em>")
            .replace(/\n\n/g, "<br><br>")
            .replace(/\n- /g, "<br>• ");

        botMsgElem.innerHTML = replyHtml;
        container.appendChild(botMsgElem);
        container.scrollTop = container.scrollHeight;

    } catch (err) {
        typingElem.remove();
        showToast("Failed to reach AI Concierge", "error");
    }
}

// Confirm trip deletion
async function confirmDeleteTrip(tripId) {
    if (!confirm("Are you sure you want to delete this itinerary?")) return;

    try {
        const res = await fetch(`/api/trips/${tripId}`, { method: "DELETE" });
        if (res.ok) {
            window.location.href = "/";
        } else {
            showToast("Failed to delete trip", "error");
        }
    } catch (e) {
        showToast("Network error deleting trip", "error");
    }
}

// Toast notification display
function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    const bgClass = type === "error" ? "bg-red-600 text-white" : "bg-slate-900 text-white";
    toast.className = `${bgClass} px-4 py-2.5 rounded-xl shadow-lg text-xs font-semibold flex items-center gap-2 pointer-events-auto transform transition-all duration-300 translate-y-2 opacity-0`;
    toast.innerHTML = `<span>${message}</span>`;

    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.remove("translate-y-2", "opacity-0");
    }, 10);

    setTimeout(() => {
        toast.classList.add("translate-y-2", "opacity-0");
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

