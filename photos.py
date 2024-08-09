from os.path import join, dirname
from google_photos_client import google_photos


def get_albums():
    results = google_photos.albums().list().execute()
    albums = results.get("albums", [])
    next_page_token = results.get("nextPageToken", "")
    for album in albums:
        print(f"{album['title']} {album['id']}")


def get_album_photos(album_id):
    results = (
        google_photos.mediaItems()
        .search(
            body={
                "albumId": album_id,
                "pageSize": 10,
            }
        )
        .execute()
    )
    items = results.get("mediaItems", [])
    next_page_token = results.get("nextPageToken", "")
    for item in items:
        print(
            f"{item['filename']} {item['mimeType']}"
            f" \nURL: {item['productUrl']} {item['baseUrl']}"
        )


def get_photos():
    next_page_token = ""
    results = (
        google_photos.mediaItems()
        .search(
            body={
                "filters": {
                    # "dateFilter": {
                    #     "dates": [{"day": day, "month": month, "year": year}]
                    # }
                },
                "pageSize": 10,
                "pageToken": next_page_token,
            }
        )
        .execute()
    )
    items = results.get("mediaItems", [])
    next_page_token = results.get("nextPageToken", "")
    for item in items:
        print(
            f"{item['filename']} {item['mimeType']}"
            f" \nURL: {item['productUrl']} {item['baseUrl']}"
        )


get_albums()
# get_album_photos(
#     "ALR1KcLHMqmYCe4BFVBguTK-gJCjBhTZmWSVE85fVwdDB8Ec9MUnqWTQSnKMM7G-pAxB4uWwAb9s"
# )
