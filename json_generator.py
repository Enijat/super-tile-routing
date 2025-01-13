import subprocess
import sys

# Directions are based on this layout
#           ˍ---¯¯¯---ˍ ˍ---¯¯¯---ˍ
#          |           |           |
#          |    (5)    |    (0)    |
#          |           |           |
#     ˍ---¯ ¯---ˍ ˍ---¯ ¯---ˍ ˍ---¯ ¯---ˍ
#    |           |           |           |
#    |    (4)    |   (Core)  |    (1)    |
#    |           |           |           |
#     ¯---ˍ ˍ---¯ ¯---ˍ ˍ---¯ ¯---ˍ ˍ---¯
#          |           |           |
#          |    (3)    |    (2)    |
#          |           |           |
#           ¯---ˍˍˍ---¯ ¯---ˍˍˍ---¯
directions = ["0", "1", "2", "3", "4", "5"]

# Transforms the wire naming system used in "super-tile_layout_generator" to the one used in fiction
def wireLookup(wireName) :
    match wireName :
        case "empty" :
            return "empty"
        # Standard wires:
        case "wire01" :
            return "wire01"
        case "wire02" :
            return "wire02"
        case "wire03" :
            return "wire03"
        case "wire04" :
            return "wire04"
        case "wire05" :
            return "wire05"
        case "wire12" :
            return "wire12"
        case "wire13" :
            return "wire13"
        case "wire14" :
            return "wire14"
        case "wire15" :
            return "wire15"
        case "wire23" :
            return "wire23"
        case "wire24" :
            return "wire24"
        case "wire25" :
            return "wire25"
        case "wire34" :
            return "wire34"
        case "wire35" :
            return "wire35"
        case "wire45" :
            return "wire45"
        # Double wires with on straight wire
        case "wire14_23" :
            return "wire14_23"
        case "wire25_34" :
            return "wire25_34"
        case "wire03_45" :
            return "wire03_45"
        case "wire14_05" :
            return "wire14_05"
        case "wire25_01" :
            return "wire25_01"
        case "wire03_12" :
            return "wire03_12"
        # Double wires with both wires bend
        case "wire12_34" :
            return "wire12_34"
        case "wire23_45" :
            return "wire23_45"
        case "wire34_05" :
            return "wire34_05"
        case "wire45_01" :
            return "wire45_01"
        case "wire05_12" :
            return "wire05_12"
        case "wire01_23" :
            return "wire01_23"
        # Default case (Error)
        case _:
            return "ERROR_wire-not-found"

# Transforms the gate naming system used in "super-tile_layout_generator" to the one used in fiction (replaces the gate name with just the output direction)
def coreLookup(coreName) :
    match (coreName[-1]) :
        case "0" :
            return "NORTH_EAST"
        case "2" :
            return "SOUTH_EAST"
        case "3" :
            return "SOUTH_WEST"
        case "5" :
            return "NORTH_WEST"
        case _:
            return "Unknown-core-orientation"

# This function is perfect only by definition, but not by execution, meaning that there is good chance there is a simpler function with the same result
def perfectHashFunction2in1out(A, B, C) :
    b = (B - A) % 6 # get B and C into the same 1-5 range for all A
    c = (C - A) % 6
    basicResult = 2*(b + c) + abs(b - c) # get 10 different numbers out of b and c
    reducedResult = ((((basicResult - 8) % 13) - 4) % 11) - 1 # reduces the 10 different numbers to the range 0 - 9
    return 10 * A + reducedResult

def perfectHashFunction1in1out(A, B) :
    basicResult = 2*(A + B) - abs(A - B)
    if (A * B) == 2 : # move the basic result 5 to the 12, because 5 is used twice and 12 is a single wide gap
        basicResult = 12
    reducedResult = ((basicResult - 15) % 17) - 2
    return reducedResult


def perfectHashFunction1in0out(A) :
    return A

# Generates the .json file for gates with 2 inputs and 1 output
def generate2in1out() :
    lookupArrayForFile = []
    for directionOut in directions :# Represents the output wire
        for i in range(10) :
            lookupArrayForFile.append("")

        for directionIn1 in directions :# Represents the first input wire
            if directionIn1 != directionOut :
                for directionIn2 in directions : # Represents the second input wire
                    if directionIn2 != directionOut and directionIn2 != directionIn1 and int(directionIn2) > int(directionIn1) :
                        
                        # Prepare programm inputs
                        gate = "SAMPLE" # fixed to sample as an input because this allows for all four required core gate rotations which every gate, that will be used, can be represented in
                        outputWire = directionOut
                        inputWires = directionIn1 + directionIn2
                        args = ("./supertile_layout_generator", "-r", gate, inputWires, outputWire)

                        # Execute programm and read output
                        executed_binary = subprocess.Popen(args, stdout=subprocess.PIPE)
                        executed_binary.wait()
                        output = executed_binary.stdout.read().decode().split(", ")

                        # Write array entry
                        arrayEntry = '\"' + directionOut + directionIn1 + directionIn2 + '\": ['

                        arrayEntry += '\"' + coreLookup(output[0]) + '\"' # Write first entry seperate so we don't write a ',' where it isn't required
                        for wire in output[1:7] :
                            arrayEntry += ', \"' + wireLookup(wire) + '\"'
                        
                        arrayEntry += ']'

                        # Add array entry
                        lookupArrayForFile[perfectHashFunction2in1out(int(directionOut), int(directionIn1), int(directionIn2))] = arrayEntry

    # Write array to file
    output_file = open(r"2in1out_supertile_layouts.json", "w")

    output_file.write('{\n')
    output_file.write('    \"2in1out_supertile_layouts\": [\n')

    output_file.write('        {\n            ' + lookupArrayForFile[0] + '\n        }')# Write first entry seperate so we don't write a ',' where it isn't required
    for entry in lookupArrayForFile[1:60] :
        output_file.write(',\n        {\n            ' + entry + '\n        }')

    output_file.write('\n    ]\n')
    output_file.write('}\n')

    output_file.close()

# Generates the .json file for gates with 1 input and 1 output (aka wires)
def generate1in1out() :
    lookupArrayForFile = []
    for i in range(15) :
            lookupArrayForFile.append("")
    for directionOut in directions :# Represents the output wire
        for directionIn in directions :# Represents the input wire
            if directionIn > directionOut :
                # Prepare programm inputs
                gate = "WIRE"
                args = ("./supertile_layout_generator", "-r", gate, directionIn, directionOut)

                # Execute programm and read output
                executed_binary = subprocess.Popen(args, stdout=subprocess.PIPE)
                executed_binary.wait()
                output = executed_binary.stdout.read().decode().split(", ")

                # Write array entry
                arrayEntry = '\"' + directionOut + directionIn + '\": ['

                arrayEntry += '\"' + wireLookup(output[0]) + '\"' # Write first entry seperate so we don't write a ',' where it isn't required
                for wire in output[1:7] :
                    arrayEntry += ', \"' + wireLookup(wire) + '\"'
                
                arrayEntry += ']'

                # Add array entry
                lookupArrayForFile[perfectHashFunction1in1out(int(directionOut), int(directionIn))] = arrayEntry
    
    # Write array to file
    output_file = open(r"1in1out_supertile_layouts.json", "w")

    output_file.write('{\n')
    output_file.write('    \"1in1out_supertile_layouts\": [\n')

    output_file.write('        {\n            ' + lookupArrayForFile[0] + '\n        }')# Write first entry seperate so we don't write a ',' where it isn't required
    for entry in lookupArrayForFile[1:30] :
        output_file.write(',\n        {\n            ' + entry + '\n        }')

    output_file.write('\n    ]\n')
    output_file.write('}\n')

    output_file.close()

# Generates the .json file for gates with 1 input and 0 output (aka inputs)
def generate1in0out() :
    lookupArrayForFile = []
    for i in range(6) :
        lookupArrayForFile.append("")
    for directionIn in directions :# Represents the input wire
            # Prepare programm inputs
            gate = "INPUT"
            args = ("./supertile_layout_generator", "-r", gate, directionIn, "1" if directionIn == "0" else "0")

            # Execute programm and read output
            executed_binary = subprocess.Popen(args, stdout=subprocess.PIPE)
            executed_binary.wait()
            output = executed_binary.stdout.read().decode().split(", ")

            # Write array entry
            arrayEntry = '\"' + directionIn + '\": ['

            arrayEntry += '\"' + wireLookup(output[0]) + '\"' # Write first entry seperate so we don't write a ',' where it isn't required
            for wire in output[1:7] :
                arrayEntry += ', \"' + wireLookup(wire) + '\"'
            
            arrayEntry += ']'

            # Add array entry
            lookupArrayForFile[perfectHashFunction1in0out(int(directionIn))] = arrayEntry

    # Write array to file
    output_file = open(r"1in0out_supertile_layouts.json", "w")

    output_file.write('{\n')
    output_file.write('    \"1in0out_supertile_layouts\": [\n')

    output_file.write('        {\n            ' + lookupArrayForFile[0] + '\n        }')# Write first entry seperate so we don't write a ',' where it isn't required
    for entry in lookupArrayForFile[1:6] :
        output_file.write(',\n        {\n            ' + entry + '\n        }')

    output_file.write('\n    ]\n')
    output_file.write('}\n')

    output_file.close()

# Read what should be generated
response = input("Which .json file should be generated? Type the respective number to choose from the following options:\n    a: Every following option at once    1: 1 input, 1 output gates, aka a wire    2: 2 inputs, 1 output gates   3: 1 input, no output gates, aka input\n")
match response :
    case "a" :
        generate1in1out()
        generate2in1out()
        generate1in0out()
    case "1" :
        generate1in1out()
    case "2" :
        generate2in1out()
    case "3" :
        generate1in0out()
    case _ :
        print("Invalid response")