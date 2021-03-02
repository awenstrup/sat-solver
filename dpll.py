import pytest

class SAT:
    def __init__(self, s: str):
        """ Initialize a SAT problem
        Args:
            s is of the format "[a b]-[.x .y z]-[p .q r s]"
            * each inner list represents a clause of ORed elements
            * all inner lists are ANDed together
            * dots before a variable denote that they are inverted
        """
        self.variables = {} # str: bool
        self.clauses = {} # str: {str: Union[bool, str], str: set}

        for clause in s.split("-"):
            d = self.clauses[clause] = {}
            d["status"] = "unknown"
            d["variables"] = set()
            for variable in clause.strip("[]").split():
                d["variables"].add(variable)
                self.variables[variable.strip(".")] = "unknown"
    
    def state(self):
        """Assuming clauses are up to date, return the state of the SAT"""
        if False in {x["status"] for x in self.clauses.values()}:
            return False
        if "unknown" in {x["status"] for x in self.clauses.values()}: 
            return "unknown"
        return True

    def update(self, changes: dict):
        """Update the variables and clauses of the SAT to reflect
        a dictionary of changes"""
        for v in changes:
            self.variables[v] = changes[v]
        
        for s, clause in self.clauses.items():
            for var in clause["variables"]:
                if var in changes or var.strip(".") in changes:
                    self.update_clause(s)
    
    def update_clause(self, c: str):
        """Update a specific clause, given the string that represents it"""
        unknown_flag = False
        clause = self.clauses[c]
        for var in clause["variables"]:
            val = self.variables[var.strip(".")]
            if var.startswith("."):
                val = not val 
            if val == True:
                clause["status"] = True
                return
            elif val == "unknown":
                unknown_flag = True
        
        # if we make it out of the for loop without a True, return unknown_flag
        clause["status"] = "unknown" if unknown_flag else False
        
    def update1(self, b):
        """Create a new SAT, and update a single, arbitrary, 
        unassigned variable in the new SAT"""
        out = SAT("")
        out.variables = dict(self.variables)
        out.clauses = dict(self.clauses)

        for var, val in out.variables.items():
            if val == "unknown": 
                out.update({var: b})
                return out

def sat_checker(sat):
    if (sat.state() != "unknown"): return sat.state(), sat.variables
    else: 
        a, v1 = sat_checker(sat.update1(True))
        if a: return True, v1
        
        b, v2 = sat_checker(sat.update1(False))
        if b: return True, v2
        
        return False, None

def test_sat_checker():
    s = SAT("[a]")
    result, values = sat_checker(s)
    assert result
    assert values["a"] == True

    s = SAT("[a b]")
    result, values = sat_checker(s)
    assert result
    assert (values["a"] == True or values["b"] == True)

    s = SAT("[a]-[.a]")
    result, values = sat_checker(s)
    assert result == False

    s = SAT("[a]-[.a a]-[b .a .b]-[c d e]-[.b .e a]-[.d]-[e]-[.e .d]")
    result, values = sat_checker(s)
    assert result == True
    assert values["a"] == True
    assert values["d"] == False

if __name__=="__main__":
    s = SAT("[a]-[.a a]-[b .a .b]-[.c d e]-[.b .e a]-[.d]-[e]-[.e .d]")
    s2 = SAT("[a b]")
    print(sat_checker(s))

