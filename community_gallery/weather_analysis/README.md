# Coding Assessment - Preswald

This repository contains my submission for the **Preswald Coding Assessment**.  
The project is built using **Python** and **Preswald**, designed to process and analyze weather data efficiently.

---

## 🚀 Live Demo  
[Weather Analysis App](https://weather-analysis-986689-vdccxm1p.preswald.app)

## 📌 Project Overview

The task involved implementing a script (`hello.py`) that:
- Loads a dataset (`seattleWeather_csv`).
- Processes and filters the data based on user-selected conditions.
- Displays interactive **charts and tables** through a web interface using **Preswald**.

---

## ⚙️ Setup Instructions

### Prerequisites
Ensure you have the following installed:
- **Python 3.8+**
- **Preswald CLI**
- **Virtual Environment (Recommended)**

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/shadyx6/weather-analysis.git
   cd weather-analysis
Create and activate a virtual environment:

```
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
Install dependencies:
```
```
pip install -r requirements.txt
▶️ Running the Project
To execute the script locally, run:
```

```
preswald run
This will start the server on http://localhost:8501.
```

🚀 Deployment
To deploy the project to Structured, use:

```
preswald deploy --target structured --github shadyx6 --api-key YOUR_API_KEY hello.py
(Replace YOUR_API_KEY with the actual API key.)
 ```
📝 Notes
The project processes data from seattleWeather_csv.
Any warnings related to SettingWithCopyWarning in pandas are expected but do not impact functionality.
Ensure that all required config files (preswald.toml, secrets.toml) are present in the working directory.

📩 Contact
If you have any questions, feel free to reach out!
