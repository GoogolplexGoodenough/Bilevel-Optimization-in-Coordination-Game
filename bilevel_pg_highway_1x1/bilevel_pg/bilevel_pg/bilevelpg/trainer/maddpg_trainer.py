"""
The trainer for multi-agent training.
"""
import pickle
# from malib.trainers.utils import *
from bilevel_pg.bilevelpg.trainer.utils_maddpg import *
import time


class Bilevel_Trainer:
    """This class implements a multi-agent trainer.
    """
    def __init__(
            self, env, agents, sampler,
            batch_size=128,
            steps=10000,
            exploration_steps=100,
            training_interval=1,
            extra_experiences=['target_actions'],
            save_path=None,
    ):
        self.env = env
        self.agents = agents
        self.sampler = sampler
        self.batch_size = batch_size
        self.steps = steps
        self.exploration_steps = exploration_steps
        self.training_interval = training_interval
        # print(training_interval)
        self.extra_experiences = extra_experiences
        self.losses = []
        self.save_path = save_path
        self.epsilon = 0.1

    def setup(self, env, agents, sampler):
        self.env = env
        self.agents = agents
        self.sampler = sampler

    def sample_batches(self):
        assert len(self.agents) > 1
        batches = []
        indices = self.agents[0].replay_buffer.random_indices(self.batch_size)
        for agent in self.agents:
            batch = agent.replay_buffer.batch_by_indices(indices)
            batches.append(batch)
        return batches

    def do_communication(self):
        pass

    def individual_forward(self):
        pass

    def centralized_forward(self):
        pass

    def apply_gradient(self):
        pass

    def run(self):
        print('trainer_start')
        for step in range(self.steps):
            '''
            if (np.random.uniform(0, 1) > 0.9):
                self.sampler.sample(explore=True)
            else:
                self.sampler.sample()
            '''
            
            if step < self.exploration_steps:
                 self.sampler.sample(explore=True)
                 continue
            
            if (np.random.uniform(0, 1) < self.epsilon):
                self.sampler.sample(explore=True)
            else:
                self.sampler.sample()
            
            #self.sampler.sample()
            batches = self.sample_batches()
            # print(np.array(batches)[0])
            # print('sample finish')
            # print(int(round(time.time() * 1000)))

            for extra_experience in self.extra_experiences:
                if extra_experience == 'annealing':
                    batches = add_annealing(batches, step, annealing_scale=1.)
                elif extra_experience == 'target_actions':
                    batches = add_target_actions(batches, self.agents, self.batch_size)
                elif extra_experience == 'recent_experiences':
                    batches = add_recent_batches(batches, self.agents, self.batch_size)
            agents_losses = []

            # print('extra finish')
            # print(int(round(time.time() * 1000)))

            if step % self.training_interval == 0:
                for agent, batch in zip(self.agents, batches):
                    # print(batch['actions'].shape)
                    agent_losses = agent.train(batch)
                    agents_losses.append(agent_losses)
                #print("---------------PRINT Q VALUES FOR AGENT 0------------------")
                #print(self.agents[0].get_critic_value(np.array([[1, 1, 0, 0, 0, 1, 0, 0, 0]])))
                #print(self.agents[0].get_critic_value(np.array([[1, 0, 0, 0, 1, 0, 0, 0, 1]])))
                #print(self.agents[0].get_critic_value(np.array([[1, 1, 0, 0, 1, 0, 0]])))
                #print(self.agents[0].get_critic_value(np.array([[1, 0, 0, 1, 0, 0, 1]])))
                #print(self.agents[0].get_critic_value(np.array([[0, 1, 0, 1, 0]])))
                #print(self.agents[0].get_critic_value(np.array([[0, 1, 0, 0, 1]])))
                #print(self.agents[0].get_critic_value(np.array([[0, 0, 1, 1, 0]])))
                #print(self.agents[0].get_critic_value(np.array([[0, 0, 1, 0, 1]])))

                #print(self.agents[0].get_policy_np(np.array([[1]])))
                #print(self.agents[1].get_policy_np(np.array([[1]])))
                #print(self.agents[1].get_policy_np(np.array([[1, 1, 0]])))
            #if step % 500 == 0:
            #    print("pause")
            self.losses.append(agent_losses)
            
            if step >0 and step % 10000 == 0:
                self.epsilon *= 0.9
            
            # print('train finish')
            # print(int(round(time.time() * 1000)))

    def save(self):
        if self.save_path is None:
            self.save_path = '/tmp/agents.pickle'
        with open(self.save_path, 'wb') as f:
            pickle.dump(self.agents, f, pickle.HIGHEST_PROTOCOL)

    def restore(self, restore_path):
        with open(restore_path, 'rb') as f:
            self.agents = pickle.load(f)

    def resume(self):
        pass

    def log_diagnostics(self):
        pass