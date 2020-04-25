
from kaggle_environments import evaluate, make

env = make("halite", debug=True)

env.run(["submission.py", "random", "random", "random"])
# env.render(mode="ipython", width=800, height=600)
out = env.render(mode="html", width=800, height=600)
f = open("halite.html", "w")
f.write(out)
f.close()
