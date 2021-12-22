#!/usr/bin/env /usr/bin/python3

import os
import sys
import requests
import json
import argparse
from datetime import datetime
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import re

# https://developer.spotify.com/documentation/web-api/reference/#/operations/get-recommendations
# https://developer.spotify.com/console/library/


def delete_file(fpath):
    if os.path.exists(fpath):
        os.remove(fpath)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def ensure_exist(fpath):
    if os.path.exists(fpath) == False:
        eprint(f"File does not exist: {fpath}")
        exit(3)


def get_access_token():
    token = os.getenv("access_token")
    if token == None or token == "":
        eprint("Must set access_token env variable")
        exit(1)
    return token


def spotify_api_call(path, params=None):
    access_token = get_access_token()

    path = f"https://api.spotify.com/{path}"
    rsp = None

    if params == None:
        # get
        rsp = requests.get(
            path,
            headers={"Authorization": f"Bearer {access_token}"},
        )
    else:
        # post
        rsp = requests.post(
            path, json=params, headers={"Authorization": f"Bearer {access_token}"}
        )

    if rsp.status_code >= 300:
        eprint(
            f"Invalid status code from spotify [{path}]: {rsp.status_code}\n{rsp.text}"
        )
        return None, None

    return (json.loads(rsp.text), rsp.text)


# ------------------------------------------------------------


def handle_load_recommendataion(infile, outfile, exclude=None):
    def load_file(fpath, dest_hashmap, dest_ids=None):
        f = open(fpath, "r")

        titles = []
        ids = []
        for line in f.readlines():
            if line.startswith("#"):
                continue

            parts = line.split("\t")
            if len(parts) < 2:
                continue
            id = parts[0]
            title = parts[1].strip()
            titles.append(title)
            ids.append(id)

        f.close()

        print(f"Loading {len(ids)} tracks from {fpath}...")
        for i in range(0, len(ids)):
            id = ids[i]
            title = titles[i]

            dest_hashmap[id] = title
            dest_hashmap[title] = id  # make sure song with same title is excluded
            if dest_ids != None:
                dest_ids.append(id)

    print(f"Generating recommendations from {infile} to {outfile}")
    # load library
    if os.path.exists(infile) == False:
        handle_load_library(infile)

    # load library into memory
    exclude_tracks_hm = (
        {}
    )  # hashmap for quick lookup if a track is already loaded, library is already included
    seed_ids = []  # the ids used as seed for recommendataion

    # load seeds
    load_file(infile, exclude_tracks_hm, seed_ids)
    exclude_ids = seed_ids

    # load exclude lists (if any)
    if exclude != None:
        paths = exclude.split(",")
        for path in paths:
            load_file(path, exclude_tracks_hm, None)  # None - to not used them as seed

    print(
        f"Generating recommendation based on {len(seed_ids)}s and {len(exclude_tracks_hm)} excluded tracks..."
    )
    # download recommendataion
    delete_file(outfile)
    rec_file = open(outfile, "a")
    # header
    rec_file.write("# id\ttitle\tartist_name\talbum_name\tpopularity\n")
    i = 0
    while i < len(seed_ids):
        print(f"Loading recommmendations {i}/{len(seed_ids)}...", end="")

        ids = ",".join(map(lambda x: (x), seed_ids[i : i + 5]))

        # get recommendation
        (resp, raw) = spotify_api_call(
            f"v1/recommendations?limit=100&seed_tracks={ids}"
        )
        if resp == None:
            continue

        tracks = resp["tracks"]
        num_added = 0
        num_skipped = 0
        for item in tracks:
            id = item["id"]
            title = item["name"]
            album_name = item["album"]["name"]
            artist_name = item["artists"][0]["name"]
            popularity = item["popularity"]

            if (
                exclude_tracks_hm.__contains__(id) == False
                and exclude_tracks_hm.__contains__(title) == False
            ):
                num_added += 1
                rec_file.write(
                    f"{id}\t{title}\t{artist_name}\t{album_name}\t{popularity}\n"
                )
                exclude_tracks_hm[id] = title
            else:
                num_skipped += 1

        print(f": {num_added} added, {num_skipped} skipped.")

        i += 5

    rec_file.close()
    print("Sorting")

    os.system(
        f"cat {outfile} | (sed -u 1q; sort -nrk 5 -t '\t') > {outfile}_sorted.tsv"
    )
    os.system(f"mv {outfile}_sorted.tsv {outfile}")

    print("Done")


def handle_load_library(ofile):

    delete_file(ofile)

    library_file = open(ofile, "a")
    # header
    library_file.write("# id\ttitle\tartist_name\talbum_name\n")
    offset = 0

    while True:
        print(f"Downloading library (offset: {offset})")
        (resp, raw) = spotify_api_call(f"v1/me/tracks?limit=50&offset={offset}")
        if resp == None:
            break

        tracks = resp["items"]

        if len(tracks) == 0:
            break

        for item in tracks:
            track = item["track"]
            id = track["id"]
            title = track["name"]
            album_name = track["album"]["name"]
            artist_name = track["artists"][0]["name"]

            library_file.write(f"{id}\t{title}\t{artist_name}\t{album_name}\n")

        offset += 50

    library_file.close()


def handle_create_playlist(infpath, playlistname):

    # read input
    infile = open(infpath, "r")
    trackIds = []
    for line in infile.readlines():
        if line.startswith("#"):
            continue

        parts = line.split("\t")
        id = f"spotify:track:{parts[0]}"
        trackIds.append(id)
    infile.close()
    total_tracks = len(trackIds)
    confirm = input(
        f'Confirm you want to add {total_tracks} songs to a new playlist "{playlistname}" (y/n): '
    )

    if confirm != "y":
        print(f'You pressed "{confirm}", Aborting')
        return
    # get user id
    (resp, raw) = spotify_api_call("v1/me")
    if resp == None:
        return
    user_id = resp["id"]

    # create playlist
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    dt_string_short = datetime.now().strftime("%y%m%d%H%M")
    playlistname = f"{playlistname} by spotify-buddy @ {dt_string_short}"
    print(f"Creating playlist {playlistname}")
    (resp, raw) = spotify_api_call(
        f"v1/users/{user_id}/playlists",
        {
            "name": playlistname,
            "public": False,
            "description": f"Created by spotify-buddy on {dt_string}",
        },
    )
    if resp == None:
        return

    playlist_id = resp["id"]

    # add tracks
    for i in range(0, len(trackIds), 100):
        print(f"Adding tracks {i}/{len(trackIds)}")
        (resp, raw) = spotify_api_call(
            f"v1/playlists/{playlist_id}/tracks", {"uris": trackIds[i : i + 100]}
        )
        if resp == None:
            return
        i += 100

    print(f"Done")


def handle_list_playlist():
    offset = 0
    while True:
        (resp, raw) = spotify_api_call(f"v1/me/playlists?limit=50&offset={offset}")
        if resp == None or len(resp["items"]) == 0:
            return

        for item in resp["items"]:
            id = item["id"]
            title = item["name"]

            print(f"{id}\t{title}")
        offset += 50


def handle_get_playlist(playlist_id):
    if playlist_id.__contains__("\t"):
        # handle when the output of list-playlists is piped
        playlist_id = playlist_id.split("\t")[0]

    (resp, _) = spotify_api_call(f"v1/playlists/{playlist_id}?fields=name")
    if resp == None:
        eprint(f"Error getting playlist with id: {playlist_id}")
        exit(5)
    title = resp["name"]
    print(f"# Playlist: {playlist_id}\t{title}")
    print("# id\ttitle\tartist_name\talbum_name\tpopularity\n")

    offset = 0
    while True:
        fields = (
            "fields=items(track(id%2Cname%2Cpopularity%2Calbum(name)%2Cartists(name)))"
        )
        (resp, _) = spotify_api_call(
            f"v1/playlists/{playlist_id}/tracks?limit=50&offset={offset}&fields={fields}"
        )
        if resp == None or len(resp["items"]) == 0:
            return

        for item in resp["items"]:
            track = item["track"]
            if track == None:
                break

            id = track["id"]
            if id == None:
                continue

            title = track["name"]
            album_name = track["album"]["name"]
            artist_name = track["artists"][0]["name"]
            popularity = track["popularity"]

            print(f"{id}\t{title}\t{artist_name}\t{album_name}\t{popularity}")
        offset += 50


def handle_token():
    host_name = "localhost"
    port = 5050
    client_id = "a7b3642e5c144974a9092e957b788768"
    redirect_uri = f"http://{host_name}:{port}/"
    scopes = "user-read-private,user-library-read,playlist-modify-private,playlist-read-private"

    url = f"https://accounts.spotify.com/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope={scopes}&response_type=token"
    print("Authorize the request and come back when you are asked.")
    webbrowser.open(url)

    class CallbackServer(BaseHTTPRequestHandler):
        def do_GET(self):
            # step 2: get access token from query string
            if self.path.__contains__("?access_token="):
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    bytes("<html><head><title>Spotify Buddy</title></head>", "utf-8")
                )
                self.wfile.write(bytes('<body style="background-color:#000">', "utf-8"))
                self.wfile.write(
                    bytes(
                        '<h1 style="font-family: sans serif;padding: 20px 20px;color: aqua;">Go back to your terminal</h1>',
                        "utf-8",
                    )
                )
                self.wfile.write(
                    bytes(
                        "<script>setTimeout(function(){window.close()}, 2000);</script>",
                        "utf-8",
                    )
                )
                self.wfile.write(bytes("</body></html>", "utf-8"))

                regex = r"access_token=([^&]*)"
                match = re.finditer(regex, self.path, re.MULTILINE).__next__()
                token = match.group(1)
                cmd = f'export access_token="{token}"'
                print(
                    "Success! run the following command to save the access token (it's also copied into the clipboard)"
                )
                print("------------------------------------------------------")
                print(cmd)
                print("------------------------------------------------------")

                os.system(f"echo '{cmd}' | xclip -selection clipboard")
                exit(0)

            # step 1: send a js code to redirect with the code
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                bytes("<html><head><title>Callback</title></head>", "utf-8")
            )
            self.wfile.write(bytes('<body style="background-color:#000">', "utf-8"))
            self.wfile.write(
                bytes(
                    "<script>location.href = `/?${location.hash.substr(1)}`;</script>",
                    "utf-8",
                )
            )
            self.wfile.write(bytes("</body></html>", "utf-8"))

    webServer = HTTPServer((host_name, port), CallbackServer)
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")


def main():
    FILE_NAME_LIBRARY = "spo_library.tsv"
    FILE_NAME_RECOMMENDATAION = "spo_recs_all.tsv"

    parser = argparse.ArgumentParser(description="Recommend new songs")
    cmd = parser.add_subparsers(dest="command")

    # get access token
    token = cmd.add_parser("token", help="Generate access token")

    # download playlist/library
    library = cmd.add_parser("library", help="load library")
    library.add_argument(
        "--out",
        help=f"Outfile file path [optional, default {FILE_NAME_LIBRARY}]",
        default=FILE_NAME_LIBRARY,
    )

    # recommend songs based on seed (--input, a tsv file)
    recommend = cmd.add_parser("recommend", help="generate recommendations")
    recommend.add_argument(
        "--input",
        help=f"Generate recommendations based on tracks in file path [optional, default {FILE_NAME_LIBRARY}]",
        default=FILE_NAME_LIBRARY,
    )
    recommend.add_argument(
        "--out",
        help=f"Outfile file path [optional, default {FILE_NAME_RECOMMENDATAION}]",
        default=FILE_NAME_RECOMMENDATAION,
    )
    recommend.add_argument(
        "--exclude",
        help=f"Comma separated files with tracks to exclude in this mix [optional]",
    )

    # create playlist from recommendations (--input, a tsv file, --name, name)
    cplaylist = cmd.add_parser(
        "create-playlist",
        help="create playlist from a generated recommendations file (*.tsv)",
    )
    cplaylist.add_argument(
        "--input",
        help=f"The file containing all songs details (default: {FILE_NAME_RECOMMENDATAION})",
        default=FILE_NAME_RECOMMENDATAION,
    )
    cplaylist.add_argument("--name", help=f"Name of the playlist", required=True)

    # basic command to talk to spotify
    # list playlists in stdout
    getallplaylists = cmd.add_parser("list-playlists", help="List all user playlists")
    # download playlists
    downloadplaylist = cmd.add_parser("get-playlist", help="Get a playlist")
    downloadplaylist.add_argument(
        "--id", help=f"id of the playlist to dowload", required=True
    )
    downloadplaylist.add_argument(
        "--out",
        help=f"Output file to write (use stdout if not specified)",
    )

    args = parser.parse_args()

    if args.command == None:
        parser.print_help()
        exit(3)

    if args.command == "token":
        handle_token()

    _ = get_access_token()  # validate access token

    if args.command == "library":
        handle_load_library(args.out)
    elif args.command == "recommend":
        handle_load_recommendataion(args.input, args.out, args.exclude)
    elif args.command == "create-playlist":
        handle_create_playlist(args.input, args.name)
    elif args.command == "list-playlists":
        handle_list_playlist()
    elif args.command == "get-playlist":
        handle_get_playlist(args.id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
