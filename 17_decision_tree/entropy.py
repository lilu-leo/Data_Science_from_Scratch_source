# coding=utf-8
from __future__ import division
from collections import Counter,  defaultdict
from functools import partial
import math, random

def entropy(class_probabilities):
    """given a list of class probabilities, compute the entropy"""

    return sum(-p * math.log(p, 2)
               for p in class_probabilities
               if p)


def class_probabilities(labels):
    total_count = len(labels)
    return [count / total_count
            for count in Counter(labels).values()
            ]

def data_entropy(label_data):
    labels = [label for _, label in label_data]
    probablities = class_probabilities(labels)
    return entropy(probablities)

def partition_entropy(subsets):
    '''find the entropy from this partition of data into subsets subsets is a list of lists of labeled data'''

    total_count = sum(len(subset) for subset in subsets)

    return sum(data_entropy(subset) * len(subset) / total_count
               for subset in subsets)


def partition_by(inputs, attribute):
    '''each input is a pair (attribute_dict, label). returns a dict : atttibute_value -> inputs'''

    groups = defaultdict(list)
    for input in inputs:
        key = inputs[0][attribute]
        groups[key].append(input)

    return groups


def group_by(items, key_fn):
    """returns a defaultdict(list), where each input item 
    is in the list whose key is key_fn(item)"""
    groups = defaultdict(list)
    for item in items:
        key = key_fn(item)
        groups[key].append(item)
    return groups


def partition_by(inputs, attribute):
    """returns a dict of inputs partitioned by the attribute
    each input is a pair (attribute_dict, label)"""
    return group_by(inputs, lambda x: x[0][attribute])

def partition_entropy_by(inputs, attribute):
    '''computes the entropy corresponding to the given partition'''
    partitions = partition_by(inputs, attribute)
    return partition_entropy(partitions.values())

def classify(tree, input):
    '''classify the input using the given decision tree'''

    # 如果这是一个叶节点，则返回其值
    if tree in [True, False]:
        return tree

    # 否则这个树就包含一个需要划分的属性和一个字典，字典的键是那个属性的值
    # 值是下一步需要考虑的子树
    attribute, subtree_dict = tree

    subtree_key = input.get(attribute) # 如果没有输入的是缺失的属性，则返回None

    if subtree_key not in subtree_dict: # 如果键没有子树
        subtree_key = None              # 则需要用到None子树

    subtree = subtree_dict[subtree_key] #选择恰当的子树

    return classify(subtree, input)  # 并用它来对输入分类

def build_tree_id3(inputs, split_candidates=None):

    # 如果这是第一步
    # 第一次输入的所有的键就都是split candidates
    if split_candidates is None:
        split_candidates = inputs[0][0].keys()

    # 对输入里的True和False计数
    num_inputs = len(inputs)
    num_trues = len([label for item, label in inputs if label])
    num_false = num_inputs - num_trues

    if num_trues == 0 : return False # 若没有True，则返回一个"False"叶节点
    if num_false == 0 : return True # 若没有False，则返回一个"True"叶节点

    if not split_candidates:            # 若不再有split candidates
        return num_trues >= num_false   # 则返回多数叶节点

    # 否则在最好的属性上进行划分
    best_attribute = min(split_candidates, key=partial(partition_by, inputs))

    partitions = partition_by(inputs, best_attribute)
    new_candidates = [a for a in split_candidates
                      if  a != best_attribute]

    # 递归地创建子树
    subtrees = { attribute_value : build_tree_id3(subset, new_candidates)
                 for attribute_value, subset in partitions.iteritems()}

    subtrees[None] = num_trues > num_false

    return (best_attribute, subtrees)


if __name__ == "__main__":

    inputs = [
        ({'level':'Senior','lang':'Java','tweets':'no','phd':'no'},   False),
        ({'level':'Senior','lang':'Java','tweets':'no','phd':'yes'},  False),
        ({'level':'Mid','lang':'Python','tweets':'no','phd':'no'},     True),
        ({'level':'Junior','lang':'Python','tweets':'no','phd':'no'},  True),
        ({'level':'Junior','lang':'R','tweets':'yes','phd':'no'},      True),
        ({'level':'Junior','lang':'R','tweets':'yes','phd':'yes'},    False),
        ({'level':'Mid','lang':'R','tweets':'yes','phd':'yes'},        True),
        ({'level':'Senior','lang':'Python','tweets':'no','phd':'no'}, False),
        ({'level':'Senior','lang':'R','tweets':'yes','phd':'no'},      True),
        ({'level':'Junior','lang':'Python','tweets':'yes','phd':'no'}, True),
        ({'level':'Senior','lang':'Python','tweets':'yes','phd':'yes'},True),
        ({'level':'Mid','lang':'Python','tweets':'no','phd':'yes'},    True),
        ({'level':'Mid','lang':'Java','tweets':'yes','phd':'no'},      True),
        ({'level':'Junior','lang':'Python','tweets':'no','phd':'yes'},False)
    ]

    for key in ['level', 'lang', 'tweets', 'phd']:
        print key, partition_entropy_by(inputs, key)
    print

    senior_inputs = [(input, label)
                     for input, label in inputs if input["level"] == "Senior"]

    for key in ['lang', 'tweets', 'phd']:
        print key, partition_entropy_by(senior_inputs, key)
    print

    print "building the tree"
    tree = build_tree_id3(inputs)
    print tree

    print "Junior / Java / tweets / no phd", classify(tree,
        { "level" : "Junior",
          "lang" : "Java",
          "tweets" : "yes",
          "phd" : "no"} )

    print "Junior / Java / tweets / phd", classify(tree,
        { "level" : "Junior",
                 "lang" : "Java",
                 "tweets" : "yes",
                 "phd" : "yes"} )

    print "Intern", classify(tree, { "level" : "Intern" } )
    print "Senior", classify(tree, { "level" : "Senior" } )
