import time

class MetaLearningTrigger:
    """
    Automates meta-learning triggers for simulation engines.
    Triggers can be based on performance metrics, trend changes, or custom conditions.
    """

    def __init__(self, learning_callback, check_interval=300):
        """
        Args:
            learning_callback (callable): Function to call when a trigger fires.
            check_interval (int): Check interval in seconds.
        """
        self.learning_callback = learning_callback
        self.check_interval = check_interval
        self.last_checked = time.time()
        self.trigger_conditions = []

    def add_trigger_condition(self, condition_func):
        """
        Adds a new trigger condition. The function should accept game_state and return True/False.
        """
        self.trigger_conditions.append(condition_func)

    def check_and_trigger(self, game_state):
        """
        Checks all trigger conditions against the current game_state.
        If any condition is True, fires the learning callback.
        """
        now = time.time()
        if now - self.last_checked < self.check_interval:
            return
        self.last_checked = now

        for condition in self.trigger_conditions:
            if condition(game_state):
                self.learning_callback(game_state)
                break

# Example usage:
# def my_learning_callback(state):
#     print("Meta-learning triggered!", state)
#
# trigger = MetaLearningTrigger(learning_callback=my_learning_callback, check_interval=60)
#
# def score_jump_condition(state):
#     return state.get('score_diff', 0) > 20
#
# trigger.add_trigger_condition(score_jump_condition)
#
# # In game loop:
# trigger.check_and_trigger(current_game_state)