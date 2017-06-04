import argparse

from GitHubNetwork import GitHubNetwork


def main():
    parser = argparse.ArgumentParser(description='Github Network Graph Builder')

    parser.add_argument('--max_depth', default=2, type=int, help='number of steps')
    parser.add_argument('--max_contributors', default=5, type=int, help='number of contributors to fetch for each step')
    parser.add_argument('--max_repos', default=5, type=int, help='number of repos to fetch for each step')
    parser.add_argument('--max_extern_repos', default=5, type=int,
                        help='number of external repos the user was involved in (by issues) to fetch for each step')
    parser.add_argument('--slow_rate', default=False, action='store_true', help='limit number of contributors_for_name() requests to 1/min')
    parser.add_argument('--name', type=str, required=True, help='name of the user to build a graph for')
    args = parser.parse_args()

    network = GitHubNetwork(max_repos=args.max_repos, max_extern_repos=args.max_extern_repos,
                            max_contributors=args.max_contributors, max_depth=args.max_depth, slow_rate=args.slow_rate)
    network.build_for(args.name)


if __name__ == "__main__":
    main()
