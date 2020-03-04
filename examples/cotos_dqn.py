''' An example of learning a Deep-Q Agent on Dou Dizhu
'''
import time
import sys

import tensorflow as tf

import rlcard
from rlcard.agents.dqn_agent import DQNAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed
from rlcard.utils.logger import Logger
from rlcard.games.cotos.player import SERVER

try:
    import socketio
except ImportError:
    print("pip install python-socketio==4.4.0")


def create_game(env):
    sio = socketio.Client()
    sio.connect(SERVER)
    game_id=[]

    @sio.on('newGameCreated')
    def game_created(data):
        env.set_game_id(data['gameId'])

    sio.emit('createNewGame', {'type': 1111})
    env.sio = sio


# Make environment
env = rlcard.make('cotos')
eval_env = rlcard.make('cotos')

# Set the iterations numbers and how frequently we evaluate/save plot
evaluate_every = 100
save_plot_every = 1000
evaluate_num = 10000
episode_num = 1000000

# Set the the number of steps for collecting normalization statistics
# and intial memory size
memory_init_size = 1000
norm_step = 1000

# The paths for saving the logs and learning curves
root_path = './experiments/cotos_dqn_result/'
log_path = root_path + 'log.txt'
csv_path = root_path + 'performance.csv'
figure_path = root_path + 'figures/'

# Set a global seed
set_global_seed(0)

# eval_env.game.server_game_id = env.game.server_game_id

with tf.compat.v1.Session() as sess:
    # Set agents
    global_step = tf.Variable(0, name='global_step', trainable=False)
    agent = DQNAgent(sess,
                     scope='dqn',
                     action_num=env.action_num,
                     replay_memory_size=20000,
                     replay_memory_init_size=memory_init_size,
                     norm_step=norm_step,
                     state_shape=env.state_shape,
                     mlp_layers=[512, 512])

    random_agent = RandomAgent(action_num=eval_env.action_num)

    sess.run(tf.compat.v1.global_variables_initializer())

    env.set_agents([agent, random_agent, random_agent, random_agent])
    eval_env.set_agents([agent, random_agent, random_agent, random_agent])

    # Count the number of steps
    step_counter = 0

    # Init a Logger to plot the learning curve
    logger = Logger(
        xlabel='timestep', ylabel='reward', legend='DQN on COTOS',
        log_path=log_path, csv_path=csv_path)

    for episode in range(episode_num):
        print("#" * 50)
        print("EPISODE: ", episode)
        # Generate data from the environment
        create_game(env)
        time.sleep(5)
        trajectories, _ = env.run(is_training=True)
        env.sio.disconnect()

        # Feed transitions into agent memory, and train the agent
        for ts in trajectories[0]:
            agent.feed(ts)
            step_counter += 1

            # Train the agent
            train_count = step_counter - (memory_init_size + norm_step)
            if train_count > 0:
                loss = agent.train()
                print('\rINFO - Step {}, loss: {}'.format(step_counter, loss), end='')

        # Evaluate the performance. Play with random agents.
        if episode % evaluate_every == 0:
            reward = 0
            for eval_episode in range(evaluate_num):
                create_game(eval_env)
                time.sleep(5)
                _, payoffs = eval_env.run(is_training=False)
                time.sleep(5)
                eval_env.sio.disconnect()
                reward += payoffs[0]

            logger.log('\n########## Evaluation ##########')
            logger.log(
                'Timestep: {} Average reward is {}'.format(
                    env.timestep, float(reward)/evaluate_num))

            # Add point to logger
            logger.add_point(x=env.timestep, y=float(reward)/evaluate_num)

        # Make plot
        if episode % save_plot_every == 0 and episode > 0:
            logger.make_plot(save_path=figure_path+str(episode)+'.png')

    # Make the final plot
    logger.make_plot(save_path=figure_path+'final_'+str(episode)+'.png')
