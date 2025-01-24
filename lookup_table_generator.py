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

seperator = "{{-1,-1}}"

def wireLookup(wireName: str) :
    match wireName :
        case "empty" :
            return [99, 99, 99, 99]
        # Standard wires:
        case "wire01" :
            return [0, 1, 99, 99]
        case "wire02" :
            return [0, 2, 99, 99]
        case "wire03" :
            return [0, 3, 99, 99]
        case "wire04" :
            return [0, 4, 99, 99]
        case "wire05" :
            return [0, 5, 99, 99]
        case "wire12" :
            return [1, 2, 99, 99]
        case "wire13" :
            return [1, 3, 99, 99]
        case "wire14" :
            return [1, 4, 99, 99]
        case "wire15" :
            return [1, 5, 99, 99]
        case "wire23" :
            return [2, 3, 99, 99]
        case "wire24" :
            return [2, 4, 99, 99]
        case "wire25" :
            return [2, 5, 99, 99]
        case "wire34" :
            return [3, 4, 99, 99]
        case "wire35" :
            return [3, 5, 99, 99]
        case "wire45" :
            return [4, 5, 99, 99]
        # Double wires with on straight wire
        case "wire14_23" :
            return [1, 4, 2, 3]
        case "wire25_34" :
            return [2, 5, 3, 4]
        case "wire03_45" :
            return [0, 3, 4, 5]
        case "wire14_05" :
            return [1, 4, 0, 5]
        case "wire25_01" :
            return [2, 5, 0, 1]
        case "wire03_12" :
            return [0, 3, 1, 2]
        # Double wires with both wires bend
        case "wire12_34" :
            return [1, 2, 3, 4]
        case "wire23_45" :
            return [2, 3, 4, 5]
        case "wire34_05" :
            return [3, 4, 0, 5]
        case "wire45_01" :
            return [4, 5, 0, 1]
        case "wire05_12" :
            return [0, 5, 1, 2]
        case "wire01_23" :
            return [0, 1, 2, 3]
        # Default case (Error)
        case _:
            return [100, 100, 100, 100]

def coreLookup(coreName) :
    match (coreName[-1]) :
        case "0" :
            return ["2","3"]
        case "2" :
            return ["0","5"]
        case "3" :
            return ["0","5"]
        case "5" :
            return ["2","3"]
        case _:
            return ["ERROR_unknown-core-orientation", "ERROR_unknown-core-orientation"]

def perfectHashFunction2in1out(A, B, C) :
    b = (B - A) % 6 # get B and C into the same 1-5 range for all A
    c = (C - A) % 6
    if (b + c) == 9 :
        basicResult = 12
    else :
        basicResult = 2*(b + c) - abs(b - c) # get 10 different numbers out of b and c
    reducedResult = basicResult - 5
    return 10 * A + reducedResult

def perfectHashFunction1in1out(A, B) :
    if (A * B) == 2 : # move the basic result 5 to the 12, because 5 is used twice and 12 is a single wide gap
        return 12
    elif (A + B) == 9:
        return 0
    else :
        return 2*(A + B) - abs(A - B)

def perfectHashFunction1in0out(A) :
    return A

# returns next position (7 represents the core, 8 represents the outside of the supertile)
def translateDirectionToPosition(currentPosition, direction) :
    match currentPosition :
        case 0 :
            match direction :
                case 2 :
                    return 1
                case 3 :
                    return 7
                case 4 :
                    return 5
                case _ :
                    return 8
        case 1 :
            match direction :
                case 3 :
                    return 2
                case 4 :
                    return 7
                case 5 :
                    return 0
                case _ :
                    return 8
        case 2 :
            match direction :
                case 4 :
                    return 3
                case 5 :
                    return 7
                case 0 :
                    return 1
                case _ :
                    return 8
        case 3 :
            match direction :
                case 5 :
                    return 4
                case 0 :
                    return 7
                case 1 :
                    return 2
                case _ :
                    return 8
        case 4 :
            match direction :
                case 0 :
                    return 5
                case 1 :
                    return 7
                case 2 :
                    return 3
                case _ :
                    return 8
        case 5 :
            match direction :
                case 1 :
                    return 0
                case 2 :
                    return 7
                case 3 :
                    return 4
                case _ :
                    return 8
        case _ :
            print("ERROR in translateDirectionToPosition")
            return 99

def writeInputPathToTable(lookupTableForSupertile, programOutput, inputPosition, lookupTableStartPosition) :
    updatedLookupTablePosition = lookupTableStartPosition
    currentWirePosition = inputPosition
    lastWirePosition = 8
    while True :
        lookupTableEntry = [str(currentWirePosition), "placeholder"]
        wireConnections = wireLookup(programOutput[currentWirePosition + 1])
        if translateDirectionToPosition(currentWirePosition, wireConnections[0]) == lastWirePosition:
            lookupTableEntry[1] = str(wireConnections[0])
            lastWirePosition = currentWirePosition
            currentWirePosition = translateDirectionToPosition(currentWirePosition, wireConnections[1])
            lookupTableForSupertile[updatedLookupTablePosition] = lookupTableEntry
            updatedLookupTablePosition += 1
            if currentWirePosition == 7 :
                break
        elif translateDirectionToPosition(currentWirePosition, wireConnections[1]) == lastWirePosition :
            lookupTableEntry[1] = str(wireConnections[1])
            lastWirePosition = currentWirePosition
            currentWirePosition = translateDirectionToPosition(currentWirePosition, wireConnections[0])
            lookupTableForSupertile[updatedLookupTablePosition] = lookupTableEntry
            updatedLookupTablePosition += 1
            if currentWirePosition == 7 :
                break
        elif translateDirectionToPosition(currentWirePosition, wireConnections[2]) == lastWirePosition :
            lookupTableEntry[1] = str(wireConnections[2])
            lastWirePosition = currentWirePosition
            currentWirePosition = translateDirectionToPosition(currentWirePosition, wireConnections[3])
            lookupTableForSupertile[updatedLookupTablePosition] = lookupTableEntry
            updatedLookupTablePosition += 1
            if currentWirePosition == 7 :
                break
        elif translateDirectionToPosition(currentWirePosition, wireConnections[3]) == lastWirePosition :
            lookupTableEntry[1] = str(wireConnections[3])
            lastWirePosition = currentWirePosition
            currentWirePosition = translateDirectionToPosition(currentWirePosition, wireConnections[2])
            lookupTableForSupertile[updatedLookupTablePosition] = lookupTableEntry
            updatedLookupTablePosition += 1
            if currentWirePosition == 7 :
                break
        else :
            print("ERROR in writeInputPathToTable")
            return 0

    return updatedLookupTablePosition

def writeOutputPathToTable(lookupTableForSupertile, programOutput, outputPosition, lookupTableStartPosition) :
    updatedLookupTablePosition = lookupTableStartPosition
    currentWirePosition = outputPosition
    lastWirePosition = 7
    while True :
        lookupTableEntry = [str(currentWirePosition), "placeholder"]
        wireConnections = wireLookup(programOutput[currentWirePosition + 1])
        if translateDirectionToPosition(currentWirePosition, wireConnections[0]) == lastWirePosition:
            lookupTableEntry[1] = str(wireConnections[0])
            lastWirePosition = currentWirePosition
            currentWirePosition = translateDirectionToPosition(currentWirePosition, wireConnections[1])
            lookupTableForSupertile[updatedLookupTablePosition] = lookupTableEntry
            updatedLookupTablePosition += 1
            if currentWirePosition == 8 :
                break
        elif translateDirectionToPosition(currentWirePosition, wireConnections[1]) == lastWirePosition :
            lookupTableEntry[1] = str(wireConnections[1])
            lastWirePosition = currentWirePosition
            currentWirePosition = translateDirectionToPosition(currentWirePosition, wireConnections[0])
            lookupTableForSupertile[updatedLookupTablePosition] = lookupTableEntry
            updatedLookupTablePosition += 1
            if currentWirePosition == 8 :
                break
        elif translateDirectionToPosition(currentWirePosition, wireConnections[2]) == lastWirePosition :
            lookupTableEntry[1] = str(wireConnections[2])
            lastWirePosition = currentWirePosition
            currentWirePosition = translateDirectionToPosition(currentWirePosition, wireConnections[3])
            lookupTableForSupertile[updatedLookupTablePosition] = lookupTableEntry
            updatedLookupTablePosition += 1
            if currentWirePosition == 8 :
                break
        elif translateDirectionToPosition(currentWirePosition, wireConnections[3]) == lastWirePosition :
            lookupTableEntry[1] = str(wireConnections[3])
            lastWirePosition = currentWirePosition
            currentWirePosition = translateDirectionToPosition(currentWirePosition, wireConnections[2])
            lookupTableForSupertile[updatedLookupTablePosition] = lookupTableEntry
            updatedLookupTablePosition += 1
            if currentWirePosition == 8 :
                break
        else :
            print("check: " + str(translateDirectionToPosition(currentWirePosition, wireConnections[3])))
            print("ERROR in writeOutputPathToTable")
            break

# Generates the .json file for gates with 2 inputs and 1 output
def generate2in1out() :
    lookupTableForFile = []
    for directionOut in directions :# Represents the output wire
        for i in range(10) :
            lookupTableForFile.append("")

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
                        programOutput = executed_binary.stdout.read().decode().split(", ")

                        lookupTableForSupertile = [seperator,seperator,seperator,seperator,seperator,seperator,seperator,seperator,seperator,seperator]

                        # write input wires
                        updatedStartPosition = writeInputPathToTable(lookupTableForSupertile, programOutput, int(directionIn1), 0)
                        updatedStartPosition += 1 # to insert dividing NULL
                        updatedStartPosition = writeInputPathToTable(lookupTableForSupertile, programOutput, int(directionIn2), updatedStartPosition)
                        updatedStartPosition += 1 # to insert dividing NULL
                        
                        # write core
                        lookupTableForSupertile[updatedStartPosition] = coreLookup(programOutput[0])
                        updatedStartPosition += 1

                        # write output wire
                        writeOutputPathToTable(lookupTableForSupertile, programOutput, int(programOutput[0][-1]), updatedStartPosition)

                        # Add array entry
                        lookupTableForFile[perfectHashFunction2in1out(int(directionOut), int(directionIn1), int(directionIn2))] = lookupTableForSupertile

    # Write array to file
    output_file = open(r"lookup_table_2in_1out.hpp", "w")

    output_file.write('#include <array>\n#include <cstdint>\n\nstatic constexpr const std::array<std::array<std::array<int8_t,2>,10>,60> lookup_table_2in_1out = {{\n')

    output_file.write('{{')

    if lookupTableForFile[0][0] != seperator : # Write first entry seperate so we don't write a ',' where it isn't required
        output_file.write('{{' + str(lookupTableForFile[0][0][0]) + ', ' + str(lookupTableForFile[0][0][1]) + '}}')
    else :
        output_file.write(seperator)

    for gate in lookupTableForFile[0][1:10] : # Write first entries seperate so we don't write a ',' where it isn't required
        output_file.write(', ')
        if gate != seperator :
            output_file.write('{{' + str(gate[0]) + ', ' + str(gate[1]) + '}}')
        else :
            output_file.write(seperator)

    output_file.write('}}')

    for supertile in lookupTableForFile[1:60] :
        output_file.write(',\n{{')

        if supertile[0] != seperator : # Write first entry seperate so we don't write a ',' where it isn't required
            output_file.write('{{' + str(supertile[0][0]) + ', ' + str(supertile[0][1]) + '}}')
        else :
            output_file.write(seperator)

        for gate in supertile[1:10] : 
            output_file.write(', ')
            if gate != seperator :
                output_file.write('{{' + str(gate[0]) + ', ' + str(gate[1]) + '}}')
            else :
                output_file.write(seperator)

        output_file.write('}}')
    
    output_file.write('}};\n')

    return

    output_file.write('        {\n            ' + lookupTableForFile[0] + '\n        }')# Write first entry seperate so we don't write a ',' where it isn't required
    for entry in lookupTableForFile[1:60] :
        output_file.write(',\n        {\n            ' + entry + '\n        }')

    output_file.write('\n    ]\n')
    output_file.write('}\n')

    output_file.close()

# Generates the .json file for gates with 1 input and 1 output (aka wires)
def generate1in1outWIRE() :
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
    output_file = open(r"1in1outWIRE_supertile_layouts.json", "w")

    output_file.write('{\n')
    output_file.write('    \"1in1outWIRE_supertile_layouts\": [\n')

    output_file.write('        {\n            ' + lookupArrayForFile[0] + '\n        }')# Write first entry seperate so we don't write a ',' where it isn't required
    for entry in lookupArrayForFile[1:30] :
        output_file.write(',\n        {\n            ' + entry + '\n        }')

    output_file.write('\n    ]\n')
    output_file.write('}\n')

    output_file.close()

def generate1in1outINVERTER() :
    lookupArrayForFile = []
    for i in range(15) :
            lookupArrayForFile.append("")
    for directionOut in directions :# Represents the output wire
        for directionIn in directions :# Represents the input wire
            if directionIn > directionOut :
                # Prepare programm inputs
                gate = "INVERTER"
                args = ("./supertile_layout_generator", "-r", gate, directionIn, directionOut)

                # Execute programm and read output
                executed_binary = subprocess.Popen(args, stdout=subprocess.PIPE)
                executed_binary.wait()
                output = executed_binary.stdout.read().decode().split(", ")

                # Write array entry
                arrayEntry = '\"' + directionOut + directionIn + '\": ['

                arrayEntry += '\"' + coreLookup(output[0]) + '\"' # Write first entry seperate so we don't write a ',' where it isn't required
                for wire in output[1:7] :
                    arrayEntry += ', \"' + wireLookup(wire) + '\"'
                
                arrayEntry += ']'

                # Add array entry
                lookupArrayForFile[perfectHashFunction1in1out(int(directionOut), int(directionIn))] = arrayEntry
    
    # Write array to file
    output_file = open(r"1in1outINVERTER_supertile_layouts.json", "w")

    output_file.write('{\n')
    output_file.write('    \"1in1outINVERTER_supertile_layouts\": [\n')

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
    output_file = open(r"0in1out_supertile_layouts.json", "w")

    output_file.write('{\n')
    output_file.write('    \"0in1out_supertile_layouts\": [\n')

    output_file.write('        {\n            ' + lookupArrayForFile[0] + '\n        }')# Write first entry seperate so we don't write a ',' where it isn't required
    for entry in lookupArrayForFile[1:6] :
        output_file.write(',\n        {\n            ' + entry + '\n        }')

    output_file.write('\n    ]\n')
    output_file.write('}\n')

    output_file.close()

# Read what should be generated
response = input("Which .json file should be generated? Type the respective number to choose from the following options:\n    a: Every following option at once    1: 1 input, 1 output gates, (wire)    2: 1 input, 1 output gates, (inverter)    3: 2 inputs, 1 output gates   4: no input, 1 output gate, aka input\n")
match response :
    case "a" :
        generate1in1outWIRE()
        generate1in1outINVERTER()
        generate2in1out()
        generate1in0out()
    case "1" :
        generate1in1outWIRE()
    case "2" :
        generate1in1outINVERTER()
    case "3" :
        generate2in1out()
    case "4" :
        generate1in0out()
    case _ :
        print("Invalid response")