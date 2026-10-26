import os,re,sys
root=sys.argv[1]
for d,ds,fs in os.walk(root,topdown=False):
    for n in fs+ds:
        m=re.sub(r'#U([0-9a-fA-F]{4})',lambda x:chr(int(x.group(1),16)),n)
        if m!=n: os.rename(os.path.join(d,n),os.path.join(d,m))
