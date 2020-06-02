#!/usr/bin/env python3
import argparse
from typing import Text

import github


def mark_as_prerelease(token: Text, release_id: int, repo: Text) -> Text:
    """Updates a release to pre-release status.

    Args:
        token: The token to use when talking to the GitHub API.
        release_id: The ID of the release.
        repo: The GitHub repo to update the release in.

    Returns:
        The release ID.
    """
    gh = github.Github(token)
    repo = gh.get_repo(repo)
    git_release = repo.get_release(id=release_id)
    # The API requires we sent the name and message again, so we just pass what we already have.
    git_release.update_release(
        name=git_release.title, message=git_release.body, draft=False, prerelease=True)

    return git_release.id


def main(args: argparse.Namespace):
    print(mark_as_prerelease(args.token, args.release_id, args.repo))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Utility to create a mark a release as pre-release.')
    parser.add_argument(
        '--token',
        help='The GitHub oauth token. This is usually provided by a GitHub actions secret.',
        type=str,
        required=True)
    parser.add_argument('--release_id', help='The ID of the release.', type=int, required=True)
    parser.add_argument(
        '--repo', help='The GitHub repo.', type=str, default='jeshua-clipchamp/sandbox')

    main(parser.parse_args())
