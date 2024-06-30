from owlready2 import *
from rdflib import Graph, Namespace, URIRef

def load_ontology(uri):
    return get_ontology(uri).load()

def get_labels(entity):
    return entity.label

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

def save_matches_as_rdf(matches, output_file):
    g = Graph()
    for match in matches:
        entity1, entity2, similarity = match
        g.add((URIRef(entity1.iri), URIRef("http://www.w3.org/2002/07/owl#equivalentClass"), URIRef(entity2.iri)))
    g.serialize(destination=output_file, format='turtle')

# Load ontologies
onto1 = load_ontology("data/cmt.owl")
onto2 = load_ontology("data/ekaw.owl")

# Find lexical matches
matches = find_lexical_matches(onto1, onto2)

# Save matches as RDF
save_matches_as_rdf(matches, "output/cmt-ekaw-matches.ttl")

