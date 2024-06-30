from owlready2 import *
from rdflib import Graph, URIRef
import Levenshtein as lev
from isub import isub

# Function to load ontology
def load_ontology(uri):
    return get_ontology(uri).load()

# Function to get labels for an entity
def get_labels(entity):
    return entity.label

# Function to find lexical matches between two ontologies
def find_lexical_matches(onto1, onto2, threshold=0.8):
    matches = []
    for entity1 in onto1.classes():
        for entity2 in onto2.classes():
            labels1 = get_labels(entity1)
            labels2 = get_labels(entity2)
            for label1 in labels1:
                for label2 in labels2:
                    similarity = max(lev.jaro_winkler(label1, label2), isub(label1, label2))
                    if similarity >= threshold:
                        matches.append((entity1, entity2, similarity))
    return matches

# Function to save matches as RDF
def save_matches_as_rdf(matches, output_file):
    g = Graph()
    for match in matches:
        entity1, entity2, similarity = match
        g.add((URIRef(entity1.iri), URIRef("http://www.w3.org/2002/07/owl#equivalentClass"), URIRef(entity2.iri)))
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

