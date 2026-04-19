# Axiom

**Axiom** is a multi model semantic analysis pipeline designed to measure the implicit sentiments and value systems encoded within modern embedding models.

Standard benchmarks (like [MTEB](https://huggingface.co/spaces/mteb/leaderboard)) evaluate retrieval performance but fail to capture structural ideological biases. Axiom bridges this gap by using semantic axis projection to evaluate how models from different geographic and institutional origins score political, economic and value-laden concepts.

## Video guide

https://youtu.be/xDg8kd9nopQ

## Example App

https://matthewhaynesonline.github.io/Axiom/

## Companion Materials

This codebase serves as the technical foundation for the following research and writing:

- **Paper:** _Do Embedding Models Have a Moral Compass?_ ([`paper.pdf`](/paper/paper.pdf))
- **Interactive Essay:** [Do Models Dream of Fascist Sheep?](https://blog.studiohaynes.com/go/axiom)

## Components

1. [jupyter notebook](/pipeline/): main data analysis pipeline
2. [svelte companion explorer app](/data_explorer/): for in browser data manipulation

### Pipeline Process

1. load models
   1. `models = ml_models.ModelConfig.load_models("models.csv", ENABLED_MODELS)`
2. load data
   1. `data_df = pl.read_csv(SOURCE_DATA)`
3. Create batches of terms to embed in one go (vs calling embed over and over again)
   1. `doc_boundaries`
4. for model in models
   1. precompute embeddings
      1. `axiom_lib.embeddings.precompute_embeddings_bulk(`
   2. basic process data for terms and judgements
      1. `data = axiom_lib.pipeline.process_data`
         1. This calcs
            1. the similarity `scores = model.similarity(a_embeddings, b_embeddings)`
            2. zscore `pl.col("score").map_batches(zscore).alias("score_z"),`
            3. zscore norm'd `.map_batches(lambda s: minmax(zscore(s))).alias("score_norm"),`
      2. **HOWEVER, these zscore / zscore norm aren't used for axis projection / it is a v1 per term data**
5. build and export axis data
   1. for processed results
      1. build averages
         1. `avgs = pipeline.build_all_avgs`
      2. write
         1. `final_axis_df.write_ipc`
6. Generate value systems ranking data

#### Notes

1. why references to +- 0.5 scale
   1. This was a quirk of the old min max approach (prior to z-score)
   2. minmax does 0 - 1, so if 0.5 is mid point (neutral) shift by 0.5 to make mid point 0
2. axis data is computed when generating plots in the old notebook code too

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
