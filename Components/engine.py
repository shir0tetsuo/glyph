import random
import numpy as np

def NewRandomSeed():
    # Get a random integer from 0 to 10000
    return int(random.uniform(0, 10000))

class WeightedDictRandomizer:
    def __init__(self, weights: dict[str, float], seed=None):
        """
        Initializes the WeightedDictRandomizer.

        Args:
            weights (dict[str, float]): A dictionary where keys are items and values are their corresponding probabilities.
            seed (int): An optional seed for the random number generator. Defaults to None.
        """

        # Set the seed if provided
        #self.rng = random.Random(seed)
        self.seed = seed
        
        # Check that all weight values add up to 1
        if not self._validate_weights(weights):
            print(weights)
            raise ValueError("Weights do not sum to 1")

        # Normalize weights
        total_weight = sum(weights.values())
        normalized_weights = {k: v / total_weight for k, v in weights.items()}

        # Store the normalized weights as an instance variable
        self.normalized_weights = normalized_weights

    def __repr__(self):
        return "WeightedDictRandomizer"

    def _validate_weights(self, weights):
        """
        Validates that all weight values add up to 1.

        Args:
            weights (dict[int, float]): A dictionary where keys are items and values are their corresponding probabilities.

        Returns:
            bool: True if the weights sum up to 1, False otherwise.
        """

        # Check that all weights add up to 1
        return abs(sum(weights.values()) - 1) < 1e-6

    def result(self):
        """
        Returns a random choice from the dictionary based on their normalized probabilities.

        Returns:
            A random item from the dictionary.
        """

        # Use the randomly generated number to select an item from the normalized weights
        return np.random.default_rng(self.seed).choice(list(self.normalized_weights.keys()), p=list(self.normalized_weights.values()))




def BooleanFromSeedWeight(seed, weight) -> bool:
    """
    Generates a boolean value based on a seed and a weight.
    Args:
        seed (int): The seed for the random number generator.
        weight (float): The probability of generating True.
    Returns:
        bool: True with the specified probability, False otherwise.
    """
    # Create a random number generator using the provided seed
    rng = np.random.default_rng(seed)
    # Generate a boolean value based on the weight
    return rng.choice([True, False], p=[weight, 1 - weight])
