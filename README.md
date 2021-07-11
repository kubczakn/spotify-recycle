# Spotify Recycle Bin
Flask application that uses the Spotipy library to recover tracks deleted by a user based on his or her last use of the application.
# Getting Started
To start recycling songs, hit recycle. First use of recycle will create a record of the contents of your public playlists that can be used to recover lost tracks in future uses of the application.  
  
A "Recycle Bin" playlist will also be created to store these recycled tracks if the playlist doesn't already exist.
# Usage
Hitting recycle will compare your current public playlist contents to our record for your account. For each playlist in our record that exists in your current playlist, each track that is in the record but isn't in your current playlist is added to the recycle bin.  
  
Afterwards our record is updated to reflect the contents of your current playlists.  
