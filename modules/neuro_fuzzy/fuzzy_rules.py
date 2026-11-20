def rule_descriptions():
    return [
      "IF x is Low AND y is Low THEN output = p1*x + q1*y + r1",
      "IF x is Low AND y is High THEN output = p2*x + q2*y + r2",
      "IF x is High AND y is Low THEN output = p3*x + q3*y + r3",
      "IF x is High AND y is High THEN output = p4*x + q4*y + r4",
    ]
