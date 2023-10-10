import sys
import re

def parse_line(line):
    """Parse a line and return relation name and its arguments."""
    match = re.match(r'(\w+)\(([^)]+)\)', line)
    if match:
        relation, args = match.groups()
        args = tuple(args.split(','))
        return relation, args
    return None

def evaluate_rules(facts, rules):
    """Evaluate rules to produce new facts."""
    new_facts = set()
    
    for rule in rules:
        head, body = rule
        body_relations, body_args = zip(*body)
        
        # Cartesian product of possible argument combinations
        combos = [facts.get(rel, []) for rel in body_relations]
        for values in product(*combos):
            bindings = {}
            valid_combination = True
            for arg, value, expected_arg in zip(body_args, values, head[1]):
                if expected_arg.isupper():  # variable
                    if expected_arg in bindings:
                        if bindings[expected_arg] != value:
                            valid_combination = False
                            break
                    else:
                        bindings[expected_arg] = value
                else:  # constant
                    if expected_arg != value:
                        valid_combination = False
                        break
            
            if valid_combination:
                new_fact_args = tuple(bindings.get(arg, arg) for arg in head[1])
                new_facts.add((head[0], new_fact_args))
                
    return new_facts

def product(*args):
    """A helper function to get Cartesian product of input lists."""
    if not args:
        return [()]
    return [(a,) + rest for a in args[0] for rest in product(*args[1:])]

def naive_sdl_interpreter(filename):
    """Naive interpreter for .sdl format."""
    facts = {}
    rules = []
    
    # Parse the .sdl input from file
    with open(filename, 'r') as f:
        for line in f.readlines():
            parsed = parse_line(line.strip())
            if not parsed:
                continue
            relation, args = parsed
            if ':-' in ','.join(args):  # Ensure ":-" is present in the arguments
                head_relation, remaining = relation, ','.join(args)
                head_args = tuple(re.findall(r'\w+', remaining.split(':-')[0]))
                head = (head_relation, head_args)
                body_str = remaining.split(':-')[1]
                body = [parse_line(part.strip()) for part in body_str.split(',')]
                rules.append((head, body))
            else:  # Fact
                if relation not in facts:
                    facts[relation] = set()
                facts[relation].add(args)
    
    # Naive evaluation
    while True:
        new_facts = evaluate_rules(facts, rules)
        if not any(((rel, args) not in facts.get(rel, set())) for rel, args in new_facts):
            break
        for rel, args in new_facts:
            if rel not in facts:
                facts[rel] = set()
            facts[rel].add(args)
    
    # Write to .tsv files
    for relation, tuples in facts.items():
        with open(f'{relation}.tsv', 'w') as f:
            for t in tuples:
                f.write('\t'.join(map(str, t)) + '\n')

def semi_naive_evaluate_rules(facts, delta, rules):
    """Semi-naive evaluation of rules."""
    new_facts = set()
    new_delta = {}
    
    for rule in rules:
        head, body = rule
        body_relations, body_args = zip(*body)
        
        combos = [delta.get(rel, facts.get(rel, [])) for rel in body_relations]
        for values in product(*combos):
            bindings = {}
            valid_combination = True
            for arg, value, expected_arg in zip(body_args, values, head[1]):
                if expected_arg.isupper():  # variable
                    if expected_arg in bindings:
                        if bindings[expected_arg] != value:
                            valid_combination = False
                            break
                    else:
                        bindings[expected_arg] = value
                else:  # constant
                    if expected_arg != value:
                        valid_combination = False
                        break
            
            if valid_combination:
                new_fact_args = tuple(bindings.get(arg, arg) for arg in head[1])
                new_fact = (head[0], new_fact_args)
                new_facts.add(new_fact)
                if new_fact not in facts.get(head[0], set()):
                    if head[0] not in new_delta:
                        new_delta[head[0]] = set()
                    new_delta[head[0]].add(new_fact_args)
    
    return new_facts, new_delta

def semi_naive_sdl_interpreter(filename):
    """Semi-naive interpreter for .sdl format."""
    facts = {}
    rules = []
    
    # Parsing logic remains unchanged
    with open(filename, 'r') as f:
        for line in f.readlines():
            parsed = parse_line(line.strip())
            if not parsed:
                continue
            relation, args = parsed
            if ':-' in ','.join(args):  # Ensure ":-" is present in the arguments
                head_relation, remaining = relation, ','.join(args)
                head_args = tuple(re.findall(r'\w+', remaining.split(':-')[0]))
                head = (head_relation, head_args)
                body_str = remaining.split(':-')[1]
                body = [parse_line(part.strip()) for part in body_str.split(',')]
                rules.append((head, body))
            else:  # Fact
                if relation not in facts:
                    facts[relation] = set()
                facts[relation].add(args)
    # Initial delta is the same as facts
    delta = {relation: set(tuples) for relation, tuples in facts.items()}
    
    while delta:
        new_facts, delta = semi_naive_evaluate_rules(facts, delta, rules)
        for rel, args in new_facts:
            if rel not in facts:
                facts[rel] = set()
            facts[rel].add(args)
    
    for relation, tuples in facts.items():
        with open(f'{relation}.tsv', 'w') as f:
            for t in tuples:
                f.write('\t'.join(map(str, t)) + '\n')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 datalog.py <filename>.sdl")
        sys.exit(1)
    naive_sdl_interpreter(sys.argv[1])
    # semi_naive_sdl_interpreter(sys.argv[1])


# # Example usage:
# sdl_input = """
# edge(1,2)
# edge(2,3)
# transitiveEdge(X,Y) :- edge(X,Y)
# transitiveEdge(X,Y) :- edge(X,Z), transitiveEdge(Z,Y)
# """