YouTube Data Harvesting and Warehousing using SQL and Streamlit

Overview
YouTube Data Harvesting and Warehousing is a comprehensive project aimed at building a Streamlit application that enables users to access, analyze, and store data from multiple YouTube channels. By leveraging Python, Streamlit, Google API, and SQL databases, this project provides a user-friendly interface for retrieving, storing, and querying YouTube channel information and video data.

Table of Contents
Overview
Features
Skills Developed
Domain
Problem Statement
Approach
Usage
Project Structure
Database Schema
Additional Resources
Demo
Features
Retrieve channel details by providing YouTube channel IDs.
Collect data for up to 10 different YouTube channels.
Store data in a SQL database (MySQL or PostgreSQL).
Search and retrieve data from the SQL database.
Display data analysis results using Streamlit.
Skills Developed
Python scripting for data retrieval and manipulation.
Streamlit for building a user-friendly web application.
API integration with the YouTube Data API.
Data management using SQL databases.
GitHub for version control and collaboration.
Domain
Social Media

Problem Statement
The problem statement is to create a Streamlit application with the following features:

Allow users to input YouTube channel IDs and retrieve relevant data.
Collect data for multiple channels and store it in a SQL database.
Enable users to search and retrieve data from the database.
Display data analysis results in the Streamlit application.
Approach
Set up a Streamlit app for the user interface.
Connect to the YouTube API to retrieve channel and video data.
Store the data temporarily before migrating it to a SQL database.
Migrate data to a SQL data warehouse (MySQL or PostgreSQL).
Query the SQL data warehouse to retrieve data for specific channels.
Display the retrieved data in the Streamlit app using data visualization features.
Usage
Installation
Clone the repository:
bash
Copy code
git clone https://github.com/your-username/youtube-data-harvesting.git
Install dependencies:
bash
Copy code
cd youtube-data-harvesting
pip install -r requirements.txt
Running the Application
bash
Copy code
streamlit run app.py
Project Structure
app.py: Main Streamlit application file.
utils.py: Utility functions for database operations and API requests.
requirements.txt: List of dependencies.
Database Schema
youtube_data: MySQL database schema.
channels: Table to store channel details.
playlists: Table to store playlist details.
videos: Table to store video details.
comments: Table to store comments data.
Additional Resources
Streamlit Documentation
YouTube API Reference
Demo
A demo video of the working model is available on LinkedIn here.
