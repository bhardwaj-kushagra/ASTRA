# Risk Analytics & Visualization Service

Delivers dashboards and basic analytics for national security analysts, aggregating detection signals.

## Responsibilities (MVP)
- Simple web UI displaying recent detections, scores, and trends.
- REST API for querying detection history and metrics.
- Pluggable visualization components (charts, tables).

## Tech Stack
- Python 3.10+, FastAPI (backend)
- HTML/CSS/JS with Chart.js or Plotly.js (frontend)
- SQLite or in-memory store for MVP data persistence

## Future Enhancements
- Interactive heatmaps, temporal trend analysis, and predictive risk scoring.
- Integration with graph intelligence and attribution services.
- Advanced dashboards using React + D3.
- Scenario simulation, alert triage, and reporting exports.

## Next Steps
1. Define UX wireframes and data contracts.
2. Implement backend API for detection aggregation.
3. Build simple HTML dashboard consuming the API.
