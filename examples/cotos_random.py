''' A toy example of playing Uno with random agents
'''

import time
import rlcard
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed
from rlcard.games.cotos.player import SERVER

try:
    import socketio
except ImportError:
    print("pip install python-socketio==4.4.0")


def create_game(env, game_id=[]):
    sio = socketio.Client()
    sio.connect(SERVER)
    game_id = []

    @sio.on('newGameCreated')
    def game_created(data):
        game_id += [data['gameId']]

    sio.emit('createNewGame', {'type': 1111})
    while len(game_id) == 0:
        time.sleep(1)

    env.set_game_id(game_id[0])

# Make environment
env = rlcard.make('cotos')
episode_num = 1000
create_game(env)

# Set a global seed
set_global_seed(0)

# Set up agents
agent_0 = RandomAgent(action_num=env.action_num)
agent_1 = RandomAgent(action_num=env.action_num)
agent_2 = RandomAgent(action_num=env.action_num)
agent_3 = RandomAgent(action_num=env.action_num)
env.set_agents([agent_0, agent_1, agent_2, agent_3])

for episode in range(episode_num):
    print("#" * 50)
    print("EPISODE: ", episode)
    # Generate data from the environment
    trajectories, _ = env.run(is_training=False)

    # Print out the trajectories
    # for ts in trajectories[0]:
    #     print('State: {}, Action: {}, Reward: {}, Next State: {}, Done: {}'.format(
    #         ts[0], ts[1], ts[2], ts[3], ts[4]))
    for ts in trajectories[0]:
        print('Action: {}, Reward: {}'.format(ts[1], ts[2]))

    print("END EPISODE")
