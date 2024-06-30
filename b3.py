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

# Pairs of ontologies for conference track
pairs = [
    ("data/cmt.owl", "data/ekaw.owl", "output/cmt-ekaw-matches.ttl"),
    ("data/cmt.owl", "data/confOf.owl", "output/cmt-confof-matches.ttl"),
    ("data/confOf.owl", "data/ekaw.owl", "output/confof-ekaw-matches.ttl")
]

for onto1_path, onto2_path, output_path in pairs:
    onto1 = load_ontology(onto1_path)
    onto2 = load_ontology(onto2_path)
    matches = find_lexical_matches(onto1, onto2)
    save_matches_as_rdf(matches, output_path)

