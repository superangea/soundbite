# soundBite
SoundBite finds and plays the "best" 30 seconds of a song according to listeners' comments. Useful for discovering new music on SoundCloud by quickly determining if a song is to your taste or not. 

Why?  
SoundCloud allows listeners to comment on a song at the exact time they want to. Most people don't bother to comment on a song 
unless they really enjoy it, which makes the data fairly accurate.  

Methodology  
Each comment on a SoundCloud track has a timestamp to the exact second in the song in which the user places his/her cursor on the comment box to make a comment. Using the timestamps of all the comments, I could find peaks in the data where the most people commented.  