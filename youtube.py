# Importing the necessary libraries
from googleapiclient.discovery import build
import pymongo
import psycopg2
import pandas as pd
import streamlit as st


#API key connection
# Define a function to create a connection to the YouTube Data API
def Api_connect():
    # The API key to authenticate with Google services
    # Replace this with your actual Google Cloud API key
    Api_Id= "AIzaSyBNB-PdYM3B8PVmk8rYWhb0yfPedDUeJo0"

    # Define the service name and version to connect to
    api_service_name="youtube"      # The service to connect to (YouTube Data API)
    api_version="v3"                # The version of the API to use (v3 is the latest stable)

    # Create a client object to interact with the YouTube API
    # - `api_service_name`: The Google service you want to connect to
    # - `api_version`: The version of the Google service
    # - `developerKey`: Your Google Cloud API key for authentication
    youtube=build(api_service_name,api_version,developerKey=Api_Id)

    # Return the YouTube client object for further use
    return youtube

# Now create a YouTube API client by calling the function
youtube=Api_connect()

# The `youtube` object can be used to interact with the YouTube Data API.
# You can use this object to make API calls, such as fetching video information,
# listing channels, searching for content, and more.

#get channels information
# Define a function to get information about a specific YouTube channel
def get_channel_info(channel_id):
    # Create a request object to fetch details about the specified YouTube channel
    # - `part`: Specifies which parts of the channel's data to retrieve
    # - `id`: The ID of the channel to fetch information about
    request=youtube.channels().list(
                    part="snippet,ContentDetails,statistics",   # Data sections to include in the response
                    id=channel_id                               # The YouTube channel ID to look up
    )

    # Execute the request to get the channel information
    response=request.execute()      # This sends the request to the YouTube API and gets the response

    # The response is a dictionary with channel information
    # It contains an 'items' key with a list of channels (usually only one when fetching by ID)

    # Loop through each item in the response (even if there's typically only one)
    for i in response['items']:
        data=dict(Channel_Name=i["snippet"]["title"],                 # The name of the YouTube channel
                Channel_Id=i["id"],                                   # The YouTube channel's unique identifier
                Subscribers=i['statistics']['subscriberCount'],       # The number of subscribers
                Views=i["statistics"]["viewCount"],                   # The total number of views
                Total_Videos=i["statistics"]["videoCount"],           # The total number of videos
                Channel_Description=i["snippet"]["description"],      # Description of the channel
                Playlist_Id=i["contentDetails"]["relatedPlaylists"]["uploads"])  # ID of the uploads playlist
    return data  # Return the dictionary with the channel's details

#get video ids
# Define a function to get all video IDs from a YouTube channel
def get_videos_ids(channel_id):
    # Initialize an empty list to store video IDs
    video_ids=[]

    # Get the uploads playlist ID for the given channel
    response=youtube.channels().list(id=channel_id,     # The YouTube channel ID to look up                     
                                    part='contentDetails').execute()    # We need content details to get the uploads playlist ID
                                                                        # Execute the request to get channel details 
    # Retrieve the playlist ID where the channel's uploaded videos are stored
    Playlist_Id=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Variable to manage pagination when fetching playlist items
    next_page_token=None

    # Loop indefinitely to handle pagination
    while True:
        # Fetch the playlist items with a specific page token
        response1=youtube.playlistItems().list(
                                            part='snippet',             # We need snippet to get video-related information
                                            playlistId=Playlist_Id,     # The ID of the uploads playlist
                                            maxResults=50,              # The maximum number of results to fetch at once
                                            pageToken=next_page_token).execute() # Token for fetching the next page of result
        
        # Iterate through all items in the response
        for i in range(len(response1['items'])):
            # Get the video ID from the snippet's resourceId       
            video_ids.append(response1['items'][i]['snippet']['resourceId']['videoId']) # Add it to the list of video IDs
        next_page_token=response1.get('nextPageToken')      # Update the page token for pagination      

        # Break the loop if there are no more pages
        if next_page_token is None:
            break       # Exit the loop if there are no more pages to fetch
    return video_ids    # Return the complete list of video IDs

#get video information
# Define a function to get information about a list of YouTube videos
def get_video_info(video_ids):
    # Initialize an empty list to store video data
    video_data=[]

    # Loop through each video ID to fetch information
    for video_id in video_ids:
        # Create a request to get information about the specified video
        request=youtube.videos().list(
            part="snippet,ContentDetails,statistics",   # Retrieve specific parts of the video data
            id=video_id     # The video ID for which we're fetching information
        )

        # Execute the request to get the video information
        response=request.execute()  # This sends the request to the YouTube API

        # The response is a dictionary containing information about the video(s)
        # Iterate through the list of items in the response (typically just one video)
        for item in response["items"]:
            # Create a dictionary to store the extracted video information
            data=dict(Channel_Name=item['snippet']['channelTitle'],     # The channel's title
                    Channel_Id=item['snippet']['channelId'],            # The channel's ID
                    Video_Id=item['id'],                                # The video's unique ID
                    Title=item['snippet']['title'],                     # The video's title
                    Tags=item['snippet'].get('tags'),                   # Tags associated with the video (if any)
                    Thumbnail=item['snippet']['thumbnails']['default']['url'],  # The default thumbnail URL
                    Description=item['snippet'].get('description'),     # The video description (if available)
                    Published_Date=item['snippet']['publishedAt'],      # The publication date
                    Duration=item['contentDetails']['duration'],        # The video's duration in ISO 8601 format
                    Views=item['statistics'].get('viewCount'),          # Total view count (if available)
                    Likes=item['statistics'].get('likeCount'),          # Total like count (if available)
                    Comments=item['statistics'].get('commentCount'),    # Total comment count (if available)
                    Favorite_Count=item['statistics']['favoriteCount'], # The favorite count
                    Definition=item['contentDetails']['definition'],    # The video definition (HD or SD)
                    Caption_Status=item['contentDetails']['caption']    # Caption status (e.g., "true" for captions)
                    )
            video_data.append(data)     # Add the data dictionary to the list of video data    
    return video_data       # Return the list containing information about all the videos


#get comment information
# Define a function to get comment information for a list of YouTube videos
def get_comment_info(video_ids):
    # Initialize an empty list to store comment data
    Comment_data=[]
    # Use a try-except block to handle potential errors during API calls
    try:
        # Loop through each video ID to fetch its comments
        for video_id in video_ids:
            # Create a request to fetch comment threads for the given video
            request=youtube.commentThreads().list(
                part="snippet",     # We need snippet to get basic comment details
                videoId=video_id,   # The ID of the video to fetch comments for
                maxResults=50       # Maximum number of comments to fetch in one request
            )
            # Execute the request to get the comments
            response=request.execute()      # This sends the request to the YouTube Data API

            # The response contains a list of comment threads
            # Loop through each item (comment thread) in the response
            for item in response['items']:
                # Extract information about the top-level comment in the thread
                # Create a dictionary to store information about this comment
                data=dict(Comment_Id=item['snippet']['topLevelComment']['id'],      # The comment's unique ID
                        Video_Id=item['snippet']['topLevelComment']['snippet']['videoId'],  # The video ID where the comment was made
                        Comment_Text=item['snippet']['topLevelComment']['snippet']['textDisplay'],  # The text/content of the comment
                        Comment_Author=item['snippet']['topLevelComment']['snippet']['authorDisplayName'],  # The name of the comment's author
                        Comment_Published=item['snippet']['topLevelComment']['snippet']['publishedAt']) # The date/time the comment was published
                # Append this comment's data to the list of comment data
                Comment_data.append(data)
    # Handle any exceptions that occur during the process            
    except:
        pass                # This ensures that the program doesn't crash if an error occurs
    return Comment_data     # Return the list containing information about all fetched comments

#get_playlist_details
# Define a function to get all playlist details from a YouTube channel
def get_playlist_details(channel_id):
        # Variable to manage pagination through multiple pages of playlists
        next_page_token=None

        # List to store the collected playlist data
        All_data=[]

        # Loop to fetch all playlists, handling pagination
        while True:
                # Create a request to fetch playlists for the specified channel
                request=youtube.playlists().list(
                        part='snippet,contentDetails',      # Sections to include in the response
                        channelId=channel_id,               # The YouTube channel ID to fetch playlists for
                        maxResults=50,                      # Maximum number of playlists to fetch at once
                        pageToken=next_page_token           # Token to fetch the next page of results
                )
                # Execute the request to get the playlists
                response=request.execute()      # Sends the request to the YouTube Data API
                # Loop through each playlist item in the response
                for item in response['items']:
                        # Create a dictionary with key details about each playlist
                        data=dict(Playlist_Id=item['id'],       # The unique ID for the playlist
                                Title=item['snippet']['title'], # The playlist's title
                                Channel_Id=item['snippet']['channelId'],    # The ID of the channel that owns the playlist
                                Channel_Name=item['snippet']['channelTitle'],   # The name of the channel
                                PublishedAt=item['snippet']['publishedAt'],     #The publication date of the playlist
                                Video_Count=item['contentDetails']['itemCount'])    # The number of videos in the playlist
                        # Add the dictionary to the list of collected playlist data
                        All_data.append(data)

                # Update the pagination token for the next request
                next_page_token=response.get('nextPageToken')

                # Break the loop if there's no next page
                if next_page_token is None:
                        break   # Exit the loop when all playlists have been fetched
        return All_data         # Return the list containing information about all the fetched playlists


#upload to mongoDB
# Connect to a MongoDB cluster using a connection string
client=pymongo.MongoClient("mongodb+srv://Bhavana:Nanu_300119@cluster0.qvrvp1a.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
# Access a specific database in the MongoDB cluster
db=client["YoutubeDataHarvesting"]

# Define a function to fetch and store channel-related details in MongoDB
def channel_details(channel_id):
    # Fetch channel information based on the channel ID
    ch_details=get_channel_info(channel_id)     # Get basic channel information
    # Fetch playlist details associated with the channel
    pl_details=get_playlist_details(channel_id) # Get all playlists in the channel
    # Fetch video IDs from the channel
    vi_ids=get_videos_ids(channel_id)       # Get all video IDs for the channel
    # Fetch detailed information about the videos in the channel
    vi_details=get_video_info(vi_ids)       # Get details for each video
    # Fetch comment information for all videos in the channel
    com_details=get_comment_info(vi_ids)    # Get top-level comments for all videos

    # Access a specific collection in the MongoDB database
    coll1=db["channel_details"]     # This collection stores channel-related data
    # Insert the gathered information into MongoDB as a new document
    coll1.insert_one({"channel_information":ch_details,"playlist_information":pl_details,   # Insert channel information, Insert playlist details
                      "video_information":vi_details,"comment_information":com_details})    # Insert video details, Insert comment details
    
    # Return a success message upon completion of the upload
    return "upload completed successfully"


#Table creation for channels,playlists,videos,comments
# Define a function to create a table for storing channel information
def channels_table(channel_name_s):
    # Connect to a PostgreSQL database
    mydb=psycopg2.connect(host="localhost",         # The database server's hostname
                        user="postgres",            # The username for authentication
                        password="Nanu_300119",     # The password for authentication
                        database="YoutubeDataHarvesting",       # The database name 
                        port="5432")                # The port number for PostgreSQL
    # Create a cursor object for executing SQL commands
    cursor=mydb.cursor()

    try:
        # Define the SQL query to create a table for channel information
        create_query='''create table if not exists channels(Channel_Name varchar(100),      
                                                            Channel_Id varchar(80) primary key,
                                                            Subscribers bigint,
                                                            Views bigint,
                                                            Total_Videos int,
                                                            Channel_Description text,
                                                            Playlist_Id varchar(80))'''
        # Execute the SQL query to create the table
        cursor.execute(create_query)
        # Commit the transaction to ensure the table is created
        mydb.commit()

    except:
        # Handle any exceptions that occur during table creation
        print("Channels table already created") # Log a message if there's an error

    #fetching all datas
    # Fetch all records from the "channels" table in PostgreSQL
    query_1= "SELECT * FROM channels"   # SQL query to fetch all records from the "channels" table
    cursor.execute(query_1)             # Execute the query to retrieve all records from the table
    table= cursor.fetchall()            # Fetch all results returned by the query
    mydb.commit()                       # Commit the transaction to ensure the data retrieval is complete and consistent

    # Lists to hold channel names
    chann_list= []      # Initialize an empty list to hold the first column from the DataFrame 
    chann_list2= []     # Initialize an empty list to store channel names

    # Convert the fetched results into a pandas DataFrame
    df_all_channels= pd.DataFrame(table)    # Create a DataFrame from the fetched results

    # Append the first column of the DataFrame to chann_list
    chann_list.append(df_all_channels[0])   # Assuming the first column contains channel names

    # Iterate over the first column of the DataFrame and add its items to chann_list2       
    for i in chann_list[0]:     # Iterate over all items in the first column of the DataFrame
        chann_list2.append(i)   # Add each item to chann_list2 
    
    # Check if the provided channel name exists in the list of channel names
    if channel_name_s in chann_list2:       # If the provided channel name is already in chann_list2
        news= f"Your Provided Channel {channel_name_s} is Already exists"   # Create a message indicating it exists        
        return news # Return the message, no further action required
    
    else:   # If the channel name does not exist in the list

        single_channel_details= []      # Initialize a list to hold channel information from MongoDB

        # Access the "channel_details" collection from MongoDB
        coll1=db["channel_details"]     # MongoDB collection to fetch channel details
        for ch_data in coll1.find({"channel_information.Channel_Name":channel_name_s},{"_id":0}): # Query to find the specific channel name,# Exclude the MongoDB document ID
            single_channel_details.append(ch_data["channel_information"])   # Add the information to the list

        # Convert the fetched channel information into a pandas DataFram
        df_single_channel= pd.DataFrame(single_channel_details)


        # Insert channel details into PostgreSQL if they don't already exist
        for index,row in df_single_channel.iterrows():          # Iterate over each row in the DataFrame
            insert_query='''insert into channels(Channel_Name ,
                                                Channel_Id,
                                                Subscribers,
                                                Views,
                                                Total_Videos,
                                                Channel_Description,
                                                Playlist_Id)
                                                
                                                values(%s,%s,%s,%s,%s,%s,%s)''' # SQL query to insert data into the "channels" table
            # Tuple containing the values to insert
            values=(row['Channel_Name'],
                    row['Channel_Id'],
                    row['Subscribers'],
                    row['Views'],
                    row['Total_Videos'],
                    row['Channel_Description'],
                    row['Playlist_Id'])

            try:
                # Try inserting the data into PostgreSQL
                cursor.execute(insert_query,values)     # Execute the insert query
                mydb.commit()       # Commit the transaction to save the changes       

            except:
                # Handle any errors during the insert operation
                print("Channel values are already inserted")    # Log an error message         

#Table creation for playlists
# Function to create the 'playlists' table and insert playlist data
def playlist_table(channel_name_s):
    # Connect to PostgreSQL database
    mydb=psycopg2.connect(host="localhost",     # Database server hostname
                        user="postgres",        # PostgreSQL username
                        password="Nanu_300119", # PostgreSQL password (make sure to replace with secure data)
                        database="YoutubeDataHarvesting",   # Name of the database to connect to    
                        port="5432")    # Port used by PostgreSQL
    # Create a cursor object to execute SQL queries
    cursor=mydb.cursor()    # Cursor for executing SQL statements

    # Create the 'playlists' table if it doesn't already exist
    create_query='''create table if not exists playlists(Playlist_Id varchar(100) primary key,
                                                        Title varchar(100),
                                                        Channel_Id varchar(100),
                                                        Channel_Name varchar(100),
                                                        PublishedAt timestamp,
                                                        Video_Count int
                                                        )'''
     # Execute the table creation query
    cursor.execute(create_query)    # Create the table if it doesn't exist
    mydb.commit()   # Commit the transaction to ensure the table is created

    # Fetching the relevant playlist information from MongoDB
    single_channel_details= []      # Initialize an empty list to store playlist information
    coll1=db["channel_details"]     # MongoDB collection that contains channel-related information

    # Retrieve the playlist information for the specified channel
    # Find documents with matching channel name
    # Exclude the MongoDB document ID from the result
    for ch_data in coll1.find({"channel_information.Channel_Name":channel_name_s},{"_id":0}):   
        # Add the playlist information to the list
        single_channel_details.append(ch_data["playlist_information"])

    # Convert the first set of playlist information to a pandas DataFrame
    df_single_channel= pd.DataFrame(single_channel_details[0])  # Convert the first playlist info to a DataFrame

    # Insert the playlist details into the 'playlists' table in PostgreSQL
    for index,row in df_single_channel.iterrows():  # Iterate over each row in the DataFrame
        # SQL query to insert playlist information into the PostgreSQL table
        insert_query='''insert into playlists(Playlist_Id,
                                            Title,
                                            Channel_Id,
                                            Channel_Name,
                                            PublishedAt,
                                            Video_Count
                                            )
                                            
                                            values(%s,%s,%s,%s,%s,%s)'''    # SQL query for inserting data into the table
        # Values to insert into the table
        values=(row['Playlist_Id'],     # Playlist ID
                row['Title'],           # Playlist title
                row['Channel_Id'],      # Channel ID
                row['Channel_Name'],    # Channel name
                row['PublishedAt'],     # Publish timestamp
                row['Video_Count']      # Number of videos in the playlist
                )

        # Execute the insert query with the specified values
        cursor.execute(insert_query,values) # Insert the row into the PostgreSQL table
        mydb.commit()       # Commit the transaction to ensure changes are permanent


#Table creation for videos
# Function to create a PostgreSQL table for video details and insert video data
def videos_table(channel_name_s):
    # Connect to PostgreSQL
    mydb=psycopg2.connect(host="localhost",     # Hostname for the PostgreSQL server
                        user="postgres",        # Username for PostgreSQL
                        password="Nanu_300119", # Password for PostgreSQL (ensure it's secure)
                        database="YoutubeDataHarvesting",   # Database name
                        port="5432")    # Port for PostgreSQL
    # Create a cursor for executing SQL queries
    cursor=mydb.cursor()        # Create cursor object for executing SQL

    # Create a table for videos if it doesn't already exist
    create_query='''create table if not exists videos(Channel_Name varchar(100),
                                                    Channel_Id varchar(100),
                                                    Video_Id varchar(30) primary key,
                                                    Title varchar(150),
                                                    Tags text,
                                                    Thumbnail varchar(200),
                                                    Description text,
                                                    Published_Date timestamp,
                                                    Duration interval,
                                                    Views bigint,
                                                    Likes bigint,
                                                    Comments int,
                                                    Favorite_Count int,
                                                    Definition varchar(10),
                                                    Caption_Status varchar(50)
                                                        )'''

    # Execute the table creation query
    cursor.execute(create_query)        # Execute the query to create the table if it doesn't exist
    mydb.commit()       # Commit the transaction to ensure changes are applied

    # Fetch video information from MongoDB
    single_channel_details= []      # List to store video information
    coll1=db["channel_details"]     # MongoDB collection with channel-related information

    # Find video information for the specified channel in MongoDB
    # Query to find the specified channel
    for ch_data in coll1.find({"channel_information.Channel_Name":channel_name_s},{"_id":0}):   # Exclude the MongoDB document ID
        # Add the video information to the list
        single_channel_details.append(ch_data["video_information"])
    # Convert the video information into a pandas DataFrame
    df_single_channel= pd.DataFrame(single_channel_details[0])  # Convert the first set of video information to a DataFrame


     # Insert the video details into the PostgreSQL table
    for index,row in df_single_channel.iterrows():  # Iterate over each row in the DataFrame
            # SQL query for inserting video information into the PostgreSQL table
            insert_query='''insert into videos(Channel_Name,
                                                    Channel_Id,
                                                    Video_Id,
                                                    Title,
                                                    Tags,
                                                    Thumbnail,
                                                    Description,
                                                    Published_Date,
                                                    Duration,
                                                    Views,
                                                    Likes,
                                                    Comments,
                                                    Favorite_Count,
                                                    Definition,
                                                    Caption_Status
                                                )
                                                
                                                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        
            # Values to insert into the table, extracted from each row of the DataFrame
            values=(row['Channel_Name'],        # Channel name
                    row['Channel_Id'],          # Channel ID
                    row['Video_Id'],            # Video ID
                    row['Title'],               # Title of the video
                    row['Tags'],                # Tags associated with the video
                    row['Thumbnail'],           # Thumbnail URL
                    row['Description'],         # Description of the video
                    row['Published_Date'],      # Date and time of publication
                    row['Duration'],            # Duration of the video
                    row['Views'],               # View count
                    row['Likes'],               # Likes count
                    row['Comments'],            # Comments count
                    row['Favorite_Count'],      # Favorite count
                    row['Definition'],          # Video quality
                    row['Caption_Status']       # Status of captions
                    )

            # Execute the insertion query with the specified values
            cursor.execute(insert_query,values)     # Insert the video information into the PostgreSQL table
            mydb.commit()       # Commit the transaction to ensure the insertion is saved

#Table creation for comments
# Function to create and populate the comments table
def comments_table(channel_name_s):
    # Establish a connection to the PostgreSQL database
    mydb=psycopg2.connect(host="localhost",     # Database host         
                        user="postgres",        # Database user   
                        password="Nanu_300119", # Database user's password    
                        database="YoutubeDataHarvesting",   # Database name
                        port="5432")    # Port number
    # Create a cursor object to interact with the database
    cursor=mydb.cursor()    

    # SQL query to create the 'comments' table if it doesn't exist
    create_query='''create table if not exists comments(Comment_Id varchar(100) primary key,
                                                        Video_Id varchar(50),
                                                        Comment_Text text,
                                                        Comment_Author varchar(150),
                                                        Comment_Published timestamp
                                                        )'''
    
    # Execute the create table query
    cursor.execute(create_query)    
    mydb.commit()       # Commit the changes to the database

    # List to store comment details for a single channel
    single_channel_details= []    
    # Assuming there's a MongoDB connection, get the collection named 'channel_details'
    # Here, 'db' is assumed to be a predefined MongoDB client connection  
    coll1=db["channel_details"]
   
    # Fetch data from the 'channel_details' collection, filtering by the given channel name
    # Only include the 'comment_information' and exclude the MongoDB ID field
    for ch_data in coll1.find({"channel_information.Channel_Name":channel_name_s},{"_id":0}): 
        # Append the comment information to the list  
        single_channel_details.append(ch_data["comment_information"])

    # Create a DataFrame from the first (and only) element in the single_channel_details list
    df_single_channel= pd.DataFrame(single_channel_details[0])  

    # Loop over each row in the DataFrame to insert comments into the 'comments' table
    for index,row in df_single_channel.iterrows():    
           # SQL query to insert a new record into the 'comments' table
            insert_query='''insert into comments(Comment_Id,
                                                    Video_Id,
                                                    Comment_Text,
                                                    Comment_Author,
                                                    Comment_Published
                                                )
                                                
                                                values(%s,%s,%s,%s,%s)'''
            
           # Values to be inserted into the 'comments' table
            values=(row['Comment_Id'],          # Comment ID
                    row['Video_Id'],            # Associated video ID
                    row['Comment_Text'],        # Text of the comment
                    row['Comment_Author'],      # Author of the comment
                    row['Comment_Published']    # Timestamp of publication
                    )

            # Execute the insert query with the given values
            cursor.execute(insert_query,values)
            # Commit the changes to the database
            mydb.commit()

# Function to create or update various tables based on channel name
def tables(channel_name):
    # Check if the channel already has an entry in the 'channels_table'
    news= channels_table(channel_name)
    if news:
        # If a record is found, output the details
        st.write(news)
    else:
        # If no record is found, create other tables for the given channel
        playlist_table(channel_name)       # Create or update the playlist table
        videos_table(channel_name)         # Create or update the videos table
        comments_table(channel_name)       # Create or update the comments table

    return "Tables Created Successfully"   # Return a success message

# Function to display the existing 'channels' table
def show_channels_table():
    ch_list=[]      # List to store channel information
    db=client["YoutubeDataHarvesting"]      # Connect to the 'YoutubeDataHarvesting' database
    coll1=db["channel_details"]     # Access the 'channel_details' collection   
    # Retrieve all 'channel_information' from the collection  
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_list.append(ch_data["channel_information"])      # Add to the list
    df=st.dataframe(ch_list)        # Display the list as a DataFrame in Streamlit

    return df       # Return the DataFrame

# Function to display the existing 'playlists' table
def show_playlists_table():
    pl_list=[]      # List to store playlist information
    db=client["YoutubeDataHarvesting"]      # Connect to the 'YoutubeDataHarvesting' database
    coll1=db["channel_details"]             # Access the 'channel_details' collection
    # Retrieve all 'playlist_information' from the collection
    for pl_data in coll1.find({},{"_id":0,"playlist_information":1}):
        # Iterate over the list of playlists within each document
        for i in range(len(pl_data["playlist_information"])):
            pl_list.append(pl_data["playlist_information"][i])  # Add to the list
    df1=st.dataframe(pl_list)       # Display the list as a DataFrame in Streamlit

    return df1      # Return the DataFrame

# Function to display the existing 'videos' table
def show_videos_table():
    vi_list=[]    # List to store video information
    db=client["YoutubeDataHarvesting"]      # Connect to the 'YoutubeDataHarvesting' database
    coll1=db["channel_details"]     # Access the 'channel_details' collection
    # Retrieve all 'video_information' from the collection
    for vi_data in coll1.find({},{"_id":0,"video_information":1}):
        # Iterate over the list of videos within each document
        for i in range(len(vi_data["video_information"])):
            vi_list.append(vi_data["video_information"][i])     # Add to the list
    df2=st.dataframe(vi_list)       # Display the list as a DataFrame in Streamlit

    return df2      # Return the DataFrame

# Function to display the existing 'comments' table
def show_comments_table():
    com_list=[]     # List to store comment information
    db=client["YoutubeDataHarvesting"]      # Connect to the 'YoutubeDataHarvesting' database
    coll1=db["channel_details"]             # Access the 'channel_details' collection
    # Retrieve all 'comment_information' from the collection
    for com_data in coll1.find({},{"_id":0,"comment_information":1}):
        # Iterate over the list of comments within each document
        for i in range(len(com_data["comment_information"])):
            com_list.append(com_data["comment_information"][i])     # Add to the list
    df3=st.dataframe(com_list)      # Display the list as a DataFrame in Streamlit

    return df3      # Return the DataFrame

#streamlit part
# Sidebar with information and interactive input
with st.sidebar:
    st.title(":red[YOUTUBE DATA HAVERSTING AND WAREHOUSING]")   # Sidebar title
    st.header("Skill Take Away")    # Sidebar header
    st.caption("Python Scripting")  # List of skills
    st.caption("Data Collection")
    st.caption("MongoDB")
    st.caption("API Integration")
    st.caption("Data Management using MongoDB and SQL")

# Text input to collect a YouTube channel ID from the user
channel_id=st.text_input("Enter the channel ID")

# Button to trigger data collection and storage
if st.button("collect and store data"):
    # List to store existing channel IDs from MongoDB
    ch_ids=[]
    # Connect to the MongoDB database
    db=client["YoutubeDataHarvesting"]
    # Access the 'channel_details' collection
    coll1=db["channel_details"]
    # Retrieve all channel IDs in the collection
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_ids.append(ch_data["channel_information"]["Channel_Id"])

    #Check if the entered channel ID already exists in the collection
    if channel_id in ch_ids:
        st.success("Channel Details of the given channel id already exists")    # Display success message

    else:
        # If the channel ID doesn't exist, call a function to insert new data
        insert=channel_details(channel_id)      # Function to collect and store channel details
        st.success(insert)      # Display success message

#New code
# New code for channel selection and SQL migration
all_channels= []
# Retrieve all unique channel names from the MongoDB collection
coll1=db["channel_details"]
for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
    all_channels.append(ch_data["channel_information"]["Channel_Name"])

# Dropdown (selectbox) to select a specific channel   
unique_channel= st.selectbox("Select the Channel",all_channels)

# Button to trigger migration to SQL
if st.button("Migrate to Sql"):
    # Call the function to create or update SQL tables for the selected channel
    Table=tables(unique_channel)
    st.success(Table)       # Display success message

# Radio button to select which table to view
show_table=st.radio("SELECT THE TABLE FOR VIEW",("CHANNELS","PLAYLISTS","VIDEOS","COMMENTS"))

# Show the selected table based on user input
if show_table=="CHANNELS":
    show_channels_table()   # Display the 'channels' table

elif show_table=="PLAYLISTS":
    show_playlists_table()  # Display the 'playlists' table      

elif show_table=="VIDEOS":
    show_videos_table()     # Display the 'videos' table

elif show_table=="COMMENTS":
    show_comments_table()   # Display the 'comments' table

#SQL Connection
# Establish a connection to the PostgreSQL database
mydb=psycopg2.connect(host="localhost",     # Host where the database is running
                    user="postgres",        # Database user
                    password="Nanu_300119", # User's password
                    database="YoutubeDataHarvesting",      # Database name
                    port="5432")    # Port for PostgreSQL
cursor=mydb.cursor()    # Create a cursor for executing SQL queries

# Create a Streamlit select box to choose a question to answer
question=st.selectbox("Select your question",("1. All the videos and the channel name",
                                              "2. channels with most number of videos",
                                              "3. 10 most viewed videos",
                                              "4. comments in each videos",
                                              "5. Videos with higest likes",
                                              "6. likes of all videos",
                                              "7. views of each channel",
                                              "8. videos published in the year of 2022",
                                              "9. average duration of all videos in each channel",
                                              "10. videos with highest number of comments"))

# Check which question was selected and execute the corresponding SQL query
if question=="1. All the videos and the channel name":
    # Query to get all videos and their channel names
    query1='''select title as videos,channel_name as channelname from videos'''
    cursor.execute(query1)  # Execute the query
    mydb.commit()   # Commit the transaction
    t1=cursor.fetchall()    # Fetch all results
    # Create a DataFrame with the query results
    df=pd.DataFrame(t1,columns=["video title","channel name"])
    st.write(df)     # Display the DataFrame in Streamlit

elif question=="2. channels with most number of videos":
    # Query to get channels and the count of their videos, ordered by video count
    query2='''select channel_name as channelname,total_videos as no_videos from channels 
                order by total_videos desc'''
    cursor.execute(query2)
    mydb.commit()
    t2=cursor.fetchall()
    df2=pd.DataFrame(t2,columns=["channel name","No of videos"])
    st.write(df2)

elif question=="3. 10 most viewed videos":
    # Query to get the top 10 most viewed videos with their channel names and titles
    query3='''select views as views,channel_name as channelname,title as videotitle from videos 
                where views is not null order by views desc limit 10'''
    cursor.execute(query3)
    mydb.commit()
    t3=cursor.fetchall()
    df3=pd.DataFrame(t3,columns=["views","channel name","videotitle"])
    st.write(df3)

elif question=="4. comments in each videos":
    # Query to get the number of comments for each video
    query4='''select comments as no_comments,title as videotitle from videos where comments is not null'''
    cursor.execute(query4)
    mydb.commit()
    t4=cursor.fetchall()
    df4=pd.DataFrame(t4,columns=["no of comments","videotitle"])
    st.write(df4)

elif question=="5. Videos with higest likes":
    # Query to get the videos with the most likes
    query5='''select title as videotitle,channel_name as channelname,likes as likecount
                from videos where likes is not null order by likes desc'''
    cursor.execute(query5)
    mydb.commit()
    t5=cursor.fetchall()
    df5=pd.DataFrame(t5,columns=["videotitle","channelname","likecount"])
    st.write(df5)

elif question=="6. likes of all videos":
    # Query to get the like count for all videos
    query6='''select likes as likecount,title as videotitle from videos'''
    cursor.execute(query6)
    mydb.commit()
    t6=cursor.fetchall()
    df6=pd.DataFrame(t6,columns=["likecount","videotitle"])
    st.write(df6)

elif question=="7. views of each channel":
    # Query to get the total views for each channel
    query7='''select channel_name as channelname ,views as totalviews from channels'''
    cursor.execute(query7)
    mydb.commit()
    t7=cursor.fetchall()
    df7=pd.DataFrame(t7,columns=["channel name","totalviews"])
    st.write(df7)

elif question=="8. videos published in the year of 2022":
    # Query to get videos published in 2022
    query8='''select title as video_title,published_date as videorelease,channel_name as channelname from videos
                where extract(year from published_date)=2022'''
    cursor.execute(query8)
    mydb.commit()
    t8=cursor.fetchall()
    df8=pd.DataFrame(t8,columns=["videotitle","published_date","channelname"])
    st.write(df8)

elif question=="9. average duration of all videos in each channel":
    # Query to get the average duration of videos in each channel
    query9='''select channel_name as channelname,AVG(duration) as averageduration from videos group by channel_name'''
    cursor.execute(query9)
    mydb.commit()
    t9=cursor.fetchall()
    df9=pd.DataFrame(t9,columns=["channelname","averageduration"])

    # Converting averageduration to a string for better display
    T9=[]
    for index,row in df9.iterrows():
        channel_title=row["channelname"]
        average_duration=row["averageduration"]
        average_duration_str=str(average_duration)      # Convert duration to string
        T9.append(dict(channeltitle=channel_title,avgduration=average_duration_str))
    df1=pd.DataFrame(T9)
    st.write(df1)

elif question=="10. videos with highest number of comments":
    # Query to get the videos with the most comments
    query10='''select title as videotitle, channel_name as channelname,comments as comments from videos where comments is
                not null order by comments desc'''
    cursor.execute(query10)
    mydb.commit()
    t10=cursor.fetchall()
    df10=pd.DataFrame(t10,columns=["video title","channel name","comments"])
    st.write(df10)