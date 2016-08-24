#__author__ = 'Jiaqi'
import copy
import sys
DICT= {0:"A1",1:"B1",2:"C1",3:"D1",4:"E1",
       5:"A2",6:"B2",7:"C2",8:"D2",9:"E2",
       10:"A3",11:"B3",12:"C3",13:"D3",14:"E3",
       15:"A4",16:"B4",17:"C4",18:"D4",19:"E4",
       20:"A5",21:"B5",22:"C5",23:"D5",24:"E5"}
def Greedy_BFS(board, status, player,file):
    x_score = 0;
    o_score = 0;
    #calculate the score of X and O###############
    for x in range(0,5):
        for y in range(0,5):
            if status[x][y]=='X':
                x_score += board[x][y]
            else :
                if status[x][y]=='O':
                    o_score += board[x][y]
    player_score= x_score if player=="X" else o_score
    rival_score=x_score if player=="O" else o_score
    evaluation = player_score-rival_score
    position=[-1,-1]
    #traverse the board and find the next step####################
    for x in range(0,5):
        for y in range(0,5):
            if status[x][y]!="*":
                continue
            back_up_status = copy.deepcopy(status)
            update(back_up_status,x,y,player)
            v = evaluate(board, back_up_status, player, 1)
            #update or not
            if v > evaluation:
                evaluation = v
                position[0] = x
                position[1] = y

    #print evaluation
    x=position[0]
    y=position[1]
    #print x,y
    update(status,x,y,player)
    #write to the output file############################
    for line in status:
        if file.tell() == 0:
            file.write("".join(line))
        else:
            file.write("\r\n")
            file.write("".join(line))
    print "Greedy BFS done"
########################################################################################################
def Minimax(board,status,player,cutoff,file):
    output_file = open("traverse_log.txt","w")
    output_file.write("Node,Depth,Value")
    next_step = Max_Value(board, status, 0, cutoff, "root", player, output_file)
    output_file.close()

    update(status,next_step[0],next_step[1],player)
    for line in status:
        if file.tell() == 0:
            file.write("".join(line))
        else:
            file.write("\r\n")
            file.write("".join(line))
    print "Minimax done"
########################################################################################################
def Max_Value(board, status, depth, cutoff, node, player, file):
    #print status, depth, cutoff, node, player
    if depth != cutoff:
        file.write("\r\n"+node+","+str(depth)+",-Infinity")
    if depth == cutoff:
        utility = evaluate(board, status, player, 1)
        file.write("\r\n"+node+","+str(depth)+","+str(utility))
        return utility
    value = -9999
    rival = ("O" if player=="X" else "X")
    for x in range(0,5):
        for y in range(0,5):
            if status[x][y] == "*":
                back_up = copy.deepcopy(status)
                update(back_up, x, y, player)
                node_name = DICT[x*5+y]
                v = Min_Value(board,back_up, depth+1, cutoff, node_name, rival, file)
                if v > value:
                    value = v
                    next_step = [x, y,v]
                file.write("\r\n"+node+","+str(depth)+","+str(value))
    if node=="root":
        return next_step
    else:
        return value
########################################################################################################
def Min_Value(board, status, depth, cutoff, node, rival, file):
    #print status, depth, cutoff, node, rival
    if depth != cutoff:
        file.write("\r\n"+node+","+str(depth)+",Infinity")
    if depth == cutoff:
        #print status
        utility = evaluate(board,status, rival, 0)
        file.write("\r\n"+node+","+str(depth)+","+str(utility))
        return utility
    value = 9999
    player = ("O" if rival=="X" else "X")
    for x in range(0,5):
        for y in range(0,5):
            if status[x][y] == "*":
                back_up = copy.deepcopy(status)
                update(back_up, x, y, rival)
                node_name = DICT[x*5+y]
                v = Max_Value(board, back_up, depth+1, cutoff, node_name, player, file)
                if v < value:
                    value = v
                file.write("\r\n"+node+","+str(depth)+","+str(value))
    return value
########################################################################################################
def evaluate(board, status, p, flag):
    x_score = 0;
    o_score = 0;
    for i in range(0,5):
        for j in range(0,5):
            if status[i][j]=="X":
                x_score += board[i][j]
            elif status[i][j] == "O":
                o_score += board[i][j]
    if (p=="X" and flag==1) or (p == "O" and flag == 0):
        return x_score-o_score
    else:
        return o_score-x_score
########################################################################################################
def update(status, x, y, player):
    rival = ("X" if player == "O" else "O")
    status[x][y] = player
    if is_raid(status, x, y, player):
        #check the left neighbor
        if y-1>=0:
            if status[x][y-1]==rival:
                status[x][y-1] = player
        #check the right beighbor
        if y+1<=4:
            if status[x][y+1]==rival:
                status[x][y+1] = player
        #check the up neighbor
        if x-1>=0:
            if status[x-1][y]==rival:
                status[x-1][y] = player
        #check the down neighbor
        if x+1<=4:
            if status[x+1][y]==rival:
                status[x+1][y] = player
########################################################################################################
def is_raid(status, x, y, player):
    if y-1>=0:
        if status[x][y-1] == player:
            return True
    if y+1<=4:
        if status[x][y+1] == player:
            return True
    if x-1>=0:
        if status[x-1][y] == player:
            return True
    if x+1<=4:
        if status[x+1][y] == player:
            return True
    return False
########################################################################################################
def get_board(board, file):
    for index in range(0,5):
        line = file.readline()
        row = line[0:len(line)-1].split(' ')
        board[index] += [int(num) for num in row]
########################################################################################################
def get_status(status,file):
    for index in range(0,5):
        line = file.readline()
        if line[len(line)-1]=='\n':
            line=line[0:len(line)-2]
        status[index] += list(line)
########################################################################################################
def Alpha_Beta_Search(board, status, player, cutoff,file):
    output_file = open("traverse_log.txt","w")
    output_file.write("Node,Depth,Value,Alpha,Beta")
    alpha_beta = ["-Infinity","Infinity"]
    next_step=Alpha_Beta_Max(board,status,player,0,cutoff,"root",alpha_beta,output_file)
    output_file.close();
    update(status,next_step[0],next_step[1],player)
    for line in status:
        if file.tell() == 0:
            file.write("".join(line))
        else:
            file.write("\r\n")
            file.write("".join(line))
    print "Alpha-Beta done"
##############################################################################################################
def Alpha_Beta_Max(board,status,player,depth,cutoff,node,a_b,file):
    if depth == cutoff or is_end(status) == True:
        utility = evaluate(board,status,player,1)
        file.write("\r\n"+node+","+str(depth)+","+str(utility)+","+str(a_b[0])+","+str(a_b[1]))
        return utility
    if depth != cutoff:
        file.write("\r\n"+node+","+str(depth)+",-Infinity,"+str(a_b[0])+","+str(a_b[1]))
    value = -9999
    rival = ("O" if player=="X" else "X")
    for x in range(0,5):
        for y in range(0,5):
            if status[x][y] == "*":
                back_up = copy.deepcopy(status)
                back_up_list = copy.deepcopy(a_b)
                update(back_up,x,y,player)
                node_name = DICT[x*5+y]
                value = max(value, Alpha_Beta_Min(board,back_up,rival,depth+1,cutoff,node_name,back_up_list,file))
                if type(a_b[1])!=str and value>=int(a_b[1]) and node!="root":
                    file.write("\r\n"+node+","+str(depth)+","+str(value)+","+str(a_b[0])+","+str(a_b[1]))
                    return value
                if (a_b[0]=="-Infinity" or value>a_b[0])and node=="root":
                    next_step=[x,y]
                a_b[0] = value if a_b[0]=="-Infinity" else max(a_b[0],value)
                if node=="root":
                    a_b[1]="Infinity"
                    file.write("\r\n"+node+","+str(depth)+","+str(value)+","+str(a_b[0])+","+str(a_b[1]))
                else:
                    file.write("\r\n"+node+","+str(depth)+","+str(value)+","+str(a_b[0])+","+str(a_b[1]))
    if node=="root":
        return next_step
    return value
###############################################################################################################
def Alpha_Beta_Min(board,status,rival,depth,cutoff,node,a_b,file):
    if depth == cutoff or is_end(status) == True:
        utility = evaluate(board,status,rival,0)
        file.write("\r\n"+node+","+str(depth)+","+str(utility)+","+str(a_b[0])+","+str(a_b[1]))
        return utility
    if depth != cutoff:
        file.write("\r\n"+node+","+str(depth)+",Infinity,"+str(a_b[0])+","+str(a_b[1]))
    value = 9999
    player = ("O" if rival=="X" else "X")
    for x in range(0,5):
        for y in range(0,5):
            if status[x][y] == "*":
                back_up = copy.deepcopy(status)
                back_up_list = copy.deepcopy(a_b)
                update(back_up,x,y,rival)
                node_name = DICT[x*5+y]
                value = min(value, Alpha_Beta_Max(board,back_up,player,depth+1,cutoff,node_name,back_up_list,file))
                #print "lalala",a_b
                if type(a_b[0])!=str and value<=int(a_b[0]):
                    file.write("\r\n"+node+","+str(depth)+","+str(value)+","+str(a_b[0])+","+str(a_b[1]))
                    return value
                a_b[1] = value if a_b[1]=="Infinity" else min(a_b[1],value)
                file.write("\r\n"+node+","+str(depth)+","+str(value)+","+str(a_b[0])+","+str(a_b[1]))
    return value
###############################################################################################################
def Start_War(board,status,first_player,first_tactic,first_cutoff,second_player,second_tactic,second_cutoff,file):
    while(True):
        if(is_end(status) == False):
            Attack(board,status,first_player,first_tactic,first_cutoff,file)
        else:
            break
        if(is_end(status) == False):
            Attack(board,status,second_player,second_tactic,second_cutoff,file)
        else:
            break
    if evaluate(board,status,"X",1)>0:
        print "X win"
    else:
        print "O win"
    print "Game over"
################################################################################################################
def is_end(status):
    for x in range(0,5):
        for y in range(0,5):
            if(status[x][y] == "*"):
                return False
    return True
###############################################################################################################
def Attack(board, status, player,tactic,cutoff,file):
    if tactic == 1:
        Greedy_BFS(board, status, player,file)
    elif tactic == 2:
        Minimax(board,status,player,cutoff,file)
    elif tactic == 3:
        Alpha_Beta_Search(board, status, player, cutoff,file)
################################################################################################################


#file = open("input.txt")
file_name = sys.argv[2]
file = open(file_name,"r")
action = int(file.readline())
if action!=4:
    player = file.readline()
    player = player[0:len(player)-2]
    cutoff = int(file.readline())
else:
    first_player = file.readline()
    first_player = first_player[0:len(first_player)-2]
    first_tactic = int(file.readline())
    first_cutoff = int(file.readline())
    second_player = file.readline()
    second_player = second_player[0:len(second_player)-2]
    second_tactic = int(file.readline())
    second_cutoff = int(file.readline())
board = [[],[],[],[],[]]
status = [[],[],[],[],[]]
get_board(board, file)
get_status(status,file)
file.close()
if(action == 1 or action == 2 or action == 3):
    output_file = open("next_state.txt","w")
elif action == 4:
    output_file = open("trace_state.txt","w")
if action == 1:
    Greedy_BFS(board, status, player,output_file)
elif action == 2:
    Minimax(board,status,player,cutoff,output_file)
elif action == 3:
    Alpha_Beta_Search(board, status, player, cutoff,output_file)
elif action == 4:
    Start_War(board,status,first_player,first_tactic,first_cutoff,second_player,second_tactic,second_cutoff,output_file)
output_file.close()