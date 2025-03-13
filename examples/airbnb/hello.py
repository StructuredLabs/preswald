from preswald import connect, get_df, query, text, table, plotly, selectbox, slider, checkbox, button
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

px.defaults.template = "plotly_white"
COLORS = px.colors.qualitative.Bold

connect()

try:
    df = get_df("airbnb")
    original_df = df.copy()
    
    if 'last_review' in df.columns:
        df['last_review'] = pd.to_datetime(df['last_review'], errors='coerce')
        df['days_since_review'] = (datetime.now() - df['last_review']).dt.days.fillna(999)
    
    df['price_category'] = pd.cut(
        df['price'], 
        bins=[0, 100, 200, 300, 500, 1000, float('inf')],
        labels=['Budget (<$100)', 'Economy ($100-$200)', 'Mid-range ($200-$300)', 
                'Upscale ($300-$500)', 'Luxury ($500-$1000)', 'Ultra-luxury ($1000+)']
    )
    
except Exception as e:
    text(f"# ⚠️ Error loading dataset: {str(e)}")
    text("Please ensure your data file is correctly set up in preswald.toml")
    df = pd.DataFrame({
        'neighbourhood': ['Error'],
        'room_type': ['Error'],
        'price': [0],
        'minimum_nights': [0]
    })
    original_df = df.copy()

text("# 🏡 San Francisco Airbnb Market Intelligence Dashboard")
text("This interactive dashboard provides comprehensive insights into San Francisco's Airbnb market, helping you understand pricing trends, neighborhood dynamics, and host behaviors.")

text("## Dataset Overview")
if 'neighbourhood' in df.columns and 'host_id' in df.columns:
    total_listings = len(df)
    unique_neighborhoods = df['neighbourhood'].nunique() 
    unique_hosts = df['host_id'].nunique()
    avg_price = df['price'].mean()
    
    text(f"**Total Listings:** {total_listings:,}  |  **Neighborhoods:** {unique_neighborhoods}  |  " + 
         f"**Unique Hosts:** {unique_hosts:,}  |  **Average Price:** ${avg_price:.2f}")

current_tab = selectbox(
    "Dashboard View", 
    options=[
        "📊 Market Overview", 
        "🗺️ Neighborhood Analysis", 
        "💰 Price Insights", 
        "👥 Host Analysis",
        "⭐ Reviews & Ratings"
    ],
    default="📊 Market Overview",
    
)

text("## 🔍 Filters")

# Get unique neighborhoods and group them into regions to reduce dropdown size
neighborhoods = sorted(df['neighbourhood'].unique().tolist())
all_neighborhoods_option = "All Neighborhoods"

# Option 1: Limit to top neighborhoods by count + All Neighborhoods option
# This keeps the dropdown manageable while still offering the most common choices
neighborhood_counts = df['neighbourhood'].value_counts()
top_neighborhoods = neighborhood_counts.nlargest(15).index.tolist()  # Adjust number as needed
neighborhood_options = [all_neighborhoods_option] + sorted(top_neighborhoods)

# Add an "Other" option that will be handled in the filtering logic
if len(neighborhoods) > len(top_neighborhoods):
    neighborhood_options.append("Other Neighborhoods")

selected_neighborhood = selectbox(
    "Neighborhood", 
    options=neighborhood_options,
    default=all_neighborhoods_option
)

room_types = sorted(df['room_type'].unique().tolist())
all_room_types_option = "All Property Types"
room_type_options = [all_room_types_option] + room_types
selected_room_type = selectbox(
    "Property Type", 
    options=room_type_options,
    default=all_room_types_option
)

# We've removed the price filter slider, but we need to define price_range so the filter button works correctly
price_min, price_max = int(df['price'].min()), int(df['price'].max())
price_range = [price_min, price_max]

if button("Apply Filters"):
    filtered_df = original_df.copy()
    
    if selected_neighborhood == "Other Neighborhoods":
        # If "Other Neighborhoods" is selected, filter to neighborhoods not in top_neighborhoods
        filtered_df = filtered_df[~filtered_df['neighbourhood'].isin(top_neighborhoods)]
    elif selected_neighborhood != all_neighborhoods_option:
        filtered_df = filtered_df[filtered_df['neighbourhood'] == selected_neighborhood]
    
    if selected_room_type != all_room_types_option:
        filtered_df = filtered_df[filtered_df['room_type'] == selected_room_type]
    
    # We still need to apply the price filter, but now it uses the full range
    filtered_df = filtered_df[
        (filtered_df['price'] >= price_range[0]) &
        (filtered_df['price'] <= price_range[1])
    ]
    
    df = filtered_df
    
    filtered_count = len(df)
    total_count = len(original_df)
    
    if filtered_count > 0:
        text(f"**Showing {filtered_count:,} of {total_count:,} listings ({filtered_count/total_count:.1%})**")
    else:
        text(f"**No listings match your filters. Please try different criteria.**")
        df = original_df
else:
    filtered_count = len(df)
    total_count = len(original_df)
    text(f"**Showing all {filtered_count:,} listings**")

if current_tab == "📊 Market Overview":
    text("## 📊 Market Overview")
    
    text("### Key Market Indicators")
    
    if 'price' in df.columns and len(df) > 0:
        avg_price = df['price'].mean()
        median_price = df['price'].median()
        text(f"**Average Price:** ${avg_price:.2f}  |  **Median Price:** ${median_price:.2f}")
    
    if 'minimum_nights' in df.columns and 'availability_365' in df.columns and len(df) > 0:
        avg_nights = df['minimum_nights'].mean()
        avg_availability = df['availability_365'].mean()
        text(f"**Avg. Minimum Nights:** {avg_nights:.1f}  |  **Avg. Days Available/Year:** {avg_availability:.0f}")
    
    text(f"**Total Listings:** {len(df):,}")
    
    if 'room_type' in df.columns and len(df) > 0:
        text("### Property Type Distribution")
        
        room_type_counts = df['room_type'].value_counts().reset_index()
        room_type_counts.columns = ['Room Type', 'Count']
        room_type_fig = px.pie(
            room_type_counts, 
            values='Count', 
            names='Room Type',
            color='Room Type',
            color_discrete_sequence=COLORS,
            hole=0.4
        )
        
        room_type_fig.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            margin=dict(t=60, b=40, l=20, r=20),
            height=400
        )
        room_type_fig.update_traces(textinfo='percent+label')
        
        plotly(room_type_fig)
        
        if not room_type_counts.empty:
            most_common = room_type_counts.iloc[0]['Room Type']
            percentage = (room_type_counts.iloc[0]['Count'] / room_type_counts['Count'].sum() * 100)
            text(f"**Insight**: {most_common} properties dominate the San Francisco market at {percentage:.1f}% of listings, indicating strong demand for this property type.")
    
    if 'price' in df.columns and len(df) > 0:
        text("### Price Distribution")
        
        price_hist = px.histogram(
            df[df['price'] <= 500],
            x="price",
            nbins=30,
            opacity=0.7,
            marginal="box",
            labels={"price": "Nightly Price ($)"}
        )
        
        price_hist.add_vline(x=df['price'].median(), line_dash="dash", line_color="red", 
                            annotation_text=f"Median: ${df['price'].median():.0f}", 
                            annotation_position="top right")
        
        price_hist.update_layout(
            title="Price Distribution (limited to $500 for visibility)",
            xaxis_title="Price ($)",
            yaxis_title="Number of Listings",
            bargap=0.1,
            height=500
        )
        
        plotly(price_hist)
        
        q25 = df['price'].quantile(0.25)
        q75 = df['price'].quantile(0.75)
        text(f"**Insight**: The price distribution shows a positive skew, with most listings in the ${q25:.0f}-${q75:.0f} range, suggesting a competitive mid-market segment.")
    
    if 'neighbourhood' in df.columns and len(df) > 0:
        text("### Top Neighborhoods by Listing Count")
        
        neighborhood_counts = df['neighbourhood'].value_counts().reset_index()
        
        if not neighborhood_counts.empty:
            neighborhood_counts.columns = ['Neighborhood', 'Count']
            
            top_n = min(10, len(neighborhood_counts))
            top_neighborhoods = neighborhood_counts.head(top_n)
            
            neighborhood_fig = px.bar(
                top_neighborhoods, 
                x='Count', 
                y='Neighborhood',
                orientation='h',
                text='Count'
            )
            
            neighborhood_fig.update_layout(
                yaxis={'categoryorder':'total ascending'},
                xaxis_title="Number of Listings",
                margin=dict(l=200),
                height=500
            )
            
            neighborhood_fig.update_traces(textposition='outside')
            
            plotly(neighborhood_fig)
            
            if not top_neighborhoods.empty:
                most_popular = top_neighborhoods.iloc[-1 if len(top_neighborhoods) > 0 else 0]['Neighborhood']
                text(f"**Insight**: {most_popular} has the highest concentration of Airbnb listings, suggesting it's a popular area for tourists or business travelers.")
        else:
            text("**Note**: Not enough neighborhood data available to show distribution.")

elif current_tab == "🗺️ Neighborhood Analysis":
    text("## 🗺️ Neighborhood Analysis")
    
    if len(df) < 5 or df['neighbourhood'].nunique() < 2:
        text("**Not enough data**: Please adjust your filters to include more neighborhoods and listings.")
    else:
        if 'neighbourhood' in df.columns and 'price' in df.columns:
            text("### Average Price by Neighborhood")
            
            neighborhood_price = df.groupby('neighbourhood').agg({
                'price': 'mean',
                'id': 'count'
            }).reset_index()
            
            neighborhood_price.columns = ['Neighborhood', 'Average Price', 'Listing Count']
            
            min_listings = min(3, neighborhood_price['Listing Count'].min())
            neighborhood_price = neighborhood_price[neighborhood_price['Listing Count'] >= min_listings]
            
            if not neighborhood_price.empty:
                neighborhood_price = neighborhood_price.sort_values('Average Price', ascending=False)
                top_n = min(15, len(neighborhood_price))
                top_price_neighborhoods = neighborhood_price.head(top_n)
                
                price_by_hood = px.bar(
                    top_price_neighborhoods,
                    x='Average Price',
                    y='Neighborhood',
                    orientation='h',
                    text='Average Price',
                    height=500
                )
                
                price_by_hood.update_layout(
                    yaxis={'categoryorder':'total ascending'},
                    margin=dict(l=200)
                )
                price_by_hood.update_traces(texttemplate='$%{text:.0f}', textposition='outside')
                
                plotly(price_by_hood)
                
                if not top_price_neighborhoods.empty:
                    idx = min(len(top_price_neighborhoods) - 1, top_n - 1)
                    most_expensive = top_price_neighborhoods.iloc[idx]['Neighborhood']
                    avg_price = top_price_neighborhoods.iloc[idx]['Average Price']
                    text(f"**Insight**: {most_expensive} commands the highest average price at ${avg_price:.0f}/night, suggesting it's a premium location for travelers.")
            else:
                text("**Note**: Not enough neighborhood data to show price analysis.")
        
        if 'neighbourhood' in df.columns and 'room_type' in df.columns:
            text("### Room Type Distribution by Neighborhood")
            
            top_n_count = min(10, df['neighbourhood'].nunique())
            top_neighborhoods = df['neighbourhood'].value_counts().head(top_n_count).index.tolist()
            
            if top_neighborhoods:
                filtered_df = df[df['neighbourhood'].isin(top_neighborhoods)]
                
                room_by_hood = px.histogram(
                    filtered_df,
                    x='neighbourhood',
                    color='room_type',
                    barmode='group',
                    color_discrete_sequence=COLORS,
                    labels={"neighbourhood": "Neighborhood", "room_type": "Room Type", "count": "Number of Listings"},
                    height=500
                )
                
                room_by_hood.update_layout(
                    xaxis={'categoryorder':'total descending'},
                    xaxis_title="Neighborhood",
                    yaxis_title="Number of Listings",
                    legend_title="Room Type",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                )
                
                plotly(room_by_hood)
                
                text(f"**Insight**: Different neighborhoods show distinct patterns in property types. Some areas specialize in entire homes, while others have a higher proportion of private rooms.")
            else:
                text("**Note**: Not enough neighborhood data to show room type distribution.")
        
        if 'neighbourhood' in df.columns and 'room_type' in df.columns and 'price' in df.columns:
            text("### Price Heatmap by Neighborhood and Room Type")
            
            heatmap_data = df.groupby(['neighbourhood', 'room_type'])['price'].mean().reset_index()
            
            if not heatmap_data.empty and len(heatmap_data) > 1:
                try:
                    pivot_data = heatmap_data.pivot(index='neighbourhood', columns='room_type', values='price')
                    
                    hood_order = df.groupby('neighbourhood')['price'].mean().sort_values(ascending=False).index.tolist()
                    top_n = min(15, len(hood_order))
                    
                    hood_order = [h for h in hood_order if h in pivot_data.index]
                    
                    if hood_order:
                        pivot_data = pivot_data.reindex(hood_order[:top_n])
                        
                        fig = px.imshow(
                            pivot_data,
                            labels=dict(x="Room Type", y="Neighborhood", color="Price ($)"),
                            x=pivot_data.columns,
                            y=pivot_data.index,
                            text_auto='.0f',
                            aspect="auto",
                            height=500
                        )
                        
                        fig.update_layout(
                            coloraxis_colorbar=dict(title="Average Price ($)"),
                            xaxis_title="Room Type",
                            yaxis_title="Neighborhood"
                        )
                        
                        plotly(fig)
                        
                        text(f"**Insight**: This heatmap reveals premium neighborhoods and property types. The price difference between entire homes and private rooms varies substantially by neighborhood, indicating different market dynamics.")
                    else:
                        text("**Note**: Not enough data to create a meaningful heatmap after filtering.")
                except Exception as e:
                    text(f"**Note**: Could not create heatmap: {str(e)}")
                    text("Try adjusting your filters to include more neighborhoods and room types.")
            else:
                text("**Note**: Not enough data to create a meaningful heatmap. Try adjusting your filters.")

elif current_tab == "💰 Price Insights":
    text("## 💰 Price Insights")
    
    if 'room_type' in df.columns and 'price' in df.columns and len(df) > 0:
        text("### Price Distribution by Property Type")
        
        fig = px.box(
            df,
            x='room_type',
            y='price',
            color='room_type',
            color_discrete_sequence=COLORS,
            points="outliers",
            labels={"room_type": "Property Type", "price": "Price ($)"},
            height=500
        )
        
        for i, room in enumerate(df['room_type'].unique()):
            try:
                median_price = df[df['room_type'] == room]['price'].median()
                fig.add_annotation(
                    x=room,
                    y=median_price,
                    text=f"${median_price:.0f}",
                    showarrow=False,
                    yshift=10
                )
            except Exception:
                pass
        
        fig.update_layout(
            xaxis_title="Property Type",
            yaxis_title="Price ($)",
            showlegend=False,
            yaxis_range=[0, df['price'].quantile(0.95)]
        )
        
        plotly(fig)
        
        text(f"**Insight**: As expected, entire homes command significantly higher prices than private rooms. The wide spread in prices for entire homes indicates diverse offerings from budget to luxury properties.")
    
    if 'minimum_nights' in df.columns and 'price' in df.columns and len(df) > 0:
        text("### Price vs. Minimum Stay Requirement")
        
        filtered_df = df[df['minimum_nights'] <= 14]
        
        if len(filtered_df) > 0:
            fig = px.scatter(
                filtered_df,
                x='minimum_nights',
                y='price',
                color='room_type',
                size='reviews_per_month' if 'reviews_per_month' in filtered_df.columns else None,
                opacity=0.7,
                color_discrete_sequence=COLORS,
                labels={"minimum_nights": "Minimum Nights", "price": "Price ($)", "room_type": "Property Type"},
                height=500
            )
            
            fig.update_layout(
                xaxis_title="Minimum Stay (Nights)",
                yaxis_title="Price ($)",
                legend_title="Property Type",
                yaxis_range=[0, filtered_df['price'].quantile(0.95)]
            )
            
            plotly(fig)
            
            text(f"**Insight**: The scatter plot shows the relationship between minimum stay requirements and price. Properties with longer minimum stays tend to have more varied pricing.")
        else:
            text("**Note**: Not enough data to show minimum nights analysis after filtering.")
    
    if 'reviews_per_month' in df.columns and 'price' in df.columns and len(df) > 0:
        text("### Price vs. Review Frequency")
        
        has_reviews = df[df['reviews_per_month'] > 0]
        
        if len(has_reviews) > 0:
            fig = px.scatter(
                has_reviews,
                x='price',
                y='reviews_per_month',
                color='room_type',
                color_discrete_sequence=COLORS,
                opacity=0.7,
                labels={"price": "Price ($)", "reviews_per_month": "Reviews per Month", "room_type": "Property Type"},
                height=500
            )
            
            fig.update_layout(
                xaxis_title="Price ($)",
                yaxis_title="Reviews per Month",
                legend_title="Property Type",
                xaxis_range=[0, has_reviews['price'].quantile(0.95)]
            )
            
            plotly(fig)
            
            text(f"**Insight**: Lower-priced listings tend to receive more reviews per month, suggesting they may have higher occupancy rates. This could indicate better value perception by guests or simply higher turnover.")
        else:
            text("**Note**: No listings with reviews found in the current selection.")
    
    if 'price' in df.columns and 'room_type' in df.columns and len(df) > 0:
        text("### Price Analysis by Property Type")
        
        room_types_present = df['room_type'].unique()
        
        if len(room_types_present) > 0:
            price_stats = df.groupby('room_type')['price'].agg([
                ('Min Price', 'min'),
                ('Average Price', 'mean'),
                ('Median Price', 'median'),
                ('Max Price', 'max'),
                ('Count', 'count')
            ]).reset_index()
            
            for col in ['Min Price', 'Average Price', 'Median Price', 'Max Price']:
                price_stats[col] = price_stats[col].map('${:.2f}'.format)
                
            table(price_stats, title="Price Statistics by Property Type")
        else:
            text("**Note**: No room type data available for price analysis.")

elif current_tab == "👥 Host Analysis":
    text("## 👥 Host Analysis")
    
    if 'host_id' in df.columns and len(df) > 0:
        text("### Host Listing Count Distribution")
        
        host_counts = df.groupby('host_id').size().reset_index()
        host_counts.columns = ['host_id', 'listing_count']
        
        if not host_counts.empty:
            host_counts['listing_group'] = pd.cut(
                host_counts['listing_count'], 
                bins=[0, 1, 2, 5, 10, float('inf')],
                labels=['1 Listing', '2 Listings', '3-5 Listings', '6-10 Listings', '11+ Listings']
            )
            
            host_group_counts = host_counts['listing_group'].value_counts().reset_index()
            host_group_counts.columns = ['Listings per Host', 'Number of Hosts']
            
            fig = px.pie(
                host_group_counts,
                values='Number of Hosts',
                names='Listings per Host',
                color_discrete_sequence=COLORS,
                hole=0.4,
                height=500
            )
            
            fig.update_layout(
                legend_title="Listings per Host",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
            )
            fig.update_traces(textinfo='percent+label')
            
            plotly(fig)
            
            single_listing_hosts = host_group_counts[host_group_counts['Listings per Host'] == '1 Listing']
            if not single_listing_hosts.empty:
                single_listing_pct = (single_listing_hosts['Number of Hosts'].values[0] / 
                                    host_group_counts['Number of Hosts'].sum() * 100)
                
                text(f"**Insight**: {single_listing_pct:.1f}% of hosts have only one listing, suggesting many are individuals renting out their homes.")
            else:
                text("**Note**: No single-listing hosts found in the current selection.")
        else:
            text("**Note**: Not enough host data available for analysis.")
    
    if 'host_id' in df.columns and 'host_name' in df.columns and len(df) > 0:
        text("### Top Hosts by Number of Listings")
        
        top_hosts = df.groupby(['host_id', 'host_name']).size().reset_index()
        
        if not top_hosts.empty:
            top_hosts.columns = ['Host ID', 'Host Name', 'Listing Count']
            top_hosts = top_hosts.sort_values('Listing Count', ascending=False)
            
            top_n = min(15, len(top_hosts))
            top_hosts = top_hosts.head(top_n)
            
            fig = px.bar(
                top_hosts,
                x='Listing Count',
                y='Host Name',
                orientation='h',
                text='Listing Count',
                height=500
            )
            
            fig.update_layout(
                yaxis={'categoryorder':'total ascending'},
                xaxis_title="Number of Listings",
                margin=dict(l=200)
            )
            fig.update_traces(textposition='outside')
            
            plotly(fig)
            
            if len(top_hosts) > 0:
                idx = min(len(top_hosts) - 1, 0)
                max_listings = top_hosts.iloc[idx]['Listing Count']
                top_host = top_hosts.iloc[idx]['Host Name']
                text(f"**Insight**: The top host '{top_host}' manages {max_listings} listings, indicating a professional operation rather than a casual host.")
        else:
            text("**Note**: Not enough host data available for analysis.")
    
    if 'host_id' in df.columns and 'price' in df.columns and len(df) > 0:
        text("### Average Price by Host Portfolio Size")
        
        host_listing_counts = df.groupby('host_id').size().reset_index(name='listing_count')
        
        if not host_listing_counts.empty:
            host_listing_counts['listing_group'] = pd.cut(
                host_listing_counts['listing_count'], 
                bins=[0, 1, 2, 5, 10, float('inf')],
                labels=['1 Listing', '2 Listings', '3-5 Listings', '6-10 Listings', '11+ Listings']
            )
            
            host_df = pd.merge(df[['host_id', 'price']], host_listing_counts[['host_id', 'listing_group']], on='host_id')
            
            price_by_size = host_df.groupby('listing_group')['price'].mean().reset_index()
            
            if not price_by_size.empty:
                fig = px.bar(
                    price_by_size,
                    x='listing_group',
                    y='price',
                    text='price',
                    labels={'listing_group': 'Host Portfolio Size', 'price': 'Average Price ($)'},
                    height=400
                )
                
                fig.update_layout(
                    xaxis_title="Host Portfolio Size",
                    yaxis_title="Average Price ($)"
                )
                fig.update_traces(texttemplate='$%{text:.0f}', textposition='outside')
                
                plotly(fig)
                
                text("**Insight**: This chart shows how pricing strategies may differ between casual hosts with few properties and professional hosts with many listings.")
            else:
                text("**Note**: Not enough data to analyze prices by host portfolio size.")
        else:
            text("**Note**: Not enough host data available for analysis.")

elif current_tab == "⭐ Reviews & Ratings":
    text("## ⭐ Reviews & Ratings")
    
    if 'reviews_per_month' in df.columns and len(df) > 0:
        text("### Reviews per Month Distribution")
        
        has_reviews = df[df['reviews_per_month'] > 0]
        
        if len(has_reviews) > 0:
            fig = px.histogram(
                has_reviews,
                x='reviews_per_month',
                nbins=30,
                marginal="box",
                height=400
            )
            
            median_reviews = has_reviews['reviews_per_month'].median()
            fig.add_vline(x=median_reviews, line_dash="dash", line_color="red", 
                        annotation_text=f"Median: {median_reviews:.1f}", 
                        annotation_position="top right")
            
            fig.update_layout(
                xaxis_title="Reviews per Month",
                yaxis_title="Number of Listings",
                bargap=0.1
            )
            
            plotly(fig)
            
            text(f"**Insight**: Most listings receive fewer than {median_reviews*2:.1f} reviews per month. Since guests typically leave reviews after stays, this metric can serve as a proxy for booking frequency.")
        else:
            text("**Note**: No listings with review data found in the current selection.")
    
    if 'reviews_per_month' in df.columns and 'room_type' in df.columns and len(df) > 0:
        text("### Average Reviews per Month by Property Type")
        
        reviews_by_type = df.groupby('room_type')['reviews_per_month'].mean().reset_index()
        
        if not reviews_by_type.empty:
            reviews_by_type.columns = ['Room Type', 'Average Reviews/Month']
            
            fig = px.bar(
                reviews_by_type,
                x='Room Type',
                y='Average Reviews/Month',
                text='Average Reviews/Month',
                height=400
            )
            
            fig.update_layout(
                xaxis_title="Property Type",
                yaxis_title="Average Reviews per Month"
            )
            fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            
            plotly(fig)
            
            if len(reviews_by_type) > 0:
                idx = reviews_by_type['Average Reviews/Month'].idxmax()
                most_reviewed_type = reviews_by_type.iloc[idx]['Room Type']
                
                text(f"**Insight**: {most_reviewed_type} properties receive the most reviews per month on average, suggesting they have the highest occupancy rates.")
            else:
                text("**Note**: Not enough review data to identify the most reviewed property type.")
        else:
            text("**Note**: Not enough review data to analyze by property type.")
    
    if 'last_review' in df.columns and 'days_since_review' in df.columns and len(df) > 0:
        text("### Review Recency Analysis")
        
        has_review_date = df.dropna(subset=['last_review'])
        
        if len(has_review_date) > 0:
            has_review_date['recency'] = pd.cut(
                has_review_date['days_since_review'],
                bins=[0, 30, 90, 180, 365, float('inf')],
                labels=['Last 30 days', '30-90 days ago', '3-6 months ago', '6-12 months ago', 'Over a year ago']
            )
            
            recency_counts = has_review_date['recency'].value_counts().reset_index()
            
            if not recency_counts.empty:
                recency_counts.columns = ['Review Recency', 'Number of Listings']
                
                recency_order = ['Last 30 days', '30-90 days ago', '3-6 months ago', '6-12 months ago', 'Over a year ago']
                recency_counts['order'] = recency_counts['Review Recency'].map({k: i for i, k in enumerate(recency_order)})
                recency_counts = recency_counts.sort_values('order')
                recency_counts = recency_counts.drop('order', axis=1)
                
                fig = px.pie(
                    recency_counts,
                    values='Number of Listings',
                    names='Review Recency',
                    hole=0.4,
                    height=400
                )
                
                fig.update_layout(
                    legend_title="Last Review",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                )
                fig.update_traces(textinfo='percent+label')
                
                plotly(fig)
                
                recent_df = recency_counts[recency_counts['Review Recency'] == 'Last 30 days']
                if not recent_df.empty:
                    recent_pct = (recent_df['Number of Listings'].values[0] / 
                                recency_counts['Number of Listings'].sum() * 100)
                    
                    text(f"**Insight**: {recent_pct:.1f}% of listings have been reviewed in the last 30 days, indicating they're actively being booked.")
                else:
                    text("**Insight**: No listings have been reviewed in the last 30 days. This could indicate seasonal trends or data collection issues.")
            else:
                text("**Note**: Not enough review recency data to analyze.")
        else:
            text("**Note**: No listings with review dates found in the current selection.")

text("---")
text("### About this Dashboard")
text("""
This dashboard provides comprehensive market insights using San Francisco Airbnb data.
Created with Preswald for Structured Labs Coding Assessment.
""")