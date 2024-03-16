# Importing necessary libraries
import streamlit as st
import pymongo
import mysql.connector
import pandas as pd
from googleapiclient.discovery import build
import json

# YouTube API key
api_key = "AIzaSyBNB-PdYM3B8PVmk8rYWhb0yfPedDUeJo0"

# Function to connect to MongoDB Atlas
def connect_to_mongodb():
    # Connect to MongoDB Atlas
    client = pymongo.MongoClient("mongodb+srv://Bhavana:Nanu_300119@cluster0.qvrvp1a.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    # Access the database
    db = client['youtube_data']
    return db

# Function to create a collection in MongoDB Atlas
def create_collection(db, collection_name):
    # Access or create the collection
    collection = db[collection_name]
    print(f"Collection '{collection_name}' created successfully.")
    return collection

# Function to insert channel data into MongoDB Atlas
def insert_channel_data_mongodb(db, channel_data):
    # Access the collection
    collection = db['channels']
    # Insert channel data
    collection.insert_one(channel_data)

# Function to insert video details into MongoDB
def insert_video_data_mongodb(db, video_data):
    # Access the collection
    collection = db['videos']
    # Insert video data
    collection.insert_one(video_data)

# Function to insert comments data into MongoDB
def insert_comments_data_mongodb(db, comments_data):
    # Access the collection
    collection = db['comments']
    if isinstance(comments_data, list):
        # Insert comments data as a list
        if comments_data:  # Ensure the list is not empty
            collection.insert_many(comments_data)
    else:
        # Insert a single comment
        if comments_data:  # Ensure the document is not empty
            collection.insert_one(comments_data)

# Function to insert playlist details into MongoDB
def insert_playlist_data_mongodb(db, playlist_data):
    # Access the collection
    collection = db['playlists']
    
    # Ensure playlist_data is a list and not empty
    if isinstance(playlist_data, list) and playlist_data:
        # Insert playlist data
        collection.insert_many(playlist_data)
    else:
        print("Playlist data is not in the correct format or is empty. No data inserted.")

# Function to connect to MySQL database
def connect_to_mysql():
    # MySQL connection string
    return mysql.connector.connect(host="localhost", user="root", password="Rudraunsh_300119", database="youtube_data")

# Function to insert channel data into MySQL database
def insert_channel_data_mysql(connection, channel_data):
    try:
        # Create MySQL cursor
        cursor = connection.cursor()
        # Construct SQL query
        sql = "INSERT INTO channels (channel_id, channel_name, channel_views, channel_description, channel_status) VALUES (%s, %s, %s, %s, %s)"
        # Execute query
        cursor.execute(sql, (channel_data['Channel_Id'], channel_data['Channel_Name'], channel_data['Channel_Views'], channel_data['Channel_Description'], channel_data['Channel_Status']))
        # Commit changes
        connection.commit()
        print("Channel data inserted into MySQL successfully.")
    except Exception as e:
        print("Error inserting channel data into MySQL:", e)

# Function to insert video details into MySQL database
def insert_video_data_mysql(connection, video_data):
    try:
        # Create MySQL cursor
        cursor = connection.cursor()
        # Construct SQL query
        sql = "INSERT INTO videos (video_id, playlist_id, video_name, video_description, published_date, view_count, like_count, dislike_count, favorite_count, comment_count, duration, thumbnail, caption_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        # Execute query
        cursor.execute(sql, (video_data['Video_Id'], video_data['Playlist_Id'], video_data['Video_Name'], video_data['Video_Description'], video_data['PublishedAt'], video_data['View_Count'], video_data['Like_Count'], video_data['Dislike_Count'], video_data['Favorite_Count'], video_data['Comment_Count'], video_data['Duration'], video_data['Thumbnail'], video_data['Caption_Status']))
        # Commit changes
        connection.commit()
        print("Video data inserted into MySQL successfully.")
    except Exception as e:
        print("Error inserting video data into MySQL:", e)

# Function to insert comments data into MySQL database
def insert_comments_data_mysql(connection, comments_data):
    try:
        # Create MySQL cursor
        cursor = connection.cursor()
        # Construct SQL query
        sql = "INSERT INTO comments (comment_id, video_id, comment_text, comment_author, comment_date) VALUES (%s, %s, %s, %s, %s)"
        # Execute query
        cursor.execute(sql, (comments_data['Comment_ID'], comments_data['Video_Id'], comments_data['Comment_Text'], comments_data['Comment_Author'], comments_data['Comment_PublishedAt']))
        # Commit changes
        connection.commit()
        print("Comments data inserted into MySQL successfully.")
    except Exception as e:
        print("Error inserting comments data into MySQL:", e)

# Function to insert playlist details into MySQL database
def insert_playlist_data_mysql(connection, playlist_data):
    try:
        # Create MySQL cursor
        cursor = connection.cursor()
        # Construct SQL query
        sql = "INSERT INTO playlists (playlist_id, channel_id, playlist_name) VALUES (%s, %s, %s)"
        # Execute query
        cursor.execute(sql, (playlist_data['Playlist_ID'], playlist_data['Channel_Id'], playlist_data['Playlist_Title']))
        # Commit changes
        connection.commit()
        print("Playlist data inserted into MySQL successfully.")
    except Exception as e:
        print("Error inserting playlist data into MySQL:", e)

# Function to connect to YouTube API
def connect_to_youtube():
    return build("youtube", "v3", developerKey=api_key)

# Function to check MySQL connection
def check_mysql_connection():
    try:
        # Establish a connection to MySQL
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Rudraunsh_300119",
            database="youtube_data"
        )
        # Check if the connection is successful
        if connection.is_connected():
            print("MySQL connection established successfully.")
            # Close the connection
            connection.close()
            print("MySQL connection closed.")
    except mysql.connector.Error as e:
        print("Error connecting to MySQL:", e)

# Function to retrieve channel details from YouTube API
def get_channel_details(youtube, channel_id):
    # Make API request to retrieve channel details
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    response = request.execute()

    # Extract relevant channel data from API response
    channel_data = {
        'Channel_Name': response['items'][0]['snippet']['title'],
        'Channel_Id': response['items'][0]['id'],
        'Channel_Views': response['items'][0]['statistics']['viewCount'],
        'Channel_Description': response['items'][0]['snippet']['description'],
        'Channel_Status': response['items'][0]['snippet'].get('status', 'Not Available')
    }
    return channel_data



# Function to retrieve video details from YouTube API
def get_video_details(youtube, playlist_id, max_comments=10):
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=10
    )
    response = request.execute()

    videos = []
    if 'items' in response:
        for item in response['items']:
            video_id = item['snippet']['resourceId']['videoId']
            video_info = youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            ).execute()

            if 'items' in video_info and video_info['items']:
                video_data = video_info['items'][0]['snippet']
                statistics = video_info['items'][0]['statistics']
                content_details = video_info['items'][0]['contentDetails']

                video = {
                    'Video_Id': video_id,
                    'Video_Name': video_data.get('title', ''),
                    'Video_Description': video_data.get('description', ''),
                    'PublishedAt': video_data.get('publishedAt', ''),
                    'View_Count': statistics.get('viewCount', 0),
                    'Like_Count': statistics.get('likeCount', 0),
                    'Dislike_Count': statistics.get('dislikeCount', 0),
                    'Favorite_Count': statistics.get('favoriteCount', 0),
                    'Comment_Count': statistics.get('commentCount', 0),
                    'Duration': content_details.get('duration', ''),
                    'Thumbnail': video_data['thumbnails']['default']['url'],
                    'Caption_Status': content_details.get('caption', 'Not Available')
                }

                video['Comments'] = get_video_comments(youtube, video_id, max_comments)
                videos.append(video)

    return videos

# Function to retrieve comments for a video from YouTube API
def get_video_comments(youtube, video_id, max_comments=10):
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=max_comments  # Limit the number of comments retrieved
    )
    response = request.execute()

    comments = []
    for item in response['items']:
        comment = {
            'Comment_ID': item['id'],
            'Comment_Text': item['snippet']['topLevelComment']['snippet']['textDisplay'],
            'Comment_Author': item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
            'Comment_PublishedAt': item['snippet']['topLevelComment']['snippet']['publishedAt']
        }
        comments.append(comment)

    return comments

# Function to retrieve playlist details from YouTube API
def get_playlist_details(youtube, channel_id):
    # Make API request to retrieve playlist details
    request = youtube.playlists().list(
        part="snippet",
        channelId=channel_id,
        maxResults=10
    )
    response = request.execute()

    # Extract relevant playlist data from API response
    playlists = []
    for item in response.get('items', []):
        playlist = {
            'Playlist_Title': item['snippet']['title'],
            'Playlist_Description': item['snippet'].get('description', ''),
            'Playlist_PublishedAt': item['snippet']['publishedAt'],
            'Playlist_Thumbnail': item['snippet']['thumbnails']['default']['url'],
            'Playlist_ID': item['id'],
            'Channel_Id': channel_id
        }
        playlists.append(playlist)

    return playlists

# Streamlit UI
def main():
    st.title('YouTube Data')

    # Call the function to check the MySQL connection
    check_mysql_connection()

    # Input field for YouTube Channel ID
    channel_id = st.text_input('Enter YouTube Channel ID')

    # Button to retrieve data from YouTube API
    if st.button('Retrieve Data') and channel_id:
        # Connect to MongoDB
        db_mongodb = connect_to_mongodb()

        # Connect to MySQL
        connection_mysql = connect_to_mysql()

        # Connect to YouTube API
        youtube = connect_to_youtube()

        # Retrieve channel details
        channel_info = get_channel_details(youtube, channel_id)
        st.subheader('Channel Details')
        st.write(channel_info)

        # Insert channel data into MongoDB
        insert_channel_data_mongodb(db_mongodb, channel_info)

        # Insert channel data into MySQL
        insert_channel_data_mysql(connection_mysql, channel_info)

        # Retrieve playlist details
        playlists = get_playlist_details(youtube, channel_id)
        st.subheader('Playlists')
        for playlist in playlists:
            st.write('Playlist Title:', playlist['Playlist_Title'])
            st.write('Playlist Description:', playlist['Playlist_Description'])
            st.write('Published Date:', playlist['Playlist_PublishedAt'])
            st.image(playlist['Playlist_Thumbnail'], caption=playlist['Playlist_Title'], use_column_width=True)

            # Insert playlist data into MongoDB
            insert_playlist_data_mongodb(db_mongodb, playlist)

            # Insert playlist data into MySQL
            insert_playlist_data_mysql(connection_mysql, playlist)

            # Retrieve video details for each playlist
            videos = get_video_details(youtube, playlist['Playlist_ID'])
            st.subheader('Videos')
            for video in videos:
                st.write('Video ID:', video['Video_Id'])
                st.write('Video Name:', video['Video_Name'])
                st.write('Video Description:', video['Video_Description'])
                st.write('Published Date:', video['PublishedAt'])
                st.write('View Count:', video['View_Count'])
                st.write('Like Count:', video['Like_Count'])
                st.write('Dislike Count:', video['Dislike_Count'])
                st.write('Favorite Count:', video['Favorite_Count'])
                st.write('Comment Count:', video['Comment_Count'])
                st.write('Duration:', video['Duration'])
                st.write('Thumbnail URL:', video['Thumbnail'])
                st.write('Caption Status:', video['Caption_Status'])

                # Insert video data into MongoDB
                insert_video_data_mongodb(db_mongodb, video)

                # Insert video data into MySQL
                insert_video_data_mysql(connection_mysql, video)

                # Retrieve comments for the video
                comments = get_video_comments(youtube, video['Video_Id'])
                st.subheader('Comments')
                for comment in comments:
                    st.write('Comment ID:', comment['Comment_ID'])
                    st.write('Comment Text:', comment['Comment_Text'])
                    st.write('Comment Author:', comment['Comment_Author'])
                    st.write('Comment Published Date:', comment['Comment_PublishedAt'])

                    # Insert comments data into MongoDB
                    insert_comments_data_mongodb(db_mongodb, comment)

                    # Insert comments data into MySQL
                    insert_comments_data_mysql(connection_mysql, comment)

if __name__ == '__main__':
    main()



