# **YouTube Global Statistics Analytics**

## **Overview**
This project is a **Preswald-powered interactive web application** that analyzes YouTube video trends across **categories, countries, and creators** using **Global YouTube Statistics 2023** dataset.

The application includes **six interactive visualizations** and **a slider-based filter** for dynamic exploration.

## **Author & Dataset**
- **Author:** Sweta Pati  
- **Email:** spati@gmu.edu  
- **University:** George Mason University  
- **Dataset:** [Global YouTube Statistics 2023](https://www.kaggle.com/datasets/nelgiriyewithana/global-youtube-statistics-2023?resource=download)  
- **Dataset Source:** Kaggle  
- **Live Deployed Preview Link:** [Preview](https://my-example-project-514006-3h0rzgww-ndjz2ws6la-ue.a.run.app) 
- **Demo Video Link:** [Video](https://drive.google.com/file/d/1dIltYoPJXD8v64u2FJ1dohb0a2Vnw4o0/view?usp=sharing) 

---

## **Features**
### **Global Filter - Slider for Views Threshold**
Before displaying the visualizations, the application features a **slider-based filter** that allows users to adjust the **minimum number of video views (in billions)** required for a category, creator, or country to appear in the plots. This enhances interactivity by dynamically filtering the dataset.

```python
views_threshold = slider("Minimum Views (Converted to Billion)", min_val=0, max_val=max_views, default=0.5)
```

Once a threshold is selected, **six different visualizations** are displayed.

---

## **Visualizations**
### **1. Views by Category (Bar Chart)**
**Graph Type:** Bar Chart (Categorical Comparison)  
- This **bar chart** illustrates the total YouTube video views for different **content categories**.
- Users can quickly identify which categories generate the highest audience engagement.

**Key Insights:**
- **Most popular category**: `top_category` with `top_category_views` views.
- **Least popular categories**: `lowest_category_list`, indicating niche audiences.

---

### **2. Top YouTubers by Views (Bar Chart)**
**Graph Type:** Bar Chart (Ranked List)  
- This visualization ranks **top YouTubers** based on their **total video views (in billions)**.

**Key Insights:**
- **Most-watched YouTuber**: `top_youtuber` with `top_youtuber_views` views.
- Entertainment, Music, and Gaming dominate, while niche creators attract smaller but loyal followings.

---

### **3. YouTube Views by Country (Choropleth Map)**
**Graph Type:** **Choropleth Map** (Geographical Data Representation)  
- This **world map** visually represents YouTube views by country, highlighting regions with the most active audience.

**Key Insights:**
- **Country with highest YouTube engagement**: `top_country_name` with `top_country_views` views.
- **Lowest engagement regions**: `lowest_country_list` - potentially due to internet penetration or population size.

---

### **4. Category Trends Across Countries (Heatmap)**
**Graph Type:** **Heatmap** (Regional Comparison)  
- This **heatmap** shows how different **YouTube categories** perform **across various countries**, revealing content preferences.

**Key Insights:**
- `top_country_name` has the **highest YouTube views**, with `top_category_name` leading in this country.
- **Least-watched categories globally**: `lowest_category_list` indicate niche engagement.

---

### **5. Trending YouTubers (Last 30 Days) (Line Chart)**
**Graph Type:** **Line Chart** (Time Series Analysis)  
- This **line chart** tracks **trending YouTubers over the past 30 days**, showing their recent rise and fall in engagement.

**Key Insights:**
- **Most trending YouTuber**: `top_trending_name` with `top_trending_views` views in the last month.
- `youtuber_with_drop` had the **largest drop in views**, suggesting declining engagement.

---

### **6. Subscribers vs Uploads Growth (Multi-Line Chart)**
**Graph Type:** **Multi-Line Chart** (Trend Comparison)  
- This **multi-line plot** explores the relationship between **video uploads and subscriber growth**, using a **moving average** to smooth fluctuations.

**Key Insights:**
- **Category with the highest subscriber growth**: `top_growth_category` reaching **top_growth_value** subscribers.
- **Category with the least subscriber growth**: `lowest_growth_category` with **lowest_growth_value** subscribers.
- **Not all categories grow equally** – quality content matters more than quantity in some cases.

---

## **How to Run the Application**
### **1. Install Preswald**
Ensure you have **Preswald** installed. If not, install it using:

```bash
pip install preswald
```

### **2. Set Up Your Project**
Initialize your **Preswald project** and navigate to it:

```bash
preswald init my_example_project
cd my_example_project
```

### **3. Download the Dataset**
Place your dataset in the **data/** folder inside your project, after downloading the data through the Kaggle link provided above.

### **4. Run the Application Locally**
Execute the following command in your project directory:

```bash
preswald run
```

### **5. Deploy to Structured Cloud**
Once you're happy with your app, **deploy it online**:

1. Get an API key from [Preswald Structured Cloud](https://app.preswald.com)
2. Run the deployment command:

```bash
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```

Replace `<your-github-username>` and `<structured-api-key>` with your credentials.

3. Open the **live preview link** provided after deployment.

This interactive app provides **valuable insights** into **global YouTube trends**. It enables **creators, analysts, and marketers** to explore data dynamically through **interactive filters and charts**.