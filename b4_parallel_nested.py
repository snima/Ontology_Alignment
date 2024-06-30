from owlready2 import *
from rdflib import Graph, URIRef
import Levenshtein as lev
from isub import isub
import multiprocessing as mp

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

# Function to find lexical matches between two ontologies
def find_lexical_matches(onto1, onto2, threshold=0.8):
    ontology1_iri = onto1.base_iri
    ontology2_iri = onto2.base_iri
    
    entities1 = list(onto1.classes())
    entities2 = list(onto2.classes())
    
    # Create pairs of entity IRIs to compare
    entity_pairs = [(entity1.iri, entity2.iri) for entity1 in entities1 for entity2 in entities2]
    
    # Use multiprocessing to calculate similarities in parallel
    pool = mp.Pool(mp.cpu_count())
    results = pool.starmap(calculate_similarity, [(ontology1_iri, ontology2_iri, pair, threshold) for pair in entity_pairs])
    pool.close()
    pool.join()
    
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

# Load anatomy ontologies
onto_mouse = load_ontology("data/mouse.owl")
onto_human = load_ontology("data/human.owl")

# Find lexical matches
matches_anatomy = find_lexical_matches(onto_mouse, onto_human)

# Save matches as RDF
save_matches_as_rdf(matches_anatomy, "output/mouse-human-matches.ttl")

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

# Evaluate mappings for anatomy track
compare_with_reference("data/anatomy-reference-mappings.ttl", "output/mouse-human-matches.ttl")

