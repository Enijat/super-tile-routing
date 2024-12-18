import subprocess

output_file = open(r"super-tile_gate-combinations.json", "w")

gate = "SAMPLE"
output = ""
inputs = ""



directions = ["0", "1", "2", "3", "4", "5"]
for directionOut in directions :# Represents the output
    for directionIn1 in directions :# Represents the first input
        if directionIn1 != directionOut :
            for directionIn2 in directions : # Represents the second input
                if directionIn2 != directionOut and directionIn2 != directionIn1 and int(directionIn2) > int(directionIn1) :
                    output = directionOut
                    inputs = directionIn1 + directionIn2
                    args = ("./main", "-r", gate, inputs, output)
                    print("Executing:")
                    print(args)
                    executed_binary = subprocess.Popen(args, stdout=subprocess.PIPE)
                    executed_binary.wait()
                    output = executed_binary.stdout.read().decode()
                    output_file.write(output)

output_file.close()