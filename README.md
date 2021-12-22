# Spotfy Buddy

Find and recommend unique songs you've never listened before based on your favorite songs in Spotify library.

## Demo
```bash
# Get access token
# 1. Goto: https://developer.spotify.com/console/post-playlists/
# 2. Click: GET TOKEN
# 3. Tick both scopes at the top (playlist-modify-public, playlist-modify-private)
# 4. Requst Token, and copy the access token

# Export the access token
$ export access_token="...."

# Download you library to use as a seed to recommend new song
# saves as spo_library.tsv (by default)
$ ./spotify.py library

# Download all other playlists (so we know what to exclude from the recommendataion)
# saved as spo_all_playlists.tsv
$ ./spotify.py list-playlists | awk '{print $1}' | xargs -I{} ./spotify.py get-playlist --id={} > spo_all_playlists.tsv

# Generate recommendation
# reads from spo_library.tsv (by default, param: --input)
# saved as spo_recs_all.tsv (by default, param: --output)
$ ./spotify.py recommend --exclude=spo_all_playlists.tsv

# create playlist with the recommendataion
# reads from spo_recs_all.tsv (by default, param: --input)
$ ./spotify.py create-playlist --name={NAME}

# check your spotify
```

## Get all playlists
Useful to use as exclude list in recommendation

```bash
$ export access_token="...."
$ ./spotify.py list-playlists | awk '{print $1}' | xargs -I{} ./spotify.py get-playlist --id={} > spo_all_playlists.tsv
```