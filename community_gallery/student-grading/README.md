# Student Grades Analysis Application

An interactive data analysis application built with Preswald for analyzing student performance metrics and identifying patterns in academic achievement.

## 📊 Features

- **Interactive Data Filtering**
  - Dynamic attendance threshold filtering
  - Participation score pre-filtering
  - Real-time updates to visualizations

- **Data Visualizations**
  - Scatter plot of Final Scores vs Study Hours
  - Color-coded grade distribution
  - Interactive data tables

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- Preswald framework
- Required Python packages (install via pip):
  ```bash
  pip install preswald plotly
  ```

### Configuration

The application uses `preswald.toml` for configuration:
- Port: 8501
- Data source: CSV file (`data/Students_Grading_Dataset.csv`)
- Custom branding and styling options

### Running the Application

```bash
preswald run
```

The application will be available at `http://localhost:8501`

## 📈 Data Analysis Features

### 1. Attendance Analysis
- Filter students based on attendance percentage
- Visualize the relationship between attendance and performance

### 2. Study Patterns
- Explore correlation between study hours and final scores
- Analyze grade distribution across different study patterns

### 3. Performance Metrics
- View detailed student performance data
- Filter by participation scores
- Track multiple assessment components

## 🎨 User Interface

The application provides an intuitive interface with:
- Clean, modern design
- Interactive controls
- Responsive visualizations
- Easy-to-read data tables

## 📁 Project Structure

```
student-grading/
├── hello.py              # Main application code
├── preswald.toml        # Configuration file
├── data/
│   └── Students_Grading_Dataset.csv  # Student data
└── images/
    ├── favicon.ico      # Application favicon
    └── logo.png         # Application logo
```

## 🤝 Contributing

Feel free to fork this project and submit pull requests for any improvements or additional features.

## 📝 Dataset Columns

The analysis uses the following key metrics:
- Attendance (%)
- Study Hours per Week
- Final Score
- Participation Score
- Grade
- And more...
