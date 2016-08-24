 
import copy;
import types;
import sys;

class clause:
    def __init__(self, line, count):
        self.number = count;
        if line.find("=>") != -1:
            self.type = "i";
        else:
            self.type = "p";
        if self.type == "p":
            predicate = get_predicate(line);
            arg_list = get_arg_list(line, count);
            self.result = {predicate:arg_list};
            self.premise = [];
        else:
            new_line = line.split("=>");
            predicate = get_predicate(new_line[1]);
            arg_list = get_arg_list(new_line[1], count);
            self.result = {predicate:arg_list};
            self.premise = get_premise(new_line[0], count);
        #print self.type, result, premise;

    def show(self):
        if self.type=="i":
            print "Implication";
            for ele in self.premise:
                for key, value in ele.items():
                    print str(key)+"("+", ".join(value)+")";
            for key,value in self.result.items():
                print "=>"+str(key)+"("+",".join(value)+")\n";
        else:
            print "Predicate"
            for key,value in self.result.items():
                print "=>"+str(key)+"("+",".join(value)+")\n";

def get_predicate(line):
    line = line.strip();
    index = line.find('(');
    return line[0:index];

def get_arg_list(line, count):
    line = line[line.find('(')+1: line.find(')')];
    line = line.split(", ");
    for i in range(0, len(line)):
        if len(line[i])==1 and line[i].islower():
            line[i] = line[i]+str(count);
    return line;

def get_premise(line,count):
    line = line.strip();
    pre = line.split(" && ");
    pre_list = [];
    for ele in pre:
        predicate = get_predicate(ele);
        arg_list = get_arg_list(ele, count);
        pre_list.append({predicate:arg_list});
    return pre_list;

def get_KB(KB, file):
    number = (int)(file.readline());
    for i in range(0, number):
        c = clause(file.readline(), i+1);
        KB.append(c);

def get_query_type(q):
    if q.find("&&") != -1:
        return 2;
    else:
        return 1;

def FETCH_RULES_FOR_GOAL(KB,goal):
    li = [];
    predicate = "";
    args_list = "";
    for pre, args in goal.items():
        predicate = pre;
        args_list = args;
    flag = 1;
    for rule in KB:
        for key, value in rule.result.items():
            if key == predicate:
                flag = 1;
                for i in range(0, len(args_list)):
                    if args_list[i][0].isupper() and value[i][0].isupper() and args_list[i] != value[i]:
                        flag = -1;
                        break;
                if flag == -1:
                    break;
            else:
                flag = -1;
        if flag == 1:
            li.append(rule);
    return li;

def replace(rule, old, new):
    for key, value in rule.result.items():
        for i in range(0, len(value)):
            if value[i] == old:
                value[i] = new;
    if rule.type == "i":
        for pre in rule.premise:
            for key, value in pre.items():
                for i in range(0, len(value)):
                    if value[i] == old:
                        value[i] = new;

def UNIFY(result, goal, sub):
    theta = copy.deepcopy(sub);
    if type(theta) == types.StringType and theta == "failure":
        return "failure";
    elif result == goal:
        return theta;
    elif type(result) == types.StringType and result[0].islower():
        return UNIFY_VAR(result, goal, theta);
    elif type(goal) == types.StringType and goal[0].islower():
        return UNIFY_VAR(goal, result, theta);
    elif type(result) == types.DictionaryType and type(goal) == types.DictionaryType:
        result_arg = [];
        goal_arg = [];
        for key, value in result.items():
            result_arg = value;
        for key, value in goal.items():
            goal_arg = value;
        return UNIFY(result_arg, goal_arg, theta);
    elif type(result) == types.ListType and type(goal) == types.ListType:
        first_g = goal[0];
        rest_g = goal[1:];
        first_r = result[0];
        rest_r = result[1:];
        theta = UNIFY(first_r, first_g, theta)
        return UNIFY(rest_r, rest_g, theta);
    else:
        return "failure";

def UNIFY_VAR(var, x, theta):
    value = theta.get(var);
    if value != None:
        return UNIFY(value,x,theta);
    else:
        value = theta.get(x);
        if value != None:
            return UNIFY(var, value, theta);
    theta[var] = x;
    return theta;

def SUBST(theta, first):
    args_list = [];
    for key, value in first.items():
        args_list = value;
    for i in range(0, len(args_list)):
        while args_list[i][0].islower():
            if theta.get(args_list[i]) != None:
                args_list[i] = theta.get(args_list[i]);
            else:
                break;

def Say(goal, file, type):
    if type == 1:
        log = "Ask: ";
    elif type == 2:
        log = "False: ";
    for key,value in goal.items():
        arg_list = copy.deepcopy(value);
        log += str(key);
        for i in range(0, len(arg_list)):
            if arg_list[i][0].islower():
                arg_list[i] = "_";
        log += "("+", ".join(arg_list)+")";
        print log;
        file.write(log+"\n");

def FOL_BC_AND(KB, goals, theta, file):
    if type(theta) == types.StringType and theta == "failure":
        yield None;
    elif len(goals) == 0:
        yield theta;
    else:
        first = goals[0];
        rest = goals[1:];
        backup_first = copy.deepcopy(first);
        SUBST(theta,backup_first);
        for theta_1 in FOL_BC_OR(KB, backup_first, theta, file):
            if theta_1 != None:
                for theta_2 in FOL_BC_AND(KB, rest, theta_1, file):
                    yield theta_2;
            else:
                yield None;

def FOL_BC_OR(KB, goal, theta, file):
    flag = 1;
    flag_no_rules = 0;
    rule_list = FETCH_RULES_FOR_GOAL(KB,goal);
    i = 0;
    if len(rule_list) == 0:
        Say(goal, file, 1);
        flag_no_rules = 1;
    while i < len(rule_list) and flag_no_rules == 0:
        Say(goal, file, 1);
        back_up_rule = "";
        backup_theta = "";
        while i < len(rule_list):
            back_up_rule = copy.deepcopy(rule_list[i]);
            backup_theta = copy.deepcopy(UNIFY(back_up_rule.result, goal, theta));
            if type(backup_theta) == types.StringType and backup_theta == "failure":
                i += 1;
                continue;
            else:
                break;
        if i == len(rule_list):
            flag = -1;
            break;
        flag = 1;
        rule_number = back_up_rule.number; ###############################################################
        for theta_1 in FOL_BC_AND(KB, back_up_rule.premise, backup_theta,file):
            if theta_1 == None:
                flag = -1;
                continue;
            else:
                flag = 1;
            backup_goal = copy.deepcopy(goal);
            SUBST(theta_1,backup_goal);
            for pre, args in backup_goal.items():
                log = "True: "+str(pre)+"("+", ".join(args)+")";
                print log;
                file.write(log+"\n")
            theta_1 = process_theta(theta_1,rule_number, KB);#############################################################
            yield theta_1;
        i += 1;
    if flag == -1 or flag_no_rules == 1:
        backup_goal = copy.deepcopy(goal);
        SUBST(theta,backup_goal);
        Say(backup_goal, file, 2);
        yield None;

def FOL_BC_ASK(KB,query, theta, file):
    return FOL_BC_OR(KB,query, theta, file)

def process_theta(theta, number, KB):
    new_theta={};
    for key, value in theta.items():
        key_num = int(key[1:]);
        if number != key_num:
            new_theta[key]=value;
    return new_theta;

def pre_process(KB, query, query_type, file):
    if query_type == 1:
        query = clause(query, 0);
        return FOL_BC_ASK(KB, query.result, {}, file);
    else:
        query_list = query.split(" && ");
        theta = {};
        print query_list;
        for i in range(0, len(query_list)):
            query_list[i] = clause(query_list[i], 0);
            query_list[i] = query_list[i].result;
        return FOL_BC_AND(KB, query_list, {}, file);

KB=[];
#file = open("sample03 2.txt");
file = open(sys.argv[2]);
output_file = open("output.txt","w");
query = file.readline().strip();
get_KB(KB,file);
file.close();

query_type = get_query_type(query);

generator = pre_process(KB,query, query_type, output_file);
if generator.next() == None:
    output_file.write("False");
    print "False";
else:
    output_file.write("True");
    print "True";
output_file.close();