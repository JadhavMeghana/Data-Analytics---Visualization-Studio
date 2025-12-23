# 🌐 Web Application Frontend Guide

## 🚀 Access the Web Interface

The Flask web application is now running! Access it at:

**👉 http://localhost:5000**

## 📱 Features Available

### 1. **Dashboard** (`/`)
- Overview of all analytics
- Statistics cards showing:
  - Number of charts generated
  - Interactive dashboards available
  - Reports count
  - Insights count
- Latest report preview
- Recent KPI results table
- Quick action buttons

### 2. **Interactive Dashboard** (`/dashboard`)
- Full-screen interactive Plotly dashboard
- Revenue by region visualization
- Monthly revenue trends
- Zoomable and interactive charts

### 3. **Charts Gallery** (`/charts`)
- Browse all generated charts
- View PNG images
- Access interactive HTML dashboards
- See chart metadata (size, modification date)

### 4. **Reports** (`/reports`)
- View all text reports
- Browse CSV summaries
- Read automated insights
- Download reports

### 5. **Upload** (`/upload`)
- Upload CSV files for processing
- File format validation
- Upload status feedback

## 🎨 UI Features

- **Modern Design**: Gradient backgrounds, card-based layout
- **Responsive**: Works on desktop, tablet, and mobile
- **Interactive**: Hover effects, smooth transitions
- **Color-Coded**: Different colors for different sections
- **Icons**: Font Awesome icons throughout

## 🔧 How to Use

### Starting the Web App

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the web application
python python/web_app.py
```

The app will start on **http://localhost:5000**

### Running Demo Mode from Web UI

1. Go to Dashboard (`/`)
2. Click "Run Demo Mode" button
3. Wait for execution (about 30 seconds)
4. Page will auto-refresh with new data

### Viewing Charts

1. Navigate to Charts (`/charts`)
2. Click on any chart to view full size
3. Interactive dashboards open in new tab

### Uploading Data

1. Go to Upload (`/upload`)
2. Select a CSV file
3. Click Upload
4. File will be saved to `data/input/` directory

## 📊 Pages Overview

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/` | Main overview with stats and KPIs |
| Interactive Dashboard | `/dashboard` | Full-screen Plotly dashboard |
| Charts | `/charts` | Gallery of all charts |
| Reports | `/reports` | All reports and insights |
| Upload | `/upload` | CSV file upload interface |

## 🎯 Quick Start

1. **Open your browser** and go to: `http://localhost:5000`
2. **View the dashboard** - See overview of all analytics
3. **Click "Run Demo Mode"** - Generate sample data and reports
4. **Explore charts** - Navigate to Charts section
5. **View reports** - Check Reports section for detailed analysis

## 🔐 Security Note

The web application is running in **debug mode** for development.
For production, disable debug mode and use proper authentication.

## 🛠️ Troubleshooting

### Port Already in Use
If port 5000 is busy, modify `web_app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change port
```

### Charts Not Showing
- Run demo mode first: Click "Run Demo Mode" button
- Check `reports/charts/` directory has files
- Refresh the page

### Upload Not Working
- Ensure CSV file format is correct
- Check file size (max 16MB)
- Verify file has required columns

## ✨ Enjoy Your Analytics Platform!

The web interface provides a complete frontend for your Enterprise Sales Analytics system!

