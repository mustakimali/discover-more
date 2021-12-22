# Spotfy Buddy

Find and recommend unique songs you've never listened before based on your favorite songs in Spotify library.

## Demo
```bash
# Get access token
$ ./spotify.py token

# this opens the browser and asks you to give access to your spotify account
# when prompted (in your browser), return to terminal and run the command
# displayed that looks like this. (It's also copied into your clipboard)
# export access_token="{token_from_spotify}"

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