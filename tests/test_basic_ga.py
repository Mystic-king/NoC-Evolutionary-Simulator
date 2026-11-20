from modules.basic_ga.optimizer import BasicGeneticAlgorithm, GAConfig


def test_decode_binary_chromosome():
    assert BasicGeneticAlgorithm.decode([1, 1, 0, 1, 0]) == 26


def test_ga_returns_valid_solution_and_history():
    config = GAConfig(population_size=20, generations=30, seed=7)
    result = BasicGeneticAlgorithm(config).run()
    assert 0 <= result["best_solution"] <= 31
    assert result["best_fitness"] == result["best_solution"] ** 2
    assert len(result["history"]) == 31
    assert result["history"][-1]["generation"] == 30


def test_ga_is_reproducible_for_same_seed():
    config = GAConfig(population_size=20, generations=20, seed=123)
    first = BasicGeneticAlgorithm(config).run()
    second = BasicGeneticAlgorithm(config).run()
    assert first["best_solution"] == second["best_solution"]
    assert first["history"] == second["history"]


def test_config_rejects_invalid_population():
    try:
        GAConfig(population_size=2)
    except ValueError as exc:
        assert "population_size" in str(exc)
    else:
        raise AssertionError("Expected invalid population size to raise ValueError")
