# Axiom

> Embedding models make implicit judgments about political and economic concepts. This project measures them, measures where models disagree and asks what happens when those disagreements end up inside your search and recommendation engines.

**Axiom** is a multi model semantic analysis pipeline designed to measure the implicit sentiments and value systems encoded within modern embedding models.

Standard benchmarks (like [MTEB](https://huggingface.co/spaces/mteb/leaderboard)) evaluate retrieval performance but fail to capture structural ideological biases. Axiom bridges this gap by using semantic axis projection to evaluate how models from different geographic and institutional origins score political, economic and value-laden concepts.

### Companion Materials

This codebase serves as the technical foundation for the following research and writing:

- **Paper:** _Do Embedding Models Have a Moral Compass?_ ([`paper.pdf`](/paper/paper.pdf))
- **Interactive Essay:** [Do Models Dream of Fascist Sheep?](https://blog.studiohaynes.com/essays/do-models-dream-of-fascist-sheep.html)

## Components

1. [jupyter notebook](/pipeline/): main data analysis pipeline
2. [svelte companion explorer app](/data_explorer/): for in browser data manipulation

## Installation

```
TODO
```

## Usage

The primary pipeline is driven by jupyter notebook. It loads the targeted models, processes the terms and generates the output data.

```
TODO
```

## Data Artifacts

Running the pipeline generates a suite of artifacts mapping model consensus, disagreement and rankings. The core outputs include:

- TODO

## Methodology Briefly Explained

Instead of measuring how similar a term is to "Good" and "Evil" separately, the pipeline subtracts the "Evil" embedding from the "Good" embedding to create a directional axis. Terms are then projected onto this axis. To allow fair comparison across different models, the resulting scores are Z-score normalized (recentering the mean to zero) and passed through a `tanh` scaling function to gently compress extreme values.
