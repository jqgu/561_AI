 
from decimal import Decimal;
import sys;

global nodes;
global dd;
JOINT_OR_MARGINAL = 1;
CONDITIONAL = 2;
JOINT_EU = 3;
CONDITIONAL_EU = 4;
JOINT_MEU = 5;
CONDITIONAL_MEU = 6;

class node:
    def __init__(self, line, file):
        self.node_name = "";
        self.occurance = "";
        self.parent_list = "";
        self.table = "";
        self.type = "";
        if line.find('|') == -1:
            self.node_name = line.strip();
            next_line = file.readline().strip();
            if next_line == "decision":
                self.type = 2;      #decision node
            else:
                self.occurance = float(next_line);
                self.type = 0;    #node without parent
            file.readline();
        else:
            longline = line.split("|");
            self.node_name = longline[0].strip();
            self.parent_list = get_parent(longline[1].strip());
            self.table = get_table(file, self.parent_list);
            if self.node_name != "utility":
                self.type = 1;          #normal node
            else:
                self.type = 3;  #utility node

    def get_prob(self, augument):
        if augument[0] == 0:
            if augument[1] == "+":
                return self.occurance;
            elif augument[1] == "-":
                return 1.0-self.occurance;
        elif augument[0] == 1:
            i = 2;
            para = "";
            while i != len(augument):
                para += augument[i]+" ";
                i = i+1;
            para = para.strip();
            prob = self.table.get(para);
            if augument[1] == "+":
                return prob;
            else:
                return 1.0-prob;
        elif augument[0] == 2:
            return 1.0;
        elif augument[0] == 3:
            i = 1;
            para = "";
            while i != len(augument):
                para += augument[i]+" ";
                i = i+1;
            para = para.strip();
            value = self.table.get(para);
            return value;

def get_parent(line):
    l = [];
    parents = line.split(" ");
    for p in parents:
        l.append(p);
    return l;
def get_table(file, parents):
    d = dict();
    line = file.readline().strip();
    while(line != "***" and line != "" and line != "******"):
        long_line = line.split(" ");
        value = float(long_line[0]);
        symbol = long_line[1:];
        evidence = "";
        for i in range(0, len(symbol)):
            if i != len(symbol)-1:
                evidence += (symbol[i]+parents[i]+" ");
            else:
                evidence += (symbol[i]+parents[i]);
        d[evidence] = value;
        line = file.readline().strip();
    return d;

def Joint(q):
    para = q[2: len(q)-1];
    variable = [];
    tmp = para.split(",");
    for p in tmp:
        tmp2 = p.split("=");
        symbol = tmp2[1].strip();
        var = symbol+tmp2[0].strip();
        variable.append(var);
    #print "var:";
    #print variable;
    hidden_variable = [];
    for v in variable:
        vv = v[1:];
        if nodes[dd.get(vv)].type == 0 or nodes[dd.get(vv)].type == 2:
            continue;
        else:
            for parent in nodes[dd.get(vv)].parent_list:
                if variable.count("+"+parent) != 0 or variable.count("-"+parent) != 0 or hidden_variable.count(parent) != 0 or hidden_variable.count(parent) != 0:
                    continue;
                else:
                    hidden_variable.append(parent);
    flag = 1;
    while flag == 1:
        flag = 0;
        for v in hidden_variable:
            if nodes[dd.get(v)].type == 0:
                continue;
            else:
                for parent in nodes[dd.get(v)].parent_list:
                    if hidden_variable.count(parent) != 0 or variable.count("+"+parent) != 0 or variable.count("-"+parent) != 0:
                        continue;
                    else:
                        hidden_variable.append(parent);
                        flag = 1;
    #print "hidden var:";
    #print hidden_variable;
    result = [0];
    enumerate(variable, hidden_variable, result);
    #result[0] = ("%.2f" % result[0]);
    #print result[0];
    return result[0];


def enumerate(variable, hidden_variable, result):
    if hidden_variable == []:
        calculate(variable, result);
        print variable;
        return;
    next_hidden_variable = hidden_variable.pop(0);
    tmp = "+"+next_hidden_variable;
    variable.append(tmp);
    enumerate(variable, hidden_variable, result);
    #############################################
    variable.remove(tmp);
    tmp = "-"+next_hidden_variable;
    variable.append(tmp);
    enumerate(variable, hidden_variable, result);
    #############################################
    variable.remove(tmp);
    hidden_variable.append(tmp[1:]);

def calculate(variable,result):
    #print variable;
    tmp = 1.0;
    for var in variable:
        symbol = var[0];
        node_var = nodes[dd.get(var[1:])];
        list = [node_var.type, symbol];
        if node_var.type == 0 or node_var.type == 2:
            tmp = tmp * node_var.get_prob(list);
        elif node_var.type == 1:
            parents = node_var.parent_list;
            for p in parents:
                if variable.count("+"+p) > 0:
                    list.append("+"+p);
                elif variable.count("-"+p) > 0:
                    list.append("-"+p);
            tmp = tmp * node_var.get_prob(list);
    print tmp;
    result[0] += tmp;
    #print result[0];


def Condition(q):
    pos = q.find('|');
    joint_query = q[0:pos-1]+","+q[pos+1:];
    joint_prob = Joint(joint_query);
    alfa_query = "P("+q[pos+2:];
    alfa_prob = Joint(alfa_query);
    return float(joint_prob)/float(alfa_prob);

def Joint_Utility(q):
    para = q[3: len(q)-1];
    para_list = para.split(", ");
    decision_node = [];
    other_node = [];
    for p in para_list:
        tmp = p.split(" = ");
        symbol = tmp[1];
        p_name = tmp[0];
        if nodes[dd.get(p_name)].type == 2:
            decision_node.append(symbol+p_name);
        else:
            other_node.append(symbol+p_name);
    utility_parents = nodes[dd.get("utility")].parent_list;
    utility_known_parents = [];
    utility_unknown_parents = [];
    for u_p in utility_parents:
        if decision_node.count("+"+u_p) > 0 or other_node.count("+"+u_p) > 0:
            utility_known_parents.append("+"+u_p);
        elif decision_node.count("-"+u_p) > 0 or other_node.count("-"+u_p) > 0:
            utility_known_parents.append("-"+u_p);
        else:
            utility_unknown_parents.append(u_p);
    #print "lalalala";
    result = [0, 0];
    eu_joint_enumerate(decision_node, other_node, utility_known_parents, utility_unknown_parents, result);
    return result[1];

def eu_joint_enumerate(d_node, other_ndoe, known_nodes, unknow_nodes, result):
    if unknow_nodes == []:
        variable = d_node + other_ndoe + known_nodes;
        variable = sorted(set(variable),key=variable.index)
        q = "P(";
        for i in range(0, len(variable)):
            symbol = variable[i][0];
            var_name = variable[i][1:];
            if i != len(variable)-1:
                q += var_name+" = "+symbol+", ";
            else:
                q += var_name+" = "+symbol+")";
        #print q;
        result[0] = Joint(q);

        var2 = d_node + other_ndoe;
        q = "P(";
        for i in range(0, len(var2)):
            symbol = var2[i][0];
            var_name = var2[i][1:];
            if i != len(var2)-1:
                q += var_name+" = "+symbol+", ";
            else:
                q += var_name+" = "+symbol+")";

        prob2 = Joint(q);
        result[0] = result[0]/prob2;

        calculate_eu(result, known_nodes);
        result[0] = 0;
        #print "lalala";
        return;
    next_utility_var = unknow_nodes.pop(0);
    tmp = "+"+next_utility_var;
    known_nodes.append(tmp);
    eu_joint_enumerate(d_node, other_ndoe, known_nodes, unknow_nodes, result);
    ######################################################################
    known_nodes.remove(tmp);
    tmp = "-"+next_utility_var;
    known_nodes.append(tmp);
    eu_joint_enumerate(d_node, other_ndoe, known_nodes, unknow_nodes, result);
    ######################################################################
    known_nodes.remove(tmp);
    unknow_nodes.append(tmp[1:]);

def calculate_eu(result, u_nodes):
    prob = float(result[0]);
    utility_ndoe = nodes[dd.get("utility")];
    list = [utility_ndoe.type];
    for p in utility_ndoe.parent_list:
        if u_nodes.count("+"+p) > 0:
            list.append("+"+p);
        elif u_nodes.count("-"+p) > 0:
            list.append("-"+p);
    utility_value = utility_ndoe.get_prob(list);
    result[1] += float(prob)*float(utility_value);

def Conditional_Utility(q):
    para = q[3: len(q)-1];
    p_list = para.split('|');
    joint_var = p_list[0].strip();
    evidence_var = p_list[1].strip();
    #construct a new EU()
    new_EU = "EU("+joint_var+", "+evidence_var+")";
    #print new_EU;
    tmp_eu = Joint_Utility(new_EU);
    #print tmp_eu;

    #construct P(evidence)
    #evidence_prob = "P("+evidence_var+")";
    #print evidence_prob;
    #e_prob = Joint(evidence_prob);
    return tmp_eu;

def Joint_Max_eu(q):
    variables = q[4: len(q)-1].split(", ");
    result = [];
    symbol_list = [];
    enumerate_MEU(variables, [], result, "", symbol_list);
    prob = max(result);
    index = result.index(prob);
    return [symbol_list[index], prob];

def enumerate_MEU(unknown_var, known_var, result, symbol, symbol_list):
    if unknown_var == []:
        eu_query = "EU(";
        for i in range(0, len(known_var)):
            if i != len(known_var)-1:
                eu_query += known_var[i] + ", ";
            else:
                eu_query += known_var[i] + ")";
        eu = Joint_Utility(eu_query);
        result.append(eu);
        symbol_list.append(symbol.strip());
        return;
    next_unknown_var = unknown_var.pop(0);
    tmp = next_unknown_var+" = +";
    known_var.append(tmp);
    symbol += "+ ";
    enumerate_MEU(unknown_var, known_var, result, symbol, symbol_list);
    known_var.remove(tmp);
    symbol = symbol[0: len(symbol)-2];
    ############################################
    tmp = next_unknown_var + " = -";
    known_var.append(tmp);
    symbol += "- ";
    enumerate_MEU(unknown_var, known_var, result, symbol, symbol_list);
    known_var.remove(tmp);
    symbol = symbol[0:len(symbol)-2];
    unknown_var.append(next_unknown_var);

def Conditional_Max_eu(q):
    para = q[4:len(q)-1];
    p_list = para.split('|');
    unknown_var = p_list[0].strip().split(", ");
    evidence_var = p_list[1].strip().split(", ");
    result = [];
    symbol_list = [];
    enumerate_MEU(unknown_var, evidence_var, result, "", symbol_list);
    value = max(result);
    index = result.index(value);
    list = [symbol_list[index], value];

    # evidence_query = "P(";
    # for i in range(0, len(evidence_var)):
    #     if i != len(evidence_var)-1:
    #         evidence_query += evidence_var[i] + ", ";
    #     else:
    #         evidence_query += evidence_var[i] + ")";
    # evidence_prob = Joint(evidence_query);
    # value = float(list[1]/evidence_prob);
    # list[1] = value;
    return list;



def query_type(query):
    if query[0] == 'P':
        if query.find('|') == -1:
            return JOINT_OR_MARGINAL;
        else:
            return CONDITIONAL;
    elif query[0] == "E":
        if query.find('|') == -1:
            return JOINT_EU;
        else:
            return CONDITIONAL_EU;
    elif query[0] == "M":
        if query.find('|') == -1:
            return JOINT_MEU;
        else:
            return CONDITIONAL_MEU;

#file = open("./HW3_samples/sample07.txt");
file = open(sys.argv[2]);
output_file = open("output.txt","w");
query = [];
nodes = [];
dd = dict();
i = 0;
line = file.readline().strip();
while line != "******":
    query.append(line);
    line = file.readline().strip();
line = file.readline();
while line != "":
    newnode = node(line, file);
    nodes.append(newnode);
    dd[newnode.node_name] = i;
    i = i+1;
    line = file.readline();

# for q in query:
#     print q;
# for n in nodes:
#     print n.node_name;
#     if n.type == 0:
#         print "occurance: "+str(n.occurance)+"\n";
#     elif n.type == 1:
#         print n.table;
#         print "\n";
#     elif n.type == 2:
#         print "decision node\n";
#     elif n.type == 3:
#         print n.table;
#         print "\n";

for q in query:
    type = query_type(q);
    if type == JOINT_OR_MARGINAL:
        prob = Joint(q)+1e-8;
        prob = "{:.2f}".format(Decimal(str(prob)));
    elif type == CONDITIONAL:
        prob = Condition(q)+1e-8;
        prob = "{:.2f}".format(Decimal(str(prob)));
    elif type == JOINT_EU:
        prob = int(round(Joint_Utility(q)+1e-8, 0));
    elif type == CONDITIONAL_EU:
        prob = int(round(Conditional_Utility(q)+1e-8,0));
    elif type == JOINT_MEU:
        list = Joint_Max_eu(q);
        value = int(round(list[1], 0));
        prob = list[0]+" "+str(value);
    elif type == CONDITIONAL_MEU:
        list = Conditional_Max_eu(q);
        value = int(round(list[1]+1e-8, 0));
        prob = list[0]+" "+str(value);
    print prob;
    output_file.write(str(prob)+"\n");
file.close();
output_file.close();
