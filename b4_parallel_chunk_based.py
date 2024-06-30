import time
from owlready2 import *
from rdflib import Graph, URIRef
import Levenshtein as lev
from isub import isub
import multiprocessing as mp
import threading

# Function to load ontology
def load_ontology(uri):
    return get_ontology(uri).load()

# Function to get labels for an entity
def get_labels(entity):
    return entity.label

# Function to get entity by IRI from an ontology
def get_entity_by_iri(ontology, iri):
    return ontology.search_one(iri=iri)

# Function to calculate similarity between labels and check against threshold
def calculate_similarity(ontology1_iri, ontology2_iri, entity_pair, threshold=0.8):
    ontology1 = get_ontology(ontology1_iri).load()
    ontology2 = get_ontology(ontology2_iri).load()
    entity1_iri, entity2_iri = entity_pair
    entity1 = get_entity_by_iri(ontology1, entity1_iri)
    entity2 = get_entity_by_iri(ontology2, entity2_iri)
    
    matches = []
    labels1 = get_labels(entity1)
    labels2 = get_labels(entity2)
    for label1 in labels1:
        for label2 in labels2:
            similarity = max(lev.jaro_winkler(label1, label2), isub(label1, label2))
            if similarity >= threshold:
                matches.append((entity1_iri, entity2_iri, similarity))
    return matches

# Split list into chunks
def chunkify(lst, n):
    return [lst[i::n] for i in range(n)]

# Function to process a chunk of entity pairs
def process_chunk(ontology1_iri, ontology2_iri, entity_pairs_chunk, threshold):
    matches = []
    for pair in entity_pairs_chunk:
        matches.extend(calculate_similarity(ontology1_iri, ontology2_iri, pair, threshold))
    return matches

# Function to find lexical matches between two ontologies using threading for I/O operations
def find_lexical_matches(onto1, onto2, threshold=0.8):
    start_time = time.time()  # Start timing the entire lexical matching process

    entities1 = list(onto1.classes())
    entities2 = list(onto2.classes())

    # Create pairs of entity IRIs to compare
    entity_pairs = [(entity1.iri, entity2.iri) for entity1 in entities1 for entity2 in entities2]

    # Split entity pairs into chunks
    num_chunks = mp.cpu_count()
    entity_pairs_chunks = chunkify(entity_pairs, num_chunks)

    # Use threading to load ontologies in parallel (I/O bound)
    def load_ontology_threaded(ontology):
        try:
            ontology.load()
        except OwlReadyOntologyParsingError as e:
            print(f"Error loading ontology: {e}")

    threads = []
    for ontology in [onto1, onto2]:
        thread = threading.Thread(target=load_ontology_threaded, args=(ontology,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Use multiprocessing to calculate similarities in parallel (CPU bound)
    with mp.Pool(num_chunks) as pool:
        results = pool.starmap(process_chunk, [(onto1.base_iri, onto2.base_iri, chunk, threshold) for chunk in entity_pairs_chunks])

    # Flatten the list of results
    matches = [match for sublist in results for match in sublist]

    end_time = time.time()  # End timing the entire lexical matching process
    print(f"Time taken to find lexical matches: {end_time - start_time} seconds")

    return matches

# Function to save matches as RDF
def save_matches_as_rdf(matches, output_file):
    start_time = time.time()  # Start timing the RDF saving process

    g = Graph()
    for match in matches:
        entity1_iri, entity2_iri, similarity = match
        g.add((URIRef(entity1_iri), URIRef("http://www.w3.org/2002/07/owl#equivalentClass"), URIRef(entity2_iri)))
    g.serialize(destination=output_file, format='turtle')

    end_time = time.time()  # End timing the RDF saving process
    print(f"Time taken to save matches as RDF: {end_time - start_time} seconds")

# Load anatomy ontologies
start_time = time.time()  # Start timing the ontology loading process
onto_mouse = get_ontology("data/mouse.owl")
onto_human = get_ontology("data/human.owl")
clear_logics()  # Clear ontology cache
end_time = time.time()  # End timing the ontology loading process
print(f"Time taken to initiate ontology loading: {end_time - start_time} seconds")

# Find lexical matches
matches_anatomy = find_lexical_matches(onto_mouse, onto_human)

# Save matches as RDF
save_matches_as_rdf(matches_anatomy, "output/mouse-human-matches.ttl")

# Function to compare with reference alignments
def compare_with_reference(reference_mappings_file, system_mappings_file):
    start_time = time.time()  # Start timing the comparison process

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

    end_time = time.time()  # End timing the comparison process
    print(f"Time taken to compare with reference: {end_time - start_time} seconds")

    print(f"Comparing '{system_mappings_file}' with '{reference_mappings_file}'")
    print(f"\tPrecision: {precision}")
    print(f"\tRecall: {recall}")
    print(f"\tF-Score: {f_score}")

# Evaluate mappings for anatomy track
compare_with_reference("data/anatomy-reference-mappings.ttl", "output/mouse-human-matches.ttl")

