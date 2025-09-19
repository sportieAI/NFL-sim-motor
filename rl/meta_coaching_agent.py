import torch
import torch.nn as nn
import torch.nn.functional as F


class PolicyNetwork(nn.Module):
    def __init__(self, state_dim, action_dim, hidden_dim=256):
        super().__init__()
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.action_head = nn.Linear(hidden_dim, action_dim)

    def forward(self, state):
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        action_logits = self.action_head(x)
        return F.softmax(action_logits, dim=-1)


class ValueNetwork(nn.Module):
    def __init__(self, state_dim, hidden_dim=256):
        super().__init__()
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.value_head = nn.Linear(hidden_dim, 1)

    def forward(self, state):
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        value = self.value_head(x)
        return value


class MetaController(nn.Module):
    """
    Meta-controller that modulates the agent's policy/value based on task context.
    """

    def __init__(self, task_dim, hidden_dim=128):
        super().__init__()
        self.fc1 = nn.Linear(task_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.control_head = nn.Linear(hidden_dim, hidden_dim)

    def forward(self, task_embedding):
        x = F.relu(self.fc1(task_embedding))
        x = F.relu(self.fc2(x))
        control_signal = torch.tanh(self.control_head(x))
        return control_signal


class MetaCoachingAgent(nn.Module):
    def __init__(self, state_dim, action_dim, task_dim, hidden_dim=256):
        super().__init__()
        self.policy_net = PolicyNetwork(state_dim, action_dim, hidden_dim)
        self.value_net = ValueNetwork(state_dim, hidden_dim)
        self.meta_controller = MetaController(task_dim, hidden_dim // 2)

    def forward(self, state, task_embedding):
        # Meta-controller influences the policy/value networks via context
        control_signal = self.meta_controller(task_embedding)
        # Example: concatenate context to state (alternatively, use FiLM, gating, etc.)
        augmented_state = torch.cat([state, control_signal], dim=-1)
        action_probs = self.policy_net(augmented_state)
        value = self.value_net(augmented_state)
        return action_probs, value


# Example usage:
if __name__ == "__main__":
    # Example dimensions
    state_dim = 20
    action_dim = 5
    task_dim = 8
    agent = MetaCoachingAgent(
        state_dim + (hidden_dim := 256) // 2, action_dim, task_dim
    )
    state = torch.randn(1, state_dim)
    task_embedding = torch.randn(1, task_dim)
    action_probs, value = agent(state, task_embedding)
    print("Action probabilities:", action_probs)
    print("Value:", value)
