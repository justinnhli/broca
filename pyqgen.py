#!/usr/bin/env python3

from random import random, randrange

from networkx import DiGraph
from networkx.drawing.nx_agraph import to_agraph as to_dot, write_dot

class ControlFlowGraph:
    def __init__(self):
        self.graph = DiGraph()
        self.entry = self.create_block()
        self.exit = self.create_block()
        self.create_successor(self.entry, self.exit)
    def create_block(self):
        block = Block()
        self.graph.add_node(block)
        return block
    def create_successor(self, before_block, new_block=None):
        if new_block is None:
            new_block = self.create_block()
        self.graph.add_edge(before_block, new_block)
        return new_block
    def insert_blocks(self, block, entry_block, exit_block):
        successors = self.graph.successors(block)
        assert len(successors) == 1
        self.create_successor(block, entry_block)
        self.create_successor(exit_block, successors[0])
        self.graph.remove_edge(block, successors[0])
    def simplify(self):
        obsolete_blocks = []
        for block in self.graph.nodes_iter():
            predecessors = self.graph.predecessors(block)
            successors = self.graph.successors(block)
            if len(predecessors) == len(successors) == 1:
                in_laws = self.graph.predecessors(successors[0])
                if len(in_laws) == 1:
                    self.graph.remove_edge(predecessors[0], block)
                    self.graph.remove_edge(block, successors[0])
                    self.graph.add_edge(predecessors[0], successors[0])
                    obsolete_blocks.append(block)
        for block in obsolete_blocks:
            self.graph.remove_node(block)
    def add_if(self, block, has_else=False, num_elif=0):
        condition_block = self.create_block()
        true_block = self.create_successor(condition_block)
        conditions = [condition_block]
        branches = [true_block]
        for i in range(num_elif):
            condition_block = self.create_successor(condition_block)
            branch_block = self.create_successor(condition_block)
            conditions.append(condition_block)
            branches.append(branch_block)
        if has_else:
            false_block = self.create_successor(condition_block)
            branches.append(false_block)
        after_block = self.create_successor(true_block)
        if not has_else:
            self.create_successor(condition_block, after_block)
        for branch_block in branches[1:]:
            self.create_successor(branch_block, after_block)
        self.insert_blocks(block, conditions[0], after_block)
        return IfBlock(conditions, branches)
    def add_while(self, block):
        condition_block = self.create_block()
        body_block = self.create_successor(condition_block)
        self.create_successor(body_block, condition_block)
        after_block = self.create_successor(condition_block)
        self.insert_blocks(block, condition_block, after_block)
        return WhileBlock(condition_block, body_block)
    def to_dot(self):
        return to_dot(self.graph).to_string()
    def write_dot(self, path):
        write_dot(self.graph, path)

class Block:
    BLOCK_ID = 0
    def __init__(self, **kwargs):
        self.block_id = Block.BLOCK_ID
        Block.BLOCK_ID += 1
        self.lines = []
        self.live_vars = {}
        self.kill_vars = {}
    def __hash__(self):
        return self.block_id
    def __eq__(self, other):
        return self.block_id == other.block_id
    def __str__(self):
        return str(self.block_id)

class IfBlock(Block):
    def __init__(self, conditions, bodies):
        super().__init__()
        self.conditions = conditions
        self.bodies = bodies

class WhileBlock(Block):
    def __init__(self, condition, body):
        super().__init__()
        self.condition = condition
        self.body = body

def generate_structure(has_branches, has_loops):
    cfg = ControlFlowGraph()
    entry = cfg.entry
    if has_loops:
        while_block = cfg.add_while(entry)
        entry = while_block.body
    if has_branches:
        rand = randrange(3)
        if rand == 0:
            if_block = cfg.add_if(entry)
        elif rand == 1:
            if_block = cfg.add_if(entry, has_else=True)
        elif rand == 2:
            has_else = (randrange(2) == 1)
            num_elif = randrange(1, 3)
            if_block = cfg.add_if(entry, has_else=has_else, num_elif=num_elif)
    cfg.simplify()
    return cfg

def main():
    cfg = generate_structure(has_branches=(random() > 0.5), has_loops=(random() > 0.5))
    print(cfg.to_dot())

if __name__ == '__main__':
    main()
