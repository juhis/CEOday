#!/usr/bin/env python3

# directly from https://github.com/Shivashish1010/Simplify-Debts/blob/e049e7466e604253a3ce0574d5623f62e2ff1eef/simplify_debts.py
# added tsv debt file read
# run: python3 simplify_debts.py debt.tsv

from collections import defaultdict
import heapq
import sys


def simplify_debts(transactions):
    total = defaultdict(int)

    for transaction in transactions:
        giver, receiver, amount = transaction
        total[giver] -= amount
        total[receiver] += amount

    credit = []
    debit = []

    for name, amount in total.items():
        if amount > 0:
            credit.append((-amount, name))
        if amount < 0:
            debit.append((amount, name))

    heapq.heapify(credit)
    heapq.heapify(debit)
    answer = []

    while credit and debit:
        credit_value, credit_name = heapq.heappop(credit)
        debit_value, debit_name = heapq.heappop(debit)

        if credit_value < debit_value:
            amount_left = credit_value - debit_value
            answer.append((debit_name, credit_name, -1 * debit_value))
            heapq.heappush(credit, (amount_left, credit_name))

        elif debit_value < credit_value:
            amount_left = debit_value - credit_value
            answer.append((debit_name, credit_name, -1 * credit_value))
            heapq.heappush(debit, (amount_left, debit_name))

        else:
            answer.append((debit_name, credit_name, -1 * credit_value))

    return answer


transactions = []
with open(sys.argv[1], "rt") as f:
    names = f.readline().strip().split("\t")
    for line in f:
        s = line.strip().split("\t")
        for i in range(1, len(s)):
            transactions.append([s[0], names[i], float(s[i])])

print("TO\tFROM\tAMOUNT")
for m in simplify_debts(transactions):
    print(m[0] + "\t" + m[1] + "\t" + str(round(m[2], 2)))
