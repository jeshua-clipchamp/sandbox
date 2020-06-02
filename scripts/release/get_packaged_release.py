#!/usr/bin/env python3

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from typing import Dict, Optional, Text

import requests

## NOTE: We cannot use PyGithub here because it does not yet support the Actions API.

_CHECK_API_HEADER = {'Accept': 'application/vnd.github.antiope-preview+json'}


def get_url(token: Text, url: Text, headers: Optional[Dict[Text, Text]] = None):
    """Perform a GET operation to the given URL.

    Args:
        token: The token to authorize with.
        url: The URL to query. This is everything after the common prefix.
        headers: An additional set of headers to include.

    Returns:
        The resulting JSON object.
    """
    if not url.startswith('https://api.github.com/'):
        url = 'https://api.github.com/' + url

    headers = headers or {}
    headers['Authorization'] = f'Bearer {token}'
    return requests.get(url=url, headers=headers)


def get_json(token: Text, url: Text, headers: Optional[Dict[Text, Text]] = None):
    return get_url(token=token, url=url, headers=headers).json()


def get_check_suites(token: Text, repo: Text, ref: Text):
    """Get a list of check suites for the given ref.

    Args:
        repo: The user/repo query.
        token: The token to authenticate with.
        ref: Either a branch, tag or sha that we want to get the check run for.

    Returns:
        A list of CheckSuite objects.
    """
    return get_json(
        token=token,
        url=f'https://api.github.com/repos/{repo}/commits/{ref}/check-suites',
        headers=_CHECK_API_HEADER)


def main(args: argparse.Namespace):
    workflow_runs = get_json(
        token=args.github_token,
        url=f'repos/{args.github_repo}/actions/workflows/ci-deploy.yaml/runs')

    print(workflow_runs)

    workflow_runs = [wr for wr in workflow_runs['workflow_runs'] if wr['head_sha'].startswith(args.sha)]
    if not workflow_runs:
        print('ERROR: Could not find deploy run for the given sha.')
        return 1

    if len(workflow_runs) > 1:
        print('ERROR: Found multiple workflows runs for the given sha.')
        return 1

    # Wait for the workflow run to finish.
    workflow_run = workflow_runs[0]
    while workflow_run['status'] != 'completed':
        print(f'Workflow is not finished, waiting for {args.poll_interval_s}...')
        time.sleep(args.poll_interval_s)

        workflow_run = get_json(token=args.github_token, url=workflow_run['url'])

    conclusion = workflow_run['conclusion']
    if conclusion != 'success':
        print(f'ERROR: Workflow failed to finish with conclusion "{conclusion}"')
        return 1

    # Workflow finish and was successful, time to get the artifacts.
    artifacts = get_json(token=args.github_token, url=workflow_run['artifacts_url'])['artifacts']
    if not artifacts:
        print(f'ERROR: Could not find any artifacts')
        return 1

    # Download them one at a time.
    for artifact in artifacts:
        artifact_name = artifact['name']
        artifact_size_mb = artifact['size_in_bytes'] / 1024 / 1024
        artifact_url = artifact['archive_download_url']
        output_file = os.path.join(args.output_dir, artifact_name + '.zip')

        print(
            f'Downloading artifact {artifact_name} to {output_file} ({artifact_size_mb:.0f} MiB) from {artifact_url}...'
        )
        subprocess.check_call(
            shlex.split(
                f'curl -L -X GET -H "Authorization: Bearer {args.github_token}" -o {output_file} {artifact_url}'
            ))

    return 0


if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser(
        description='Utility to download a packaged release from GH Actions.')
    argument_parser.add_argument(
        '--github_token', type=str, required=True, help='The GitHub API token to use.')
    argument_parser.add_argument('--sha', type=str, required=True, help='The git hash to look for.')
    argument_parser.add_argument(
        '--github_repo',
        type=str,
        default='jeshua-clipchamp/sandbox',
        help='The GitHub repo this action is being run as part of.')
    argument_parser.add_argument(
        '--output_dir',
        type=str,
        default=os.getcwd(),
        help='The directory to download the built artifacts to.')
    argument_parser.add_argument(
        '--poll_interval_s',
        type=int,
        default=60,
        help='The amount of time between checks when waiting for a check suite to finish.')
    sys.exit(main(argument_parser.parse_args()))
