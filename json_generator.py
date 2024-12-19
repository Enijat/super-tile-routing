import subprocess
import sys

lookupArrayForFile = []
directions = ["0", "1", "2", "3", "4", "5"]

#TODO beschreibung dieser Methode
def wireLookup(wireName) :
    match wireName :
        case "empty" :
            return "empty"
        # Standard wires:
        case "wire01" :
            return "0null"
        case "wire02" :
            return "1null"
        case "wire03" :
            return "2null"
        case "wire04" :
            return "3null"
        case "wire05" :
            return "4null"
        case "wire12" :
            return "5null"
        case "wire13" :
            return "6null"
        case "wire14" :
            return "7null"
        case "wire15" :
            return "8null"
        case "wire23" :
            return "9null"
        case "wire24" :
            return "10null"
        case "wire25" :
            return "12null"
        case "wire34" :
            return "13null"
        case "wire35" :
            return "14null"
        case "wire45" :
            return "15null"
        # Double wires with on straight wire
        case "wire14_23" :
            return "16null"
        case "wire25_34" :
            return "17null"
        case "wire03_45" :
            return "18null"
        case "wire14_05" :
            return "19null"
        case "wire25_01" :
            return "20null"
        case "wire03_12" :
            return "21null"
        # Double wires with both wires bend
        case "wire12_34" :
            return "22null"
        case "wire23_45" :
            return "23null"
        case "wire34_05" :
            return "24null"
        case "wire45_01" :
            return "25null"
        case "wire05_12" :
            return "26null"
        case "wire01_23" :
            return "27null"
        # Default case (Error)
        case _:
            return "ERROR_wire-not-found"

#This function is perfect only by definition, but not by execution, meaning that there is good chance there is a simpler function with the same result
def perfectHashFunction(A, B, C) :
    b = (B - A) % 6
    c = (C - A) % 6
    basicResult = 2*(b + c) + abs(b - c)
    reducedResult = ((((basicResult - 8) % 13) - 4) % 11) - 1 # reduces the 10 different numbers in basicResult to the range 0 - 9
    return 10 * A + reducedResult

#This function generates the .json file for gates with 2 inputs and 1 output
def generate2in1out() :
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
                        args = ("./super-tile_layout_generator", "-r", gate, inputWires, outputWire)

                        # Execute programm and read output
                        executed_binary = subprocess.Popen(args, stdout=subprocess.PIPE)
                        executed_binary.wait()
                        output = executed_binary.stdout.read().decode().split(", ")
                        supertileWires = ["", "", "", "", "", ""]
                        supertileWires[0:6] = output[1:7]

                        # Write array entry
                        arrayEntry = '\"' + directionOut + directionIn1 + directionIn2 + '\": ['

                        arrayEntry += '\"' + wireLookup(supertileWires[0]) + '\"' # Write first entry seperate so we don't write a ',' where it isn't required
                        for wire in supertileWires[1:6] :
                            arrayEntry += ', \"' + wireLookup(wire) + '\"'
                        
                        arrayEntry += ']'

                        # Add array entry
                        lookupArrayForFile[perfectHashFunction(int(directionOut), int(directionIn1), int(directionIn2))] = arrayEntry

    # Write array to file
    output_file = open(r"2in1out_super-tile_layouts.json", "w")

    output_file.write('{\n')
    output_file.write('    \"2in1out_super-tile_layouts\": [\n')

    output_file.write('        {\n            ' + lookupArrayForFile[0] + '\n        }')# Write first entry seperate so we don't write a ',' where it isn't required
    for entry in lookupArrayForFile[1:60] :
        output_file.write(',\n        {\n            ' + entry + '\n        }')

    output_file.write('\n    ]\n')
    output_file.write('}\n')

    output_file.close()

#TODO make this custom to wires
def generate1in1out() :
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
                        args = ("./super-tile_layout_generator", "-r", gate, inputWires, outputWire)

                        # Execute programm and read output
                        executed_binary = subprocess.Popen(args, stdout=subprocess.PIPE)
                        executed_binary.wait()
                        output = executed_binary.stdout.read().decode().split(", ")
                        supertileWires = ["", "", "", "", "", ""]
                        supertileWires[0:6] = output[1:7]

                        # Write array entry
                        arrayEntry = '\"' + directionOut + directionIn1 + directionIn2 + '\": ['

                        arrayEntry += '\"' + wireLookup(supertileWires[0]) + '\"' # Write first entry seperate so we don't write a ',' where it isn't required
                        for wire in supertileWires[1:6] :
                            arrayEntry += ', \"' + wireLookup(wire) + '\"'
                        
                        arrayEntry += ']'

                        # Add array entry
                        lookupArrayForFile[perfectHashFunction(int(directionOut), int(directionIn1), int(directionIn2))] = arrayEntry

    # Write array to file
    output_file = open(r"1in1out_supertile_layouts.json", "w")

    output_file.write('{\n')
    output_file.write('    \"1in1out_supertile_layouts\": [\n')

    output_file.write('        {\n            ' + lookupArrayForFile[0] + '\n        }')# Write first entry seperate so we don't write a ',' where it isn't required
    for entry in lookupArrayForFile[1:60] :
        output_file.write(',\n        {\n            ' + entry + '\n        }')

    output_file.write('\n    ]\n')
    output_file.write('}\n')

    output_file.close()

# Read what should be generated
response = input("Which .json file should be generated? Type the respective number to choose from the following options:\n    1: 1 input, 1 output gates, aka a wire    2: 2 inputs, 1 output gates")
match response :
    case "1" :
        generate1in1out()
    case "2" :
        generate2in1out()
    case _ :
        print("Invalid response")