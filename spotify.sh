#!/usr/bin/env /bin/bash

set -eu pipefail

# get library
#xh https://api.spotify.com/v1/me/tracks Authorization:"Bearer $access_token" | \
#    jq '.items[] | .track.id + " " + .track.name'

# "3xzxYEsDhcgA4dDGHC9Fdb Kabeera (feat. Harpreet Bachher)"
# "6eaG5icDNUUkB8yhtk4sED Ei Shohor Amar"
# "1TYCRLJFabBTEwGyRNgvUH A Simple Man"
# "6RCT5XYlsp0wvffcntgYHv Piya Daikho"
# "2r32XiAWtZbT3eLUvf4pag Jee Le Zaraa"
# "5bPEUVyCQEYdIscrGdiHj7 Bhebe Bhebe"
# "4GHuEO0gWcA05tBAdzjFmf Madno"
# "32JRVwx9Supn0wXkbVobrN Damadam Mast Kalandar"
# "414FqRxeG518IkFrmzdQjt Easy on Me"
# "2COO0bwU92d8hcJLdFCXCJ Utshorgo"
# "5mu5BVIOi28xIwgPiTf7m3 Dip Dip"
# "3ExLap1qHBI4f9bTfN5qk8 Tum Meri Ho"
# "2auw41vtv0Z5yffajkt0Mg Keya Ful"
# "5gIMagGznv2XQ8jidddEz1 Anek Durer Manush"
# "4t2i9pYjx9gWtGvPYEtvUl O Megh - The Dewarists, Season 4"
# "1ID8nD7o3Z7gtd8rsuof7F Chaudhary"
# "3v0Kj1WHvFJGFe12Q9PHNt Aaj Ei Akash Unplugged"
# "3vjkllvtOIKpVvXSWsu1ta Tu Hai"
# "4GXnjiHZm3YFFSbglMyY2p Majhe Majhe Tabo Dekha Pai"
# "3Ra219veylOqxYg9aSEq1E Fatema"

# get reommendations
#xh https://api.spotify.com/v1/recommendations\?seed_tracks\=1ID8nD7o3Z7gtd8rsuof7F Authorization:"Bearer $access_token" \
#    | jq '.tracks[] | .id + " " + .name'

#####
# download all library
rm spo_library.txt || true
touch spo_library.txt

xh https://api.spotify.com/v1/me/tracks\?limit=50 Authorization:"Bearer $access_token" | \
    jq -r '.items[] | .track.id + " " + .track.name' >> spo_library.txt

#xh https://api.spotify.com/v1/me/tracks\?limit=2 Authorization:"Bearer $access_token" | \
#    jq -r '.items[] | .track.id' | \
#    xargs -I{} xh https://api.spotify.com/v1/recommendations\?seed_tracks\={} Authorization:"Bearer $access_token" \
#    | jq -r '.tracks[] | .id + " " + .name' > spo_remommended.txt