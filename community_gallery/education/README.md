# Preswald Project

# Student Performance Dashboard

## Dataset Source

This project uses the **Students Performance in Exams** dataset, which is available on **[Kaggle](https://www.kaggle.com/datasets/spscientist/students-performance-in-exams)**.

- The dataset contains information about students' scores in Math, Reading, and Writing.
- Additional attributes include **gender, parental education level, and test preparation course status**.
- The data is used to analyze and visualize **patterns in student performance**.

---

## What Does This App Do?

This **interactive dashboard** allows users to **explore student performance** through **filters, visualizations, and tables**. The app helps answer key questions such as:

**Does test preparation improve scores?**
**Does parental education influence student performance?**
**Do male and female students perform differently?**
**How do subject scores compare?**

### **Features**

- **Interactive Filters:** Filter students by **gender, parental education level, and test preparation course.**
- **Math Score Slider:** Adjust the **minimum math score** to dynamically filter students.
- **Charts for Analysis:**
  - **Bar Chart** → Shows average scores in Math, Reading, and Writing.
  - **Grouped Bar Chart** → Compares gender-based performance.
  - **Box Plots** → Show the impact of **Parental Education** and **Test Preparation** on Math scores.
- **Tabular Data:** Displays **Math, Reading, and Writing scores grouped by Test Preparation Course.**
- **Automatic Formatting:**
  - **Parental Education & Test Preparation** values are converted to **Camel Case** for better readability.

---

## How to Run the App Locally

### **Ensure Preswald is Installed**

If you haven't installed **Preswald**, run:

```bash
pip install preswald
```

### **Run the App**

```bash
preswald run
```

This will launch the **interactive dashboard** in your web browser.

---

## Deploying the App

```bash
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```

Deployed URL: https://education-426954-emwy6scp-ndjz2ws6la-ue.a.run.app/

---

**Future Enhancements:**

- Add more **insights and predictive analytics** for student performance.
- Enhance **UI design for better user experience**.
- Allow **data export** for offline analysis.
