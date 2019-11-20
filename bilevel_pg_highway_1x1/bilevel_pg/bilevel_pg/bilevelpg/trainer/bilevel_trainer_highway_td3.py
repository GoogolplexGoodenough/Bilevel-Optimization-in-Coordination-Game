"""
The trainer for multi-agent training.
"""
import pickle
# from malib.trainers.utils import *
from bilevel_pg.bilevelpg.trainer.utils_highway_maddpg import *
from bilevel_pg.bilevelpg.trainer.bilevel_test_highway_maddpg import Tester
from bilevel_pg.bilevelpg.samplers.sampler_highway_test_maddpg import MASampler_Test
import time
import numpy as np

class Bilevel_Trainer:
    """This class implements a multi-agent trainer.
    """
    def __init__(
            self, seed, env, agents, train_agents, sampler,
            batch_size=128,
            steps=10000,
            exploration_steps=100,
            training_interval=1,
            extra_experiences=['target_actions'],
            save_path=None,
    ):
        self.env = env
        self.seed = seed
        self.agents = agents
        self.train_agents = train_agents
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
        self.success_rate = []

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
        #print('trainer_start')
        for step in range(self.steps):
            #print("step ", step)
            if step < self.exploration_steps:
                 self.sampler.sample(explore=True)
                 continue
            
            if (np.random.uniform(0, 1) < self.env.epsilon):
                self.sampler.sample(explore=True)
            else:
                self.sampler.sample()
            
            #self.sampler.sample()
            
            batches = self.sample_batches()
            # print(np.array(batches).shape) (2, )  leader and follower
            # print(np.array(batches)[0])
            # print('sample finish')
            # print(int(round(time.time() * 1000)))

            for extra_experience in self.extra_experiences:
                if extra_experience == 'annealing':
                    batches = add_annealing(batches, step, annealing_scale=1.)
                elif extra_experience == 'target_actions':
                    batches = add_target_actions(self.env, self.sampler, batches, self.agents, self.train_agents, self.batch_size)
                elif extra_experience == 'recent_experiences':
                    batches = add_recent_batches(batches, self.agents, self.batch_size)
            agents_losses = []

            # print('extra finish')
            # print(int(round(time.time() * 1000)))

            if step % self.training_interval == 0:
                
                for agent, batch in zip(self.agents, batches):
                    if self.env.is_vehicles_valid[agent._agent_id]:
                        agent_losses = self.train_agents[agent._agent_id].train(batch, self.env, agent._agent_id)
                        agents_losses.append(agent_losses)
                

            if step > 0 and step % 500 == 0:
                self.env.epsilon *= 0.9
            ''' 
            if step % 100 == 0:
                test_sampler = MASampler_Test(self.env.agent_num, self.env.leader_num, self.env.follower_num)
                test_sampler.initialize(self.env, self.agents, self.train_agents)
                self.env.merge_count = 0
                self.env.correct_merge_count = 0
                tester = Tester(
                    env=self.env, agents=self.agents, train_agents=self.train_agents, sampler=test_sampler,
                    steps=5000, exploration_steps=self.exploration_steps,
                    extra_experiences=['target_actions'], batch_size=self.batch_size
                )
                tester.run()
                self.success_rate.append(self.env.correct_merge_count / 100)
                print("step ", step, ", success rate = ", self.env.correct_merge_count / 100)
            if step % 1000 == 0:
                np.save('./curves/sucess_rate_MADDPG.npy', self.success_rate)
            '''
            
            if self.env.merge_count % 100 == 0:
                np.save('./curves/reward0_TD3_1x1_test'+str(self.seed)+'_s6_t15.npy', self.env.episodes_reward_0)
                np.save('./curves/reward1_TD3_1x1_test'+str(self.seed)+'_s6_t15.npy', self.env.episodes_reward_1) 
                np.save('./curves/success_merge_TD3_1x1_test'+str(self.seed)+'_s6_t15.npy', self.env.episode_merge_record)
                np.save('./curves/target_merge_TD3_1x1_test'+str(self.seed)+'_s6_t15.npy', self.env.episode_target_merge_record) 
            if self.env.merge_count == 8001:
                break
            # print('train finish')
            # print(int(round(time.time() * 1000)))

    def save(self):
        save_path = './models/agents_td3_1x1_'+'test'+str(self.seed)+'_s6_t15.pickle'
        if self.save_path is None:
            self.save_path = './models/agents_maddpg_1x1_seed35.pickle'
        with open(save_path, 'wb') as f:
            pickle.dump(self.train_agents, f, pickle.HIGHEST_PROTOCOL)

    def restore(self, restore_path):
        with open(restore_path, 'rb') as f:
            self.train_agents = pickle.load(f)

    def resume(self):
        pass

    def log_diagnostics(self):
        pass