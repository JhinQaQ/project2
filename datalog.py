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

def evaluate_rules(facts):
    """Evaluate rules to produce new facts."""
    new_facts = set()

    # Initialize path facts with edge facts
    facts['path'] = set(facts.get('edge', []))

    # Flag to track if any new facts are added in each iteration
    added_new_fact = True

    while added_new_fact:
        added_new_fact = False

        # For each path(x, y) and edge(y, z), if path(x, z) is not in facts, add it
        for (x, y) in facts['path']:
            for (y_prime, z) in facts.get('edge', []):
                if y == y_prime and (x, z) not in facts['path']:
                    new_facts.add((x, z))
                    added_new_fact = True

        # Update the path facts with new facts
        for new_fact in new_facts:
            facts['path'].add(new_fact)

        new_facts.clear()

    return facts

def naive_sdl_interpreter(filename):
    """Naive interpreter for .sdl format."""
    facts = {}

    # Parse the .sdl input from file
    with open(filename, 'r') as f:
        for line in f.readlines():
            parsed = parse_line(line.strip())
            if not parsed:
                continue
            relation, args = parsed
            if relation not in facts:
                facts[relation] = set()
            facts[relation].add(args)

    # Apply rules to derive new facts
    facts = evaluate_rules(facts)

    # Write path relation to a CSV file
    with open('path.csv', 'w') as f:
        for x, y in sorted(facts['path'], key=lambda pair: (int(pair[0]), int(pair[1]))):
            f.write(f'{x}\t{y}\n')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 datalog.py <filename>.sdl")
        sys.exit(1)
    naive_sdl_interpreter(sys.argv[1])
