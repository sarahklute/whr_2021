'''
Sarah Klute
DS 4300 HW3: Mongo Database
Visualizing results and Mongo API calls
'''
# Imports
import pymongo
import pandas as pd
import folium
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


class WorldHappinessAPI:

    def __init__(self, host='localhost', port=27017, db_name='world_happiness_report_db', collection_name ='whr_2021'):
        self.client = pymongo.MongoClient(host, port)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def calculate_region_explanation(self):
        '''Query for caclulating the explaination of influence on happiness index '''
        pipeline = [
            {
                "$project": {
                    "region": "$Regional indicator",
                    "explanations": {"$objectToArray": "$$ROOT"}
                }
            },
            {"$unwind": "$explanations"},
            {
                "$match": {
                    "explanations.k": {"$regex": "^Explained by:"}
                }
            },
            {
                "$group": {
                    "_id": {
                        "region": "$region",
                        "explanation": "$explanations.k"
                    },
                    "total_influence": {"$sum": "$explanations.v"}
                }
            },
            {"$sort": {"_id.region": 1, "total_influence": -1}},
            {
                "$group": {
                    "_id": "$_id.region",
                    "top_explanation": {"$first": "$_id.explanation"},
                    "total_influence": {"$first": "$total_influence"}
                }
            }
        ]

        # Cast to dataframe
        result = list(self.collection.aggregate(pipeline))
        df_region = pd.DataFrame(result)
        # Plot df
        self.plot_region_explanation(df_region)
        return df_region


    def plot_region_explanation(self, df):
        '''Plot region explanation, color markers by Top Explanation for Region'''
        plt.figure(figsize=(12, 8))
        sns.barplot(data=df, y='_id', x='total_influence', hue='top_explanation')
        plt.xlabel('Total Influence')
        plt.ylabel('Region')
        plt.title('Total Influence by Region with Explanation')
        plt.legend(title='Top Explanation')
        plt.show()

    def calculate_country_explanation(self):
        '''Query for calculating the explanation of influence on the happiness index by country'''
        pipeline = [
            {
                "$project": {
                    "country": "$Country name",
                    "explanations": {"$objectToArray": "$$ROOT"}
                }
            },
            {"$unwind": "$explanations"},
            {
                "$match": {
                    "explanations.k": {"$regex": "^Explained by:"}
                }
            },
            {
                "$group": {
                    "_id": {
                        "country": "$country",
                        "explanation": "$explanations.k"
                    },
                    "total_influence": {"$sum": "$explanations.v"}
                }
            },
            {"$sort": {"_id.country": 1, "total_influence": -1}},
            {
                "$group": {
                    "_id": "$_id.country",
                    "top_explanation": {"$first": "$_id.explanation"},
                    "total_influence": {"$first": "$total_influence"}
                }
            }
        ]

        # Cast to dataframe
        result = list(self.collection.aggregate(pipeline))
        df = pd.DataFrame(result)
        # Displaying dataframe
        print(df)
        return df

    def visualize_country_explanation(self):
        df = self.calculate_country_explanation()
        # Group by country: get the top explanation and total influence
        grouped = df.groupby('_id').agg({'top_explanation': 'first', 'total_influence': 'sum'}).reset_index()

        # Unique explanations
        unique_explanations = grouped['top_explanation'].unique()
        num_explanations = len(unique_explanations)

        # Color map for unique explanations
        color_map = plt.cm.get_cmap('tab10', num_explanations)

        fig, ax = plt.subplots(figsize=(40, 8))

        # Empty bars for each unique explanation (to create legend)
        for i, explanation in enumerate(unique_explanations):
            ax.bar(0, 0, color=color_map(i), label=explanation)

        # Iterate through each country
        for country, explanation, influence in zip(grouped['_id'], grouped['top_explanation'],
                                                   grouped['total_influence']):
            # Find  index of  explanation in unique explanations list
            explanation_index = np.where(unique_explanations == explanation)[0][0]
            # Plot  bar with the corresponding color
            ax.bar(country, influence, color=color_map(explanation_index))

        # Set labels and title
        ax.set_xlabel('Country')
        ax.set_ylabel('Total Influence')
        ax.set_title('Top Explanation Influence on Happiness Index by Country')
        ax.legend(title='Top Explanation', fontsize='large', loc='upper left')
        ax.set_xticklabels(grouped['_id'], rotation=45, ha='right')  # Rotate country labels
        plt.tight_layout()
        plt.savefig('Top Explanation.png')
        plt.show()


    def happiness(self, ascending=True):
        '''Query for reporting countries with highest or lowest happiness levels depending
        on user input'''
        # Happiest or Least happy
        sort_order = 1 if ascending else -1

        pipeline = [
            {"$project": {"Country name": 1, "_id": 0, "Ladder score": 1}},
            {"$sort": {"Ladder score": sort_order}},
            {"$limit": 10}
        ]
        # Cast to dataframe
        result = list(self.collection.aggregate(pipeline))
        df = pd.DataFrame(result)
        return df

    def happiness_levels(self):
        '''Plot happiest and least happy levels for top 5 and bottom 5 countries'''

        sns.set(style="whitegrid")
        plt.figure(figsize=(10, 6))

        # Get top and bottom countries
        top_countries = self.happiness(ascending=False)
        bottom_countries = self.happiness(ascending=True)

        # Concatenate the dataframes
        df = pd.concat([top_countries, bottom_countries])

        # Define light red and light green colors
        light_red = "#FFB6C1"  # Light red
        light_green = "#90EE90"  # Light green

        # Define color palette
        colors = [light_red if country in bottom_countries['Country name'].values else light_green for country in df['Country name']]

        # Plotting dataframe
        sns.barplot(x='Ladder score', y='Country name', data=df, palette=colors)
        plt.xlabel('Happiness Score')
        plt.ylabel('Country')
        plt.title('Top and Bottom Happiest Countries')
        plt.show()

    def countries_by_ladder_score_range(self, min_score, max_score):
        '''Query for reporting countries within a specified ladder score range'''
        pipeline = [
            {
                '$match': {
                    'Ladder score': {
                        '$gte': min_score,
                        '$lte': max_score
                    }
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'Country name': 1,
                    'Regional indicator': 1,
                    'Ladder score': 1
                }
            }
        ]
        result = list(self.collection.aggregate(pipeline))
        df = pd.DataFrame(result)
        return df

    def ladder_score_choropleth(self, min_score, max_score):
        '''Create a choropleth map based on the ladder score'''
        # Get countries ladder scores within user specified range
        df = self.countries_by_ladder_score_range(min_score, max_score)
        print(df)

        # Convert dataframe to dictionary
        data_dict = df.set_index('Country name')['Ladder score'].to_dict()
        print('data dict here:', data_dict)

        # Create base map
        world_map = folium.Map(location=[0, 0], zoom_start=2)

        # Load the GeoJSON data for countries
        countries_geojson = 'world.geo.json/countries.geo.json'  # Replace with the path to your GeoJSON data

        # Create choropleth layer
        folium.Choropleth(
            geo_data=countries_geojson,
            name='choropleth',
            data=data_dict,
            columns=['Country name', 'Ladder score'],
            key_on='feature.properties.name',
            fill_color='YlGnBu',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Ladder Score'
        ).add_to(world_map)

        # Add layer control
        folium.LayerControl().add_to(world_map)
        return world_map

    def high_corruption(self, top_n=10):
        '''Query for reporting top countries with high levels of corruption'''
        pipeline = [
            {
                '$group': {
                    '_id': '$Country name',
                    'average_corruption_perceptions': {'$avg': '$Perceptions of corruption'}
                }
            },
            {"$sort": {"average_corruption_perceptions": -1}},
            {"$limit": top_n}
        ]
        # Cast to dataframe
        result = list(self.collection.aggregate(pipeline))
        df = pd.DataFrame(result)
        return df

    def top_countries_corruption_choropleth(self, top_n=5):
        '''Create a choropleth map based on percentage of corruption for top countries'''
        # Get top countries with high levels of corruption
        df = self.high_corruption(top_n)
        print(df)

        # Create base map
        world_map = folium.Map(location=[0, 0], zoom_start=2)

        # Load the GeoJSON data for countries
        countries_geojson = 'world.geo.json/countries.geo.json'  # Replace with the path to your GeoJSON data

        # Create choropleth layer
        folium.Choropleth(
            geo_data=countries_geojson,
            name='choropleth',
            data=df,
            columns=['_id', 'average_corruption_perceptions'],
            key_on='feature.properties.name',
            fill_color='YlOrRd',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Average Corruption Perceptions (%)'
        ).add_to(world_map)

        # Add layer control
        folium.LayerControl().add_to(world_map)
        return world_map

