#!/usr/bin/env python3
"""Run the real analyzer and validate its output against SVF's dumped ICFG."""
import argparse
from collections import defaultdict
from pathlib import Path
import re
import subprocess


def run(command, cwd):
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=30)
    (cwd / (Path(command[0]).name + '.log')).write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f'{command}: {result.stdout}{result.stderr}')


def graph(dot):
    nodes, ports, edges = {}, {}, []
    for line in dot.splitlines():
        match = re.match(r'\s*(Node0x[\da-f]+) \[.*label="\{(\w+ICFGNode)(\d+)(.*)', line)
        if match:
            address, kind, number, label = match.groups()
            nodes[address] = (int(number), kind, label)
            for port, call in re.findall(r'<(s\d+)>(0x[\da-f]+)', label):
                ports[address, port] = 'Node' + call
        match = re.match(r'\s*(Node0x[\da-f]+)(?::(s\d+))? -> (Node0x[\da-f]+)\[(.*)\];', line)
        if match:
            edges.append(match.groups())
    adjacency = defaultdict(list)
    for src, port, dst, attrs in edges:
        kind = 'call' if 'color=red' in attrs else 'ret' if 'color=blue' in attrs else 'intra'
        call = nodes[src][0] if kind == 'call' else nodes[ports[src, port]][0] if kind == 'ret' else None
        adjacency[nodes[src][0]].append((nodes[dst][0], kind, call))
    sources = [n for n, k, label in nodes.values() if k == 'FunEntryICFGNode' and re.search(r'fun: main(?:\\|\s)', label)]
    sinks = [n for n, k, label in nodes.values() if k == 'FunExitICFGNode' and re.search(r'fun: main(?:\\|\s)', label)]
    # SVF omits the function exit when main has no return path.
    assert len(sources) == 1 and len(sinks) <= 1, (sources, sinks)
    return adjacency, sources[0], sinks[0] if sinks else None


def reference(adjacency, source, sink):
    # An iterative search independent of the C++ DFS and its backtracking state.
    result = set()
    pending = [(source, (), (), frozenset())]
    while pending:
        node, stack, path, seen = pending.pop()
        state = (node, stack)
        if state in seen:
            continue
        path = path + (node,)
        seen = seen | {state}
        if node == sink:
            if not stack:
                result.add(path)
            continue
        for dst, kind, call in adjacency[node]:
            if kind == 'call':
                if call in stack:
                    continue
                next_stack = stack + (call,)
            elif kind == 'ret':
                if not stack or stack[-1] != call:
                    continue
                next_stack = stack[:-1]
            else:
                next_stack = stack
            pending.append((dst, next_stack, path, seen))
    return result


EXTRA = {
    'nested-repeat': 1,
    'branch-merge': 2,
    'recursive-repeat': 4,
    'mutual-recursion': 3,
    'no-exit': 0,
    'external': 1,
}


def main():
    repo = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfga', type=Path, required=True)
    parser.add_argument('--clang', type=Path, required=True)
    parser.add_argument('--assignment3', type=Path, default=repo / 'tests/reference')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out = args.out.resolve()
    args.out.mkdir(parents=True, exist_ok=True)
    expected = {'branch': 2, 'buffer': 4, 'loop': 1, 'multi-call': 1, 'simple-call': 1}
    cases = [('Assignment-2', p, expected[p.stem]) for p in sorted((repo / 'Assignment-2-CFA/Test-Cases').glob('*.c'))]
    cases += [('Assignment-3', p, 2 if p.stem in ('branch-call', 'CI-local') else 1) for p in sorted((args.assignment3.resolve() / 'Assignment-3-CFLR/Test-Cases').glob('*.c'))]
    assert len(cases) == 13, 'Expected 5 Assignment-2 and 8 Assignment-3 test files'
    for name, count in EXTRA.items():
        cases.append(('regression', repo / 'tests/regression' / (name + '.c'), count))
    rows = []
    for group, source, count in cases:
        directory = args.out / group / source.stem
        directory.mkdir(parents=True, exist_ok=True)
        bitcode = source.stem + '.bc'
        run([str(args.clang.resolve()), '-O0', '-g', '-Wno-main-return-type', '-emit-llvm', '-c', str(source.resolve()), '-o', bitcode], directory)
        run([str(args.cfga.resolve()), '-dump-icfg', bitcode], directory)
        lines = (directory / (bitcode + '.res.txt')).read_text().splitlines()
        paths = [tuple(int(n) for n in re.findall(r'\d+', line)) for line in lines if line.strip()]
        assert len(paths) == len(set(paths)), 'Duplicate paths'
        adjacency, start, end = graph((directory / 'icfg_initial.dot').read_text())
        assert set(paths) == reference(adjacency, start, end), source
        assert len(paths) == count, (source, len(paths), count)
        # Repeat the executable to verify deterministic results.
        run([str(args.cfga.resolve()), bitcode], directory)
        again = (directory / (bitcode + '.res.txt')).read_text()
        assert again == '\n'.join(lines) + ('\n' if lines else ''), source
        print(f'PASS {group}/{source.name}: {len(paths)} paths', flush=True)
        rows.append(f'| {group} | {source.name} | {len(paths)} | PASS |')
    (args.out / 'results.md').write_text('| Test set | Case | Paths | Result |\n|---|---|---:|---|\n' + '\n'.join(rows) + '\n')
    print(f'All {len(rows)} cases passed.')


if __name__ == '__main__':
    main()
