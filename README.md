# Ontology Alignment and Parallel Computing Optimization

## Overview

This project aims to enhance the efficiency of ontology alignment tasks using parallel computing techniques. We focus on aligning ontologies from the OAEI Conference and Anatomy tracks by implementing lexical similarity measures to identify equivalent classes and properties across ontologies.

## Contents

- [Description](#description)
- [Tasks](#tasks)
  - [Task 3: Ontology Alignment in OAEI Conference Track](#task-3-ontology-alignment-in-oaei-conference-track)
  - [Task 4: Ontology Alignment in OAEI Anatomy Track](#task-4-ontology-alignment-in-oaei-anatomy-track)
- [Parallel Computing Optimization](#parallel-computing-optimization)
  - [Strategies Implemented](#strategies-implemented)
  - [Results](#results)
- [Conclusion](#conclusion)
- [Usage](#usage)
  - [Prerequisites](#prerequisites)
  - [Running the Code](#running-the-code)
  - [Evaluation](#evaluation)
- [License](#license)

## Description

The project involves:
1. Loading and processing ontologies using the Owlready2 library.
2. Computing lexical similarities using the Levenshtein distance and ISUB methods.
3. Generating RDF alignments in Turtle format.
4. Evaluating the alignments against reference mappings using precision, recall, and F-score metrics.
5. Implementing parallel computing strategies to improve efficiency in handling large-scale ontology alignment tasks.

## Tasks

### Task 3: Ontology Alignment in OAEI Conference Track

- **Objective:** Align entities between pairs of ontologies (`cmt.owl`, `ekaw.owl`, `confOf.owl`).
- **Steps:**
  - Load ontologies using Owlready2.
  - Compute lexical similarities.
  - Generate RDF alignments.
  - Evaluate alignments using precision, recall, and F-score.

### Task 4: Ontology Alignment in OAEI Anatomy Track

- **Objective:** Align entities between large-scale ontologies (`mouse.owl` and `human.owl`).
- **Steps:**
  - Load ontologies.
  - Compute lexical similarities.
  - Implement parallel computing to handle large datasets.
  - Generate and evaluate RDF alignments.

## Parallel Computing Optimization

### Strategies Implemented

1. **Nested Loop Parallelization:**
   - Utilized Python's multiprocessing library to parallelize the comparison of entity labels.
   - Distributed nested loops across multiple processes for efficient computation.

2. **Chunk-based Parallelization:**
   - Split entity pairs into chunks and processed them in parallel.
   - Enhanced granularity in parallel execution, optimizing resource utilization.

### Results

- **Execution Time:**
  - Sequential Time: 1006.96 seconds
  - Parallel Time (Nested Loop): 189.26 seconds
  - Parallel Time (Chunk-based): 356.92 seconds
- **Accuracy:**
  - Consistent precision and recall metrics across all methods:
    - Precision: 0.5974
    - Recall: 0.6313
    - F-Score: 0.6139
- **Speedup:**
  - Significant reduction in computation time with both parallelization strategies.

## Conclusion

The implementation of parallel computing techniques significantly enhances the efficiency of ontology alignment tasks without compromising accuracy. This project demonstrates the practical benefits of parallelization in large-scale semantic web applications, making ontology integration faster and more efficient.

## Usage

### Prerequisites

- Python 3.x
- Owlready2
- rdflib
- Levenshtein
- isub
- Multiprocessing library (standard in Python)

### Running the Code

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ontology-alignment-parallel
   cd ontology-alignment-parallel
