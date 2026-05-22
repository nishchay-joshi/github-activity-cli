import argparse
import requests


parser = argparse.ArgumentParser(
    description="Find recent GitHub activity of a user"
)

parser.add_argument(
    "-u",
    "--username",
    type=str,
    required=True,
    help="GitHub username"
)

args = parser.parse_args()


def get_user_events(username):
    url = f"https://api.github.com/users/{username}/events"

    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.ConnectionError:
        print("Network error: Unable to connect to GitHub.")
        return None
    except requests.exceptions.Timeout:
        print("Request timed out.")
        return None
    except requests.exceptions.RequestException as error:
        print(f"Unexpected request error: {error}")
        return None

    if response.status_code == 404:
        print(f"User '{username}' does not exist.")
        return None
    elif response.status_code == 403:
        print("GitHub API rate limit exceeded.")
        return None
    elif response.status_code != 200:
        print(f"GitHub API returned status code {response.status_code}")
        return None

    return response.json()


def analyze_events(events):
    summary = {
        "push_count": 0,
        "issue_count": 0,
        "watch_count": 0,
        "fork_count": 0,
        "create_count": 0,
        "pushes_by_repo": {},
    }

    for event in events:

        event_type = event["type"]
        repo_name = event["repo"]["name"]

        if event_type == "PushEvent":
            summary["push_count"] += 1
            summary["pushes_by_repo"][repo_name] = (
                summary["pushes_by_repo"].get(repo_name, 0) + 1
            )
        elif event_type == "IssuesEvent":
            summary["issue_count"] += 1
        elif event_type == "WatchEvent":
            summary["watch_count"] += 1
        elif event_type == "ForkEvent":
            summary["fork_count"] += 1
        elif event_type == "CreateEvent":
            summary["create_count"] += 1

    return summary


def display_summary(username, summary):

    pushes_by_repo = summary["pushes_by_repo"]

    print(f"\nGitHub Activity Summary for {username}\n")
    print(f"Push Events   : {summary['push_count']}")
    print(f"Issue Events  : {summary['issue_count']}")
    print(f"Stars Given   : {summary['watch_count']}")
    print(f"Fork Events   : {summary['fork_count']}")
    print(f"Create Events : {summary['create_count']}")

    print("\nMost Active Repositories:\n")

    sorted_repos = sorted(
        pushes_by_repo.items(),
        key=lambda item: item[1],
        reverse=True
    )

    for index, (repo, pushes) in enumerate(sorted_repos, start=1):
        print(f"{index}. {repo} -> {pushes} push event(s)")


def main(username):

    events = get_user_events(username)

    if events is None:
        return

    summary = analyze_events(events)
    display_summary(username, summary)


if __name__ == "__main__":
    main(args.username)