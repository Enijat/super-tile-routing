import subprocess
import sys

def wireLookup(wireName) :
    #TODO
    return wireName

#this function is perfect only by definition, but not by execution, meaning that there is good chance there is a simpler function with the same result
def perfectHashFunction(A, B, C) :
    b = (B - A) % 6
    c = (C - A) % 6
    basicResult = 2*(b + c) + abs(b - c)
    reducedResult = ((((basicResult - 8) % 13) - 4) % 11) - 1 # reduces the 10 different numbers in basicResult to the range 0 - 9
    return 10 * A + reducedResult

gate = "SAMPLE" # fixed to sample as an input because this allows for all four required core gate rotations which every gate, that will be used, can be represented in
output = ""
inputs = ""

wires = ["", "", "", "", "", ""]

lookupArrayForFile = []

directions = ["0", "1", "2", "3", "4", "5"]
for directionOut in directions :# Represents the output
    i = 0
    while i < 10 :
        lookupArrayForFile.append("") # This just makes room for the next 10 entrys in the array, yes it's inefficient but this is never executed in time critical code
        i += 1
    for directionIn1 in directions :# Represents the first input
        if directionIn1 != directionOut :
            for directionIn2 in directions : # Represents the second input
                if directionIn2 != directionOut and directionIn2 != directionIn1 and int(directionIn2) > int(directionIn1) :

                    output = directionOut
                    inputs = directionIn1 + directionIn2
                    args = ("./main", "-r", gate, inputs, output)

                    executed_binary = subprocess.Popen(args, stdout=subprocess.PIPE)
                    executed_binary.wait()
                    output = executed_binary.stdout.read().decode().split(", ")

                    wires[0:6] = output[1:7]

                    arrayEntry = '\"' + directionOut + directionIn1 + directionIn2 + '\": ['

                    arrayEntry += '\"' + wireLookup(wires[0]) + '\"' # Write first entry seperate so we don't write a ',' where it isn't required
                    for wire in wires[1:6] :
                         arrayEntry += ', \"' + wireLookup(wire) + '\"'
                    
                    arrayEntry += ']'

                    lookupArrayForFile[perfectHashFunction(int(directionOut), int(directionIn1), int(directionIn2))] = arrayEntry

                    #What I want to write to the array: "205": ["empty", "wire01", ...]

output_file = open(r"super-tile_gate-combinations.json", "w")

output_file.write('{\n')
output_file.write('    \"2in1out_supertile_layouts\": [\n')


output_file.write('        {\n            ' + lookupArrayForFile[0] + '\n        }')# Write first entry seperate so we don't write a ',' where it isn't required
for entry in lookupArrayForFile[1:60] :
    output_file.write(',\n        {\n            ' + entry + '\n        }')

output_file.write('\n    ]\n')
output_file.write('}\n')


output_file.close()