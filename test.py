from github import Github
import networkx as nx
from collections import defaultdict
import matplotlib.pyplot as plt

repos_per_step = 10
contributors_per_step = 10
max_depth = 2

def contributors_for_name(name, client):

    repos = []
    for repo in client.get_user(name).get_repos():
        repos.append(repo)

    repos.sort(key=lambda x: x.stargazers_count, reverse=True)
    repos = repos[:repos_per_step]

    contributors_frequency = defaultdict(int)
    for repo in repos:
        for contributor in repo.get_contributors():
            if contributor.login != name:
                contributors_frequency[contributor.login] += 1

    best_contributors = sorted(contributors_frequency.iteritems(), key=lambda (k,v): v, reverse=True)
    return map(lambda (k, v): k, best_contributors[:contributors_per_step])

def network_for_user(name, network, depth, client):
    if depth > max_depth:
        return

    contributors = contributors_for_name(name, g)
    network[name] = contributors

    for contributor in contributors:
        if contributor not in network:
            network_for_user(contributor, network, depth + 1, client)

network = {}
g = Github("tsiss", "qwerty123")

network_for_user("kkapitan", network, 1, g)

G=nx.Graph()
for (name, contributors) in network.iteritems():
    for contributor in contributors:
        G.add_edge(name, contributor)

nx.draw(G)
plt.savefig("simple_path.png")
plt.show()