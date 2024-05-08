import os,linecache
print(os.getcwd())

file1 = open('Resources\Look.txt', 'r')
Lines = file1.readlines()
arr=[]
 
count = 0
sbrake=0
ebrake=0
e_arr=[];f_arr=[]
failure=0
# Strips the newline character
for line in Lines:
    count += 1
    arr = line.split("\t")
    print(f"Line #{count}=\tL:{float(arr[3])},\tSL:{float(arr[5])}")
    
    #service
    t1=( (0-float(arr[5]))/(-1.2 ) )*(5/18)
    s1=0.5*(0+float(arr[5]))*t1*(5/18)#1/2 * u * t * conversion of km/hr to m/s
    
    t2=( (0-float(arr[5]))/(-2.73) )*(5/18)
    s2=0.5*(0+float(arr[5]))*t2*(5/18)#1/2 * u * t * conversion of km/hr to m/s
    
    #print(f"Line #{count}=\t {s}\t{'SERVICE' if s<float(arr[0]) else 'EMERGENCY'}\n")
    
    if s1<=float(arr[3]):
        print(f"Line #{count}=\t{s1}\t{t1}\tSERVICE")
        sbrake+=1
    elif s2<=float(arr[3]):
        print(f"Line #{count}=\t{s2}\t{t2}\tEMERGENCY")
        ebrake+=1
        e_arr.append(count)
        #e_arr.append(arr[3])
    else:
        print(f"Line #{count}=\t!!!!!!!!!!!!!!!\tFAILURE")
        print(f"Line #{count}=\tS:{s1}\t{t1}")
        print(f"Line #{count}=\tE:{s2}\t{t2}")
        failure+=1
        f_arr.append(count)
    print("\n")
    
print(f"""
======================================

S:{sbrake}
E:{ebrake}""")
#print(e_arr)
print("Line\tSect\t#\tLen\t%\tSL\tInfrastructure")
for i in e_arr:
    #print(i)
    #print(linecache.getline('Resources\Look.txt', i)[:-1].split("\t"))
    print(linecache.getline('Resources\Look.txt', i)[:-1])
print(f"F:{failure}")
for i in f_arr:
    print(linecache.getline('Resources\Look.txt', i)[:-1])