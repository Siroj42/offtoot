# offtoot

A command line mastodon client inspired by [offpunk](https://sr.ht/~lioploum/offpunk/). Downloads statuses & stores them for offline reading. Currently extremely limited.

## Roadmap

- [x] Login & automatically generate secret
  - [] Proper (meaning more secure) Secret storage implementation
- [x] Actually render the bit of html in most posts, especially with links and hashtags
  - [x] Offpunk-style links & hashtags
- [] Ability to delete old entries
- [] Looking up if posts in current tour have been edited
- [] Sync depth (=comments/posts that the downloaded post is a reply to)
- [x] Prettier output
- [x] Image handling
  - [x] Image downloading
  - [] Inline Image viewing
    - [] Nix packaging for chafa.py
- [] Guides
- [] Outbox / Creating posts
- [] Fetch-later list
  - [] Add posts from tour that were not found to fetch-later
