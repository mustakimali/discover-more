# Spotfy Buddy

Find and recommend unique songs you've never listened before based on your favorite songs in Spotify library.

## Demo
```bash
# Get access token
# ----------------
# This opens the browser and asks you to give access to your spotify account
# when prompted (in your browser), return to terminal.
$ export access_token=$(./spotify.py token --quiet)

# Download you library to use as a seed to recommend new song
# saves as spo_library.tsv (by default)
$ ./spotify.py library

# Download all other playlists (so we know what to exclude from the recommendations)
# ----------------
# saved as spo_all_playlists.tsv
$ ./spotify.py list-playlists | awk '{print $1}' | xargs -I{} ./spotify.py get-playlist --id={} > spo_all_playlists.tsv

# Generate recommendations
# ----------------
# reads from spo_library.tsv (by default, param: --input)
# saved as spo_recs_all.tsv (by default, param: --output)
$ ./spotify.py recommend --exclude=spo_all_playlists.tsv

# Create playlist with the recommendations
# ----------------
# reads from spo_recs_all.tsv (by default, param: --input)
$ ./spotify.py create-playlist --name="My new favorites"

# check your spotify
```
