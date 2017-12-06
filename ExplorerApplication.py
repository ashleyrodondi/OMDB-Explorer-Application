from os.path import dirname, join
import pandas.io.sql as psql
import sqlite3 as sql
import numpy as np
from bokeh.models.widgets import Slider
from bokeh.models.widgets import Select
from bokeh.models.widgets import TextInput
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool
from bokeh.plotting import figure
from bokeh.layouts import layout
from bokeh.layouts import widgetbox
from bokeh.io import curdoc

# Set path to movies database
working_directory = "C:\\Users\\Ashley Rodondi\\Documents\\BMKT 670 Applied Data Analytics\\Projects\\Explorer Application\\"
database = "movies.db"
path = working_directory + database

connect = sql.connect(path) # Connect movies database 
query = open(join(dirname(working_directory), "query.sql")).read() # Open query 
movies = psql.read_sql(query, connect) # Read movies database and query into Python 

movies["color"] = np.where(movies["Oscars"] > 0, "blue", "grey") # Identifying movies having more than 0 Oscars and labling each as a blue dot
movies["alpha"] = np.where(movies["Oscars"] > 0, 0.9, 0.25)
movies.fillna(0, inplace=True) # Replace missing values (N/A) with zero 
movies["revenue"] = movies.BoxOffice.apply(lambda x: '{:,d}'.format(int(x)))

# Creating axis map on bokeh plot
axis_map = {
    "Tomato Meter": "Meter",
    "Numeric Rating": "numericRating",
    "Number of Reviews": "Reviews",
    "Box Office (dollars)": "BoxOffice",
    "Length (minutes)": "Runtime",
    "Year": "Year"}

# Input controls
reviews = Slider(title = "Minimum number of reviews", value = 10, start = 10, end = 300, step = 10) # Slider for minimum number of movies
min_year = Slider(title = "Year released", start = 1970, end = 2014, value = 1970, step = 1) # Slider for year released
oscars = Slider(title = "Minimum number of Oscar wins (Blue Dots)", start = 0, end = 4, value =0, step =1) # Slider for minimum number of Oscar wins
boxoffice = Slider(title = "Dollars at Box Office (millions)", start =0, end =800, value =0, step =1) # Slider for dollars at box office
genre = Select(title = "Genre", value = "All",
               options = open(join(dirname(working_directory), 'genres.txt')).read().split()) # Select dropdown for genre
cast = TextInput(title = "Cast names (i.e., Emma Watson - Case Sensitive )  ") # text input for film cast name 
x_axis = Select(title = "X Axis", options=sorted(axis_map.keys()), value = "Number of Reviews") # Select dropdown for changing x-axis 
y_axis = Select(title = "Y Axis", options=sorted(axis_map.keys()), value = "Box Office (dollars)") # Select dropdown for changing y-axis 

# Column Data Source 
source = ColumnDataSource(data = dict(x = [], y = [], color = [], title = [], year = [], revenue = [], alpha = []))

# Code when hovering over a point on the plot will return data about the point
hover = HoverTool(tooltips = [
    ("Title", "@title"),
    ("Year", "@year"),
    ("$", "@revenue")])

# Making plot identifying height, weight, title, and more
p = figure(plot_height = 800, plot_width = 900, title = "IMDb and Rotten Tomatos Movie Explorer", toolbar_location = None, tools = [hover])
p.circle(x = "x", y = "y", source = source, size = 8, color = "color", line_color = None, fill_alpha = "alpha")

def select_movies():
    genre_val = genre.value
    cast_val = cast.value.strip()
    selected = movies[
        (movies.Reviews >= reviews.value) &
        (movies.BoxOffice >= (boxoffice.value * 1e6)) &
        (movies.Year >= min_year.value) &
        (movies.Oscars >= oscars.value)]
    
    if (genre_val != "All"):
        selected = selected[selected.Genre.str.contains(genre_val) == True]
    if (cast_val != ""):
        selected = selected[selected.Cast.str.contains(cast_val) == True]
    return selected

def update():
    df = select_movies()
    x_name = axis_map[x_axis.value]
    y_name = axis_map[y_axis.value]

    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = y_axis.value
    p.title.text = "%d movies selected" % len(df)
    source.data = dict(
        x = df[x_name],
        y = df[y_name],
        color = df["color"],
        title = df["Title"],
        year = df["Year"],
        revenue = df["revenue"],
        alpha = df["alpha"],
    )

controls = [reviews, boxoffice, genre, min_year, oscars, cast, x_axis, y_axis]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

sizing_mode = 'fixed'  

inputs = widgetbox(*controls, sizing_mode=sizing_mode)
l = layout([
    [inputs, p]], sizing_mode=sizing_mode)

update()  

curdoc().add_root(l)
curdoc().title = "IMDb and Rotten Tomatos Movie Explorer"

# In comand prompt cd to working directory and then enter "bokeh serve --show ExplorerApplication.py" to see interactive explorer on local host
