import math


EPSILON = 1e-15


def _validate_inputs(actual_results, predicted_probabilities):
    if len(actual_results) != len(predicted_probabilities):
        raise ValueError("actual_results and predicted_probabilities must have the same length.")
    if len(actual_results) == 0:
        raise ValueError("Cannot calculate metrics for an empty prediction set.")


def _clip_probability(probability):
    return min(max(float(probability), EPSILON), 1 - EPSILON)


def calculate_accuracy(actual_results, predicted_probabilities):
    _validate_inputs(actual_results, predicted_probabilities)

    correct = 0
    for actual, probability in zip(actual_results, predicted_probabilities):
        predicted_result = 1 if probability >= 0.5 else 0
        if predicted_result == actual:
            correct += 1

    return correct / len(actual_results)


def calculate_log_loss(actual_results, predicted_probabilities):
    _validate_inputs(actual_results, predicted_probabilities)

    total_log_loss = 0
    for actual, probability in zip(actual_results, predicted_probabilities):
        probability = _clip_probability(probability)
        probability_given_to_actual_result = probability if actual == 1 else 1 - probability
        total_log_loss += -math.log(probability_given_to_actual_result)

    return total_log_loss / len(actual_results)


def calculate_brier_score(actual_results, predicted_probabilities):
    _validate_inputs(actual_results, predicted_probabilities)

    total_squared_error = 0
    for actual, probability in zip(actual_results, predicted_probabilities):
        total_squared_error += (probability - actual) ** 2

    return total_squared_error / len(actual_results)


def calculate_classification_metrics(actual_results, predicted_probabilities):
    return {
        "accuracy": calculate_accuracy(actual_results, predicted_probabilities),
        "log_loss": calculate_log_loss(actual_results, predicted_probabilities),
        "brier_score": calculate_brier_score(actual_results, predicted_probabilities),
    }
