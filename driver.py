'''
Sarah Klute
DS 4300 HW3 Mongo Database
Driver application

To run Choropleth maps must have world.geo.json downloaded!

Dataset loaded through MongoCompass
'''
# Imports
from mongo_api import WorldHappinessAPI
import pandas as pd
import webbrowser

def main():

    # Authenticate
    api = WorldHappinessAPI()

    # Data loaded on Compass

    # Forcing Dataframe to show all
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    # ----Happiest or Least Happy Countries-----#
    # Ask the user for input to determine sorting order
    user_input = input("Do you want the happiest or least happy countries? (happiest/least): ")

    if user_input.lower() == "happiest":
        ascending = False
    elif user_input.lower() == "least":
        ascending = True
    else:
        print("Invalid input. Defaulting to happiest.")
        ascending = False

    # Top (happiest/least happy) countries by user input
    happiness_user = api.happiness(ascending)
    print(happiness_user)
    # Visualization of happiest and least happy countries
    api.happiness_levels()

    # ---Ladder Score Explainations----#
    # Country explanation of ladder score
    happiness_explanation_country = api.visualize_country_explanation()
    happiness_explanation_country

    # Regional Explanation of ladder score
    region_explanation_influence = api.calculate_region_explanation()
    print(region_explanation_influence)


    # ---Ladder Score on Choroplath map---#
    # Happiness score visualized on map by max and min levels (user)
    max = int(input("Enter max happiness score (>7.842) for map:"))
    min = int(input("Enter max happiness score (<2.523) for map:"))
    # Call api
    map_ladder = api.ladder_score_choropleth(min, max)
    # Make choropleth
    map_ladder.save('ladder_choropleth_map.html')  # Save the map as an HTML file
    webbrowser.get('chrome').open('http://localhost:8000/ladder_choropleth_map.html')


    #---Corruption Visualization----#
    # Top countries with Corruption given N countries
    top_n = int(input("Enter the number of countries (max 149) you want to report for Average Corruption %: "))
    # API call
    map_corruption = api.top_countries_corruption_choropleth(top_n)
    # Choropleth call
    map_corruption.save('corruption_choropleth_map.html')
    webbrowser.get('chrome').open('http://localhost:8000/corruption_choropleth_map.html')


if __name__ == '__main__':
    main()