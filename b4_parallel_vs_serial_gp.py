from owlready2 import *
from rdflib import Graph, URIRef
import Levenshtein as lev
from isub import isub
import multiprocessing as mp
import time

# Function to load ontology
def load_ontology(uri):
    return get_ontology(uri).load()

# Function to get labels for an entity
def get_labels(entity):
    return list(entity.label)

# Function to calculate similarity between labels and check against threshold
def calculate_similarity(entity_pair, threshold=0.8):
    entity1_iri, entity1_labels, entity2_iri, entity2_labels = entity_pair
    matches = []
    for label1 in entity1_labels:
        for label2 in entity2_labels:
            similarity = max(lev.jaro_winkler(label1, label2), isub(label1, label2))
            if similarity >= threshold:
                matches.append((entity1_iri, entity2_iri, similarity))
    return matches

# Sequential version of find_lexical_matches
def find_lexical_matches_sequential(onto1, onto2, threshold=0.8):
    matches = []
    for entity1 in onto1.classes():
        for entity2 in onto2.classes():
            labels1 = get_labels(entity1)
            labels2 = get_labels(entity2)
            for label1 in labels1:
                for label2 in labels2:
                    similarity = max(lev.jaro_winkler(label1, label2), isub(label1, label2))
                    if similarity >= threshold:
                        matches.append((entity1.iri, entity2.iri, similarity))
    return matches

# Parallel version of find_lexical_matches
def find_lexical_matches_parallel(onto1, onto2, threshold=0.8):
    entities1 = [(entity.iri, get_labels(entity)) for entity in onto1.classes()]
    entities2 = [(entity.iri, get_labels(entity)) for entity in onto2.classes()]
    
    # Create pairs of entities to compare
    entity_pairs = [(entity1[0], entity1[1], entity2[0], entity2[1]) for entity1 in entities1 for entity2 in entities2]
    
    # Use multiprocessing to calculate similarities in parallel
    with mp.Pool(mp.cpu_count()) as pool:
        results = pool.starmap(calculate_similarity, [(pair, threshold) for pair in entity_pairs])
    
    # Flatten the list of results
    matches = [match for sublist in results for match in sublist]
    return matches

# Function to save matches as RDF
def save_matches_as_rdf(matches, output_file):
    g = Graph()
    for match in matches:
        entity1_iri, entity2_iri, similarity = match
        g.add((URIRef(entity1_iri), URIRef("http://www.w3.org/2002/07/owl#equivalentClass"), URIRef(entity2_iri)))
    g.serialize(destination=output_file, format='turtle')

# Function to compare with reference alignments
def compare_with_reference(reference_mappings_file, system_mappings_file):
    ref_mappings = Graph()
    ref_mappings.parse(reference_mappings_file, format="ttl")
    
    system_mappings = Graph()
    system_mappings.parse(system_mappings_file, format="ttl")
    
    tp = 0
    fp = 0
    fn = 0
    
    for t in system_mappings:
        if t in ref_mappings:
            tp += 1
        else:
            fp += 1

    for t in ref_mappings:
        if t not in system_mappings:
            fn += 1
            
    precision = tp / (tp + fp) if tp + fp > 0 else 0
    recall = tp / (tp + fn) if tp + fn > 0 else 0
    f_score = (2 * precision * recall) / (precision + recall) if precision + recall > 0 else 0
    
    print(f"Comparing '{system_mappings_file}' with '{reference_mappings_file}'")
    print(f"\tPrecision: {precision}")
    print(f"\tRecall: {recall}")
    print(f"\tF-Score: {f_score}")

# Main function to run and compare both versions
def main():
    # Load anatomy ontologies
    onto_mouse = load_ontology("data/mouse.owl")
    onto_human = load_ontology("data/human.owl")

    # Sequential version
    start_time = time.time()
    matches_anatomy_sequential = find_lexical_matches_sequential(onto_mouse, onto_human)
    sequential_time = time.time() - start_time
    save_matches_as_rdf(matches_anatomy_sequential, "output/mouse-human-matches-sequential.ttl")

    # Parallel version
    start_time = time.time()
    matches_anatomy_parallel = find_lexical_matches_parallel(onto_mouse, onto_human)
    parallel_time = time.time() - start_time
    save_matches_as_rdf(matches_anatomy_parallel, "output/mouse-human-matches-parallel.ttl")

    # Compare timings
    print(f"Sequential Time: {sequential_time} seconds")
    print(f"Parallel Time: {parallel_time} seconds")

    # Compare accuracy
    compare_with_reference("data/anatomy-reference-mappings.ttl", "output/mouse-human-matches-sequential.ttl")
    compare_with_reference("data/anatomy-reference-mappings.ttl", "output/mouse-human-matches-parallel.ttl")

if __name__ == "__main__":
    main()

