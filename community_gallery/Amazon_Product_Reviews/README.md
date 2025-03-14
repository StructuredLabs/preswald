# Amazon Product Reviews Analytics Dashboard

**Dataset Used:** Amazon Product Reviews <br>
**Source:** https://www.kaggle.com/datasets/arhamrumi/amazon-product-reviews?resource=download

## What This App Does

The Amazon Product Reviews Analytics Dashboard transforms raw customer review data into actionable business insights through interactive visualizations. This application helps businesses understand customer sentiment, product performance, and review patterns to make data-driven decisions.

### Key Features

#### 📊 Comprehensive Analytics
- **Sentiment Analysis**: Automatically categorizes reviews as Positive, Neutral, or Negative
- **Rating Distribution**: Visualizes star ratings with counts and percentages
- **Trend Analysis**: Tracks review volume and sentiment changes over time
- **Product Performance Matrix**: Identifies star products vs. those needing improvement

#### 📈 Interactive Visualizations
- **Key Metrics Gauges**: Average rating, positive review percentage, negative review percentage
- **Sentiment Distribution**: Pie chart showing the breakdown of customer sentiment
- **Review Length Analysis**: Box plots showing how review length varies by rating
- **Helpfulness Analysis**: Charts revealing what makes reviews helpful to other customers
- **Time Trend Charts**: Review volume and average ratings over time with trend lines
- **Day-of-Week Patterns**: Identifies when reviews are submitted and sentiment variations

#### 🔍 Filtering Capabilities
- Filter by minimum star rating (1-5)
- Filter by sentiment category (Positive, Neutral, Negative)
- Focus on specific time periods or products

#### 💡 Automated Insights
- Plain-language interpretations of data patterns
- Correlation analysis between ratings, helpfulness, and review length
- Trend detection (improving or declining metrics)
- Product performance classification and recommendations

### Business Value

- **Early Problem Detection**: Identify declining review trends before they impact sales
- **Product Development Guidance**: Understand what customers value in your products
- **Marketing Optimization**: Highlight top-performing products and features
- **Customer Experience Improvement**: Address common complaints and enhance satisfaction

### Data Requirements

The dashboard works with Amazon product review data containing:
- Product identifiers
- Star ratings (1-5)
- Review text
- Submission timestamps
- Helpfulness votes
- Review summaries

### Dashboard Sections

1. **Key Metrics**: Overall performance indicators with interactive gauges
2. **Sentiment Analysis**: Distribution of positive, neutral, and negative reviews
3. **Rating Distribution**: Detailed breakdown of star ratings
4. **Review Length Analysis**: How review content varies by rating
5. **Helpfulness Analysis**: What makes reviews valuable to other customers
6. **Time Trend Analysis**: How reviews and sentiment change over time
7. **Product Performance**: Comparative analysis of products in your catalog

### Insights Generated

- Correlation between review characteristics and helpfulness
- Day-of-week patterns in review submission
- Relationship between review length and sentiment
- Product quadrant analysis (high/low quality vs. popularity)
- Trend direction with statistical validation
- Comparative product performance metrics


## To run and deploy this:
1. ```pip install preswald```
2. Clone this repository
3. (Optional) Use Virtual Environment (Recommended)
```
python -m venv myvenv
cd myvenv/Scripts
activate
```
4. Execute ```preswald run``` in cloned repo

---

Built with Preswald and Plotly for interactive data visualization and analysis.
