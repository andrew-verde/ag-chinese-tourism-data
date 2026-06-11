# Fukui Tourism Location Trend Report

An interactive web application that visualizes tourism activity trends for Fukui Prefecture, Japan by aggregating and analyzing impression counts from online maps and web search tools.

**[View the Application](https://code4fukui.github.io/fukui-kanko-trend-report/)**

## Overview

This application aggregates impression data from online maps and web search tools for tourist locations across Fukui Prefecture and visualizes trends through interactive charts. It helps stakeholders understand tourism patterns and popularity of different regions within Fukui.

## Key Features

- **Area-Level & Prefectural Aggregation**: View data for individual regions or all of Fukui Prefecture combined
- **Time Series Analysis**: Analyze data at daily, weekly, or monthly granularity
- **Dual-Period Comparison**: Compare trends across two different time periods side-by-side
- **Comprehensive Metrics**: 
  - Map impressions and searches
  - Web search impressions
  - Route search impressions
  - Call button clicks
  - Website clicks
  - Review submissions
  - Review count by star rating (1-5 stars)
  - Average rating
- **Data Export**: Download visualized data in CSV format

## Supported Regions

The application collects data for 13 cities within Fukui Prefecture:

- Awara City (あわら市)
- Ikeda Town (池田町)
- Ōi Town (おおい町)
- Eihei-ji Town (永平寺町)
- Echizen City (越前市)
- Katsuyama City (勝山市)
- Minamiechizen Town (南越前町)
- Takahama Town (高浜町)
- Tsuruga City (敦賀市)
- Wakasa Town (若狭町)
- Obama City (小浜市)
- Mihama Town (美浜町)
- Ōno City (大野市)

## Usage Guide

1. **Select Area**: Choose between viewing data for the entire Fukui Prefecture ("All Areas") or a specific region
2. **Select Time Unit**: Choose the time granularity - daily, weekly, or monthly aggregation
3. **Select Date Range**: Use the calendar picker to choose the analysis period
4. **Enable Comparison** (Optional): Check the comparison checkbox to enable a second date range for side-by-side comparison
5. **View Analysis**: Examine two chart views:
   - **Impression Trends**: Shows impression and interaction counts over time
   - **Review Trends**: Shows review submission and rating data over time
6. **Export Data** (Optional): Download the displayed data as a CSV file for further analysis

## Data Format

### CSV Column Structure

Exported CSV files contain the following columns:

| Column Name | Description |
| --- | --- |
| `Date` | Date in YYYY-MM-DD format |
| `Map Searches` | Number of map searches |
| `Web Searches` | Number of web searches |
| `Route Searches` | Number of route searches |
| `Calls` | Number of call button clicks |
| `Website Clicks` | Number of website clicks |
| `Reviews Submitted` | Number of reviews submitted |
| `5-Star Reviews` | Count of 5-star reviews |
| `4-Star Reviews` | Count of 4-star reviews |
| `3-Star Reviews` | Count of 3-star reviews |
| `2-Star Reviews` | Count of 2-star reviews |
| `1-Star Reviews` | Count of 1-star reviews |
| `Average Rating` | Average rating score |

## Technology Stack

- **Frontend Framework**: React 19 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with shadcn/ui components
- **Charts**: Recharts for data visualization
- **State Management**: React Context API
- **Data Processing**: PapaParse (CSV), Tidy.js (data transformation)
- **Date Utilities**: date-fns, dayjs, react-day-picker
- **Package Manager**: pnpm

## Development

### Quick Setup

Copy and paste these commands to set up and run the development server:

```bash
# Clone the repository
git clone https://github.com/code4fukui/fukui-kanko-trend-report.git
cd fukui-kanko-trend-report

# Ensure Node.js 20.19+ or 22.12+ is installed
# (If you use nvm, pick one of the following)
# nvm install 22.12.0
# nvm use 22.12.0
# --- or ---
# nvm install 20.19.0
# nvm use 20.19.0
# node -v

# Enable Corepack and use the pnpm version specified in package.json
corepack enable
corepack use pnpm@10.11.0

# Initialize submodules and install dependencies
git submodule update --init --recursive
pnpm install

# Start the development server
pnpm dev
```

After the development server starts, open the URL shown in your terminal (typically `http://localhost:5173`) in your browser.

### Updating Submodules (for Latest Data)

To fetch the latest data from the submodule:

```bash
git submodule update --remote --recursive
```

### Build for Production

```bash
pnpm build
```

The build artifacts will be generated in the `dist/` directory.

### Preview Production Build

```bash
pnpm preview
```

### Lint Code

```bash
pnpm lint
```

## Project Structure

```
fukui-kanko-trend-report/
├── public/
│   └── data/                        # CSV data files (git submodule)
├── index.html                       # HTML entry point
├── src/
│   ├── components/
│   │   ├── parts/                   # Application-specific components
│   │   │   ├── date-range-picker/   # Date range selection component
│   │   │   │   ├── index.tsx
│   │   │   │   ├── utils.ts
│   │   │   │   └── hooks/
│   │   │   │       └── useInitialRangeAdjustment.ts
│   │   │   │   └── range-picker/    # Individual range picker variants
│   │   │   │       ├── day-range-picker.tsx
│   │   │   │       ├── month-picker.component.tsx
│   │   │   │       ├── month-range-picker.tsx
│   │   │   │       └── week-range-picker.tsx
│   │   │   ├── graph/               # Chart display components
│   │   │   │   ├── index.tsx
│   │   │   │   ├── types.ts
│   │   │   │   ├── utils.ts
│   │   │   │   ├── constants.ts
│   │   │   │   ├── charts/
│   │   │   │   │   ├── chart-elements.tsx
│   │   │   │   │   ├── count-trend-chart.tsx
│   │   │   │   │   └── review-trend-chart.tsx
│   │   │   │   └── hooks/
│   │   │   │       ├── use-chart-data.ts
│   │   │   │       └── use-metrics-data.ts
│   │   │   ├── selector/            # Area and time unit selectors
│   │   │   │   ├── area-selector.tsx
│   │   │   │   ├── time-unit-selector.tsx
│   │   │   │   └── hooks/
│   │   │   │       └── use-areas.ts
│   │   │   ├── download-csv-button.tsx
│   │   │   ├── external-navigation.tsx
│   │   │   └── header.tsx
│   │   └── ui/                      # Reusable UI components (shadcn/ui)
│   │       ├── button.tsx
│   │       ├── calendar.tsx
│   │       ├── checkbox.tsx
│   │       ├── popover.tsx
│   │       └── select.tsx
│   ├── context/
│   │   └── ChartSettingsContext.tsx  # Global state management for chart settings
│   ├── lib/
│   │   └── utils.ts                 # Utility functions
│   ├── types/
│   │   └── types.ts                 # TypeScript type definitions
│   ├── utils/
│   │   └── csv-export.ts            # CSV export functionality
│   ├── App.tsx                      # Main application component
│   ├── main.tsx                     # Application entry point
│   └── index.css                    # Global styles
├── tools/
│   ├── upload.sh                    # Deployment script
│   └── utils.sh                     # Utility functions for scripts
├── .github/
│   ├── copilot-instructions.md      # Copilot instructions for developers
│   ├── pull_request_template.md     # Pull request template
│   └── workflows/
│       ├── pages.yml                # GitHub Pages deployment workflow
│       └── submodule.yml            # Automatic data update workflow
├── components.json                  # shadcn/ui configuration
├── tsconfig.json                    # TypeScript configuration
├── vite.config.ts                   # Vite configuration
├── eslint.config.js                 # ESLint configuration
└── package.json                     # Project dependencies and scripts
```

## Configuration

### Component Library

This project uses [shadcn/ui](https://ui.shadcn.com/) for reusable UI components. Configuration can be found in `components.json`.

### TypeScript

The project is configured with strict TypeScript settings. See `tsconfig.json` for compiler options.

### Styling

Styled with Tailwind CSS v4. See `index.css` for global styles and component overrides.

## Deployment

The application is automatically deployed to GitHub Pages when changes are pushed to the main branch. See `.github/workflows/pages.yml` for deployment configuration.

### Data Updates

Data is automatically updated via GitHub Actions. The submodule containing CSV data is updated according to the schedule defined in `.github/workflows/submodule.yml`.

## Scripts

| Command | Description |
| --- | --- |
| `pnpm dev` | Start the development server |
| `pnpm build` | Build for production |
| `pnpm preview` | Preview the production build |
| `pnpm lint` | Run ESLint on the codebase |
| `pnpm upload` | Deploy to AWS S3/CloudFront (requires stage name and AWS credentials) |

## Contributing

Contributions are welcome! Please follow these guidelines when contributing:

- Read the [pull request template](.github/pull_request_template.md) before submitting a PR
- Follow the existing code style and conventions
- Ensure all tests pass and the code lints without errors
- Write clear commit messages and PR descriptions

## Troubleshooting

### Port Already in Use

If port 5173 is already in use, Vite will automatically try the next available port. You'll see the correct URL in the terminal output.

### Node.js Version Too Old

Vite requires Node.js 20.19+ or 22.12+. If you see a version error, upgrade Node.js and try again. Example with nvm:

```bash
nvm install 22.12.0
nvm use 22.12.0
node -v
```

### Data Not Appearing

Ensure that submodules have been properly initialized:

```bash
git submodule update --init --recursive
```

### Build Errors

If you encounter build errors, try:

1. Clear the cache: `rm -rf node_modules pnpm-lock.yaml`
2. Reinstall dependencies: `pnpm install`
3. Rebuild: `pnpm build`

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## About

This project is maintained by [Code for FUKUI](https://github.com/code4fukui), a civic tech organization dedicated to supporting local communities through open-source technology and civic innovation.

---

**Last Updated**: February 2026  
**Version**: 0.0.0
