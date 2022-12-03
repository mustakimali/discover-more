# Discover More

Find and recommend unique songs you've never listened before based on your favorite songs in Spotify library.

## Demo
A quick demo is prepared that creates a playlist named `My new favorites` with unique songs based on your liked songs.

This exludes any songs you have in any of your playlists, therefore you'll more likely get lots of new songs to enjoy.

```bash
./demo
```
## How to use?
Check [demo](demo) for examples.

### Generate a new playlist based on an existing playlist

Without the songs you already like (in your library.)


```bash
# set up token, if not already set
./discover-more token

# find the ID of the playlist you like
./discover-more list-playlists | grep "<playlist title>"

# get the id from the output
./discover-more get-playlist --id={PLAYLIST_ID} > spo_input.tsv

# get your liked songs (so they can be excluded from the recommendation)
./discover-more get-library

# generate recommendation
./discover-more recommend --exclude spo_library.tsv --input spo_input.tsv

# create playlist based on the new recommendation
./discover-more create-playlist --input spo_recommendations_top.tsv --name "My new playlist"

# now look for the new playlist in spotify
```
