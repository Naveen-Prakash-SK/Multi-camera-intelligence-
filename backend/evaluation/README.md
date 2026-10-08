# Video Intelligence Evaluation Framework

This directory contains the integration and ablation evaluation framework for the HNX26EPS05 Multi-Camera Video Intelligence backend.

## Contents
- `queries.json`: The test dataset of natural language queries.
- `expected_results.json`: The expected structured results and ground-truth validation criteria.
- `evaluate.py`: The evaluation runner that performs the ablation study (Baseline vs. Full System).

## Running the Evaluation
To run the evaluation ablation study, simply execute:
```bash
python evaluate.py
```

## Metrics Tracked
1. **Retrieval Accuracy**: Did Qdrant return the correct frame in the Top-K?
2. **Camera Accuracy**: Did the LLM Scene Memory map correctly to the right camera?
3. **Timestamp Accuracy**: Did the event happen within ±2 seconds of the returned timestamp?
4. **Evidence Accuracy**: Is the answer fully grounded in the returned evidence?
5. **False Positive Rate**: How often did the system hallucinate a match?
6. **VLM Verification Precision**: Did the VLM correctly filter out false positives from Qdrant/OwlViT?
7. **Latency**: Breakdowns for parsing, embeddings, indexing, and VLM.

## Re-ID and Memory
- Cross-camera Re-ID is evaluated using strict Cosine Similarity bounds.
- Memory persistence is tested separately via `test_clarify_once.py` in the root directory.
