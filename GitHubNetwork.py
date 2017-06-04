from github import Github
from collections import defaultdict

import networkx as nx
import matplotlib.pyplot as plt
import urllib, json
import colorsys
import re

PATTERN_ISSUE_PR = "[/](pull|issue).*"

class GitHubNetwork:

    def __init__(self, max_repos=5, max_extern_repos=5, max_contributors=5, max_depth=2):
        self.repos_per_step = max_repos
        self.ext_repos_per_step = max_extern_repos
        self.max_depth = max_depth
        self.contributors_per_step = max_contributors
        self.client = Github("tsiss", "qwerty123")

    def contributors_for_name(self, name):
        print "--> Finding contributors for " + name

        print "\t--> Fetching " + str(self.repos_per_step) + " best ranked repos..."

        repos = []
        for repo in self.client.get_user(name).get_repos():
            repos.append(repo)

        repos = filter(lambda x: not x.fork, repos)
        repos.sort(key=lambda x: x.stargazers_count, reverse=True)
        repos = repos[:self.repos_per_step]

        print "\t--> Fetching " + str(self.ext_repos_per_step) + " most recent external repos..."
        issues = self.client.search_issues(query="involves:" + str(name), sort="updated", order="desc")
        issue_urls = set()
        issue_list = list()
        for issue in issues:
            html_url = re.sub(PATTERN_ISSUE_PR, "", issue.html_url)  # remove '/pull/123' or '/issue/123' suffix
            if html_url not in issue_urls:
                issue_urls.add(html_url)
                if not issue.repository.fork:
                    issue_list.append(issue)
            if len(issue_list) >= self.ext_repos_per_step:
                break
        for issue in issue_list:
            repos.append(issue.repository)

        print "\t--> DONE " + str(repos)

        print "\t--> Fetching " + str(self.contributors_per_step) + " most common contributors..."

        contributors_frequency = defaultdict(int)
        for repo in repos:
            for contributor in repo.get_contributors():
                if contributor.login != name:
                    contributors_frequency[contributor.login] += 1

        best_contributors = sorted(contributors_frequency.iteritems(),
                                   key=lambda (k, v): v,
                                   reverse=True)

        print "\t--> DONE"

        return map(lambda (k, v): k, best_contributors[:self.contributors_per_step])

    def network_for_user(self, name, network, depth):
        if depth > self.max_depth:
            return

        contributors = self.contributors_for_name(name)
        network[name] = contributors

        for contributor in contributors:
            if contributor not in network:
                self.network_for_user(contributor, network, depth + 1)

    def build_for(self, name):
        network = {}

        self.network_for_user(name, network, 1)

        G = nx.Graph()
        for (name, contributors) in network.iteritems():
            for contributor in contributors:
                G.add_edge(name, contributor)

        color_map = []
        d = sorted(nx.degree(G).values(), reverse=True)
        d1 = nx.degree(G)
        for node in G:
            color_map.append(colorsys.rgb_to_hsv(1.0/max(d)*G.degree(node), 1.0-0.8/max(d)*G.degree(node), 0.5))

        nx.draw(G, with_labels=True, nodelist=d1.keys(), node_size=[(200 + v * 100) for v in d1.values()], node_color=color_map)

        plt.savefig("simple_path.png")
        plt.show()