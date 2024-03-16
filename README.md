
# YouTube Data Harvesting and Warehousing using SQL and Streamlit

This project aims to develop a Streamlit application that allows users to access, analyze, and store data from multiple YouTube channels. Leveraging Python, Streamlit, Google API, and SQL databases, the application provides a user-friendly interface for retrieving, storing, and querying YouTube channel information and video data.

# Table of Contents
Project Overview
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

# Project Overview
YouTube Data Harvesting and Warehousing is designed to provide users with a comprehensive tool for accessing and managing data from YouTube channels. By integrating Streamlit for the user interface, Google API for data retrieval, and SQL databases for data storage, the project facilitates efficient data analysis and management.

# Features
Retrieve channel details by providing YouTube channel IDs.
Collect data for up to 10 different YouTube channels.
Store data in a SQL database (MySQL or PostgreSQL).
Search and retrieve data from the SQL database.
Display data analysis results using Streamlit.

# Skills Developed
Python scripting for data retrieval and manipulation.
Streamlit for building a user-friendly web application.
API integration with the YouTube Data API.
Data management using SQL databases.
GitHub for version control and collaboration.

# Domain
Social Media

# Problem Statement
The problem statement is to create a Streamlit application with the following features:

Allow users to input YouTube channel IDs and retrieve relevant data.
Collect data for multiple channels and store it in a SQL database.
Enable users to search and retrieve data from the database.
Display data analysis results in the Streamlit application.

# Approach
Set up a Streamlit app for the user interface.
Connect to the YouTube API to retrieve channel and video data.
Store the data temporarily before migrating it to a SQL database.
Migrate data to a SQL data warehouse (MySQL or PostgreSQL).
Query the SQL data warehouse to retrieve data for specific channels.
Display the retrieved data in the Streamlit app using data visualization features.

# Usage
#Installation
# 1.Clone the repository:
git clone https://github.com/your-username/youtube-data-harvesting.git

# 2.Install dependencies:
cd youtube-data-harvesting
pip install -r requirements.txt

# 3.Running the Application:
streamlit run app.py

# Project Structure
1. app.py: Main Streamlit application file.
2. utils.py: Utility functions for database operations and API requests.
3. requirements.txt: List of dependencies.

# Database Schema
# youtube_data Database Schema

channels Table
Column Name	Data Type	Description
channel_id	VARCHAR(255)	Unique identifier for the channel
channel_name	VARCHAR(255)	Name of the channel
channel_type	VARCHAR(255)	Type of the channel
channel_views	INT	Total number of views for the channel
channel_description	TEXT	Description of the channel
channel_status	VARCHAR(255)	Status of the channel
playlists Table
Column Name	Data Type	Description
playlist_id	VARCHAR(255)	Unique identifier for the playlist
channel_id	VARCHAR(255)	Foreign key referencing the channel table
playlist_name	VARCHAR(255)	Name of the playlist
comments Table
Column Name	Data Type	Description
comment_id	VARCHAR(255)	Unique identifier for the comment
video_id	VARCHAR(255)	Foreign key referencing the video table
comment_text	TEXT	Text of the comment
comment_author	VARCHAR(255)	Name of the comment author
comment_date	DATETIME	Date and time when the comment was published
videos Table
Column Name	Data Type	Description
video_id	VARCHAR(255)	Unique identifier for the video
playlist_id	VARCHAR(255)	Foreign key referencing the playlist table
video_name	VARCHAR(255)	Name of the video
video_description	TEXT	Description of the video
published_date	DATETIME	Date and time when the video was published
view_count	INT	Total number of views for the video
like_count	INT	Total number of likes for the video
dislike_count	INT	Total number of dislikes for the video
favorite_count	INT	Total number of times the video has been marked as a favorite
comment_count	INT	Total number of comments on the video
duration	INT	Duration of the video in seconds
thumbnail	VARCHAR(255)	URL of the thumbnail for the video
caption_status	VARCHAR(255)	Status of the video caption

# Additional Resources
Streamlit Documentation
YouTube API Reference

# Demo
A demo video of the working model can be found here.
