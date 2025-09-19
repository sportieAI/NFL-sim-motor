import torch
import numpy as np


class SyntheticDataGenerator:
    """
    Utility for generating synthetic data for pre-training or meta-learning.
    Can simulate states, actions, rewards for RL tasks.
    """

    def __init__(self, state_dim, action_dim, num_tasks=1, seed=None):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.num_tasks = num_tasks
        self.rng = np.random.RandomState(seed)

    def sample_task_params(self):
        """
        Generate random parameters for a synthetic task.
        Returns a dict encoding task-specific parameters.
        """
        # Example: randomly generate a reward weight vector per task
        return {"reward_weights": self.rng.randn(self.state_dim)}

    def generate_trajectory(self, task_params, length=20):
        """
        Simulate a synthetic trajectory for a given task.
        Returns (states, actions, rewards) as torch tensors.
        """
        states = []
        actions = []
        rewards = []

        state = torch.from_numpy(self.rng.randn(self.state_dim)).float()
        for t in range(length):
            action = self.rng.randint(0, self.action_dim)
            next_state = (
                state + torch.from_numpy(0.1 * self.rng.randn(self.state_dim)).float()
            )
            reward = float(np.dot(task_params["reward_weights"], next_state.numpy()))
            states.append(state)
            actions.append(action)
            rewards.append(reward)
            state = next_state

        states = torch.stack(states)
        actions = torch.tensor(actions, dtype=torch.long)
        rewards = torch.tensor(rewards, dtype=torch.float32)
        return states, actions, rewards

    def generate_dataset(self, num_trajectories=100, length=20):
        """
        Generate a dataset of synthetic trajectories for meta-learning.
        Returns a list of dicts: [{"states": ..., "actions": ..., "rewards": ..., "task_params": ...}, ...]
        """
        dataset = []
        for _ in range(num_trajectories):
            task_params = self.sample_task_params()
            states, actions, rewards = self.generate_trajectory(task_params, length)
            dataset.append(
                {
                    "states": states,
                    "actions": actions,
                    "rewards": rewards,
                    "task_params": task_params,
                }
            )
        return dataset


if __name__ == "__main__":
    # Example usage
    generator = SyntheticDataGenerator(state_dim=10, action_dim=4, num_tasks=1, seed=42)
    dataset = generator.generate_dataset(num_trajectories=5, length=15)
    for i, traj in enumerate(dataset):
        print(f"Trajectory {i}:")
        print("States shape:", traj["states"].shape)
        print("Actions:", traj["actions"])
        print("Rewards:", traj["rewards"])
        print("Task params:", traj["task_params"])
        print("---")
