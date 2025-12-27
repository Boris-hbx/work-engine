# Boris Life

A personal life management PWA built with Flask. Organize tasks with the Eisenhower Matrix, maintain motivation, and visualize data with bubble charts.

## Features

- **Todo (Eisenhower Matrix)**: Organize tasks by importance and urgency across three time horizons (Today, This Week, Next 30 Days)
- **Motivation**: Personal motivation text organized by categories
- **Bubble Chart Tool**: Create and save bubble chart visualizations
- **PWA Support**: Install on mobile devices, works offline
- **Local-First**: All data stored in JSON/text files

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python app.py
   ```

3. **Open in Browser**
   Navigate to `http://localhost:3000`

## Project Structure

```
boris-life/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── data/                  # User data storage
│   ├── todos.json         # Task data
│   ├── motivation.txt     # Motivation content
│   ├── quotes.txt         # Random quotes
│   ├── bubbles.json       # Bubble chart data
│   └── config.json        # App configuration
├── static/
│   ├── style.css          # Styles
│   ├── manifest.json      # PWA manifest
│   ├── sw.js              # Service worker
│   └── icons/             # App icons
└── templates/
    ├── base.html          # Base template
    ├── todo.html          # Todo page
    ├── motivation.html    # Motivation page
    └── bubble.html        # Bubble chart page
```

## Mobile Usage

1. Open `http://localhost:3000` on your phone (same network)
2. Add to home screen via browser menu
3. Use as a standalone app

## Philosophy

This tool is designed for clarity and simplicity:
- Reduce cognitive noise
- Keep important information visible
- Focus on thinking rather than task management mechanics
