import os


for fname in [f for f in os.listdir("./") if f.split(".")[-1] == "csv"]:
    print "##### FNAME : ", fname
    with open( fname, 'r') as f:
        lines = f.readlines()

    with open(fname, 'w') as f:
        print lines[0]
        if lines[0][3] != "H":
            pos = [i for i,c in enumerate(lines[0]) if c == "H"][0]
            print pos
            print str(lines[0][0]) + ",,," + lines[0][pos:]
            f.write(lines[0][0] + ",,," + lines[0][pos:])


        else:
            f.write(lines[0])

        for l in lines[1:]:
            l = l.split(",")
            pos = [i for i,j in enumerate(l) if j == "%"][0]

            print "pos",pos
            if pos < 2:
                comma = 2 - pos
                print "Moving columns ", comma, "positions to the right"
                print ",".join(l[0:pos]) + ","*comma + ",".join(l[pos:])
                f.write(",".join(l[0:pos]) + ","*comma + ",".join(l[pos:]))

            elif pos > 2:
                tojoin = pos - 2 + 1
                print "Moving columns ", tojoin, "positions to the left"
                print "l",l
                print "' '.join([l[0:tojoin]])", " ".join(l[0:tojoin])
                print [" ".join(l[0:tojoin])] + l[tojoin:]
                print ",".join([" ".join(l[0:tojoin])] + l[tojoin:])
                l = [" ".join(l[0:tojoin])] + l[tojoin:]
                f.write(",".join(l))

            elif pos == 0:
                f.write("," + ",".join(l))

            else:
                f.write(",".join(l))

