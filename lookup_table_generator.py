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
DIRECTIONS = ["0", "1", "2", "3", "4", "5"]

EMPTY = "{{-1,-1}}"

def directionLookup(direction: str) :
    match direction :
        case "-1" :
            return "X"
        case "0" :
            return "NE"
        case "1" :
            return "E"
        case "2" :
            return "SE"
        case "3" :
            return "SW"
        case "4" :
            return "W"
        case "5" :
            return "NW"
        case "7" :
            return "CORE"
        case _ :
            print("ERROR in directionLookup")
            return direction

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

def perfectHashFunction21(A, B, C) :
    b = (B - A) % 6 # get B and C into the same 1-5 range for all A
    c = (C - A) % 6
    if (b + c) == 9 :
        basicResult = 12
    else :
        basicResult = 2*(b + c) - abs(b - c) # get 10 different numbers out of b and c
    reducedResult = basicResult - 5
    return 10 * A + reducedResult

def perfectHashFunction11(A, B) :
    if (A > B) :
        base = 15
    else :
        base = 0
    if (A * B) == 2 : # move the basic result 5 to the 12, because 5 is used twice and 12 is a single wide gap
        return 12 + base
    elif (A + B) == 9:
        return 0 + base
    else :
        return 2*(A + B) - abs(A - B) + base

def perfectHashFunction10(A) :
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
    return updatedLookupTablePosition

def writeTableStart(outputFile, totalSize, supertileSize, name) :
    outputFile.write('\nstatic constexpr const std::array<std::array<std::array<int8_t,2>,' + str(supertileSize) + '>,' + str(totalSize) + '> ' + name + ' = {{\n')

def writeTable(outputFile, table) :
    outputFile.write('{{')

    if table[0][0] != EMPTY : # Write first entry seperate so we don't write a ',' where it isn't required
        outputFile.write('{{' + directionLookup(str(table[0][0][0])) + ', ' + directionLookup(str(table[0][0][1])) + '}}')
    else :
        outputFile.write("{{X, X}}")

    for gate in table[0][1:len(table[0])] : # Write first entries seperate so we don't write a ',' where it isn't required
        outputFile.write(', ')
        if gate != EMPTY :
            outputFile.write('{{' + directionLookup(str(gate[0])) + ', ' + directionLookup(str(gate[1])) + '}}')
        else :
            outputFile.write("{{X, X}}")

    outputFile.write('}}')

    for supertile in table[1:(len(table))] :
        outputFile.write(',\n{{')

        if supertile[0] != EMPTY : # Write first entry seperate so we don't write a ',' where it isn't required
            outputFile.write('{{' + directionLookup(str(supertile[0][0])) + ', ' + directionLookup(str(supertile[0][1])) + '}}')
        else :
            outputFile.write("{{X, X}}")

        for gate in supertile[1:len(supertile)] : 
            outputFile.write(', ')
            if gate != EMPTY :
                outputFile.write('{{' + directionLookup(str(gate[0])) + ', ' + directionLookup(str(gate[1])) + '}}')
            else :
                outputFile.write("{{X, X}}")

        outputFile.write('}}')

def writeTableEnd(outputFile) :
    outputFile.write('}};\n')

def generate2in1out(outputFile) :
    lookupTableForFile = []
    for directionOut in DIRECTIONS :# Represents the output wire
        for i in range(10) :
            lookupTableForFile.append("")

        for directionIn1 in DIRECTIONS :# Represents the first input wire
            if directionIn1 != directionOut :
                for directionIn2 in DIRECTIONS : # Represents the second input wire
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

                        # prepare lookup table entry for this gate
                        lookupTableForSupertile = [EMPTY,EMPTY,EMPTY,EMPTY,EMPTY,EMPTY,EMPTY,EMPTY,EMPTY,EMPTY]

                        # write input wires
                        updatedStartPosition = writeInputPathToTable(lookupTableForSupertile, programOutput, int(directionIn1), 0)
                        updatedStartPosition += 1 # to insert dividing EMPTY
                        updatedStartPosition = writeInputPathToTable(lookupTableForSupertile, programOutput, int(directionIn2), updatedStartPosition)
                        updatedStartPosition += 1 # to insert dividing EMPTY
                        
                        # write core
                        lookupTableForSupertile[updatedStartPosition] = coreLookup(programOutput[0])
                        updatedStartPosition += 1

                        # write output wire
                        writeOutputPathToTable(lookupTableForSupertile, programOutput, int(programOutput[0][-1]), updatedStartPosition)

                        # Add array entry
                        lookupTableForFile[perfectHashFunction21(int(directionOut), int(directionIn1), int(directionIn2))] = lookupTableForSupertile
                        

    # Write array to file
    writeTableStart(outputFile, 60, 10, 'lookup_table_2in1out')
    writeTable(outputFile, lookupTableForFile)
    writeTableEnd(outputFile)

def generate1in2out(outputFile) :
    lookupTableForFile = []
    for directionIn in DIRECTIONS :# Represents the output wire
        for i in range(10) :
            lookupTableForFile.append("")

        for directionOut1 in DIRECTIONS :# Represents the first input wire
            if directionOut1 != directionIn :
                for directionOut2 in DIRECTIONS : # Represents the second input wire
                    if directionOut2 != directionIn and directionOut2 != directionOut1 and int(directionOut2) > int(directionOut1) :
                        # Prepare programm inputs
                        gate = "SAMPLE" # fixed to sample as an input because this allows for all four required core gate rotations which every gate, that will be used, can be represented in
                        inputWire = directionIn
                        outputWires = directionOut1 + directionOut2
                        args = ("./supertile_layout_generator", "-r", gate, outputWires, inputWire)

                        # Execute programm and read output
                        executed_binary = subprocess.Popen(args, stdout=subprocess.PIPE)
                        executed_binary.wait()
                        programOutput = executed_binary.stdout.read().decode().split(", ")

                        # prepare lookup table entry for this gate
                        lookupTableForSupertile = [EMPTY,EMPTY,EMPTY,EMPTY,EMPTY,EMPTY,EMPTY,EMPTY,EMPTY,EMPTY]

                        # write intput wire
                        updatedStartPosition = writeInputPathToTable(lookupTableForSupertile, programOutput, int(directionIn), 0)
                        updatedStartPosition += 1 # to insert dividing EMPTY
                        
                        # write core
                        lookupTableForSupertile[updatedStartPosition] = [str(programOutput[0][-1]),str(-1)]
                        updatedStartPosition += 1

                        # write output wires
                        if int(programOutput[0][-1]) == 2 or int(programOutput[0][-1]) == 3 :
                            outputPosition1 = 0
                            outputPosition2 = 5
                        elif int(programOutput[0][-1]) == 0 or int(programOutput[0][-1]) == 5 :
                            outputPosition1 = 2
                            outputPosition2 = 3
                        else :
                            print("ERROR in generate1in2out")
                            return
                        updatedStartPosition = writeOutputPathToTable(lookupTableForSupertile, programOutput, outputPosition1, updatedStartPosition)
                        updatedStartPosition += 1 # to insert dividing EMPTY
                        updatedStartPosition = writeOutputPathToTable(lookupTableForSupertile, programOutput, outputPosition2, updatedStartPosition)

                        # Add array entry
                        lookupTableForFile[perfectHashFunction21(int(directionIn), int(directionOut1), int(directionOut2))] = lookupTableForSupertile

    # Write array to file
    writeTableStart(outputFile, 60, 10, 'lookup_table_1in2out')
    writeTable(outputFile, lookupTableForFile)
    writeTableEnd(outputFile)

def generate1in1outWIRE(outputFile) :
    lookupTableForFile = []
    for i in range(30) :
            lookupTableForFile.append("")
    for directionOut in DIRECTIONS :# Represents the output wire
        for directionIn in DIRECTIONS :# Represents the input wire
            if directionIn != directionOut :
                # Prepare programm inputs
                gate = "WIRE"
                args = ("./supertile_layout_generator", "-r", gate, directionIn, directionOut)

                # Execute programm and read output
                executed_binary = subprocess.Popen(args, stdout=subprocess.PIPE)
                executed_binary.wait()
                programOutput = executed_binary.stdout.read().decode().split(", ")

                # prepare lookup table entry for this gate
                lookupTableForSupertile = [EMPTY,EMPTY,EMPTY]

                # write input wire
                updatedStartPosition = writeInputPathToTable(lookupTableForSupertile, programOutput, int(directionIn), 0)

                # write core
                lookupTableForSupertile[updatedStartPosition] = ["7", directionIn]
                updatedStartPosition += 1
                
                # write output wire
                writeOutputPathToTable(lookupTableForSupertile, programOutput, int(directionOut), updatedStartPosition)

                # Add array entry
                lookupTableForFile[perfectHashFunction11(int(directionIn), int(directionOut))] = lookupTableForSupertile

    # Write array to file
    writeTableStart(outputFile, 30, 3, 'lookup_table_1in1out_WIRE')
    writeTable(outputFile, lookupTableForFile)
    writeTableEnd(outputFile)

def getInverterCore(programOutput) :
    match programOutput[0][-3] :
        case "0" :
            return ["7","0"]
        case "2" :
            return ["7","2"]
        case "3" :
            return ["7","3"]
        case "5" :
            return ["7","5"]

def generate1in1outINVERTER(outputFile) :
    lookupTableForFile = []
    for i in range(30) :
            lookupTableForFile.append("")
    for directionOut in DIRECTIONS :# Represents the output wire
        for directionIn in DIRECTIONS :# Represents the input wire
            if directionIn != directionOut :
                # Prepare programm inputs
                gate = "INVERTER"
                args = ("./supertile_layout_generator", "-r", gate, directionIn, directionOut)

                # Execute programm and read output
                executed_binary = subprocess.Popen(args, stdout=subprocess.PIPE)
                executed_binary.wait()
                programOutput = executed_binary.stdout.read().decode().split(", ")

                # prepare lookup table entry for this gate
                lookupTableForSupertile = [EMPTY,EMPTY,EMPTY,EMPTY,EMPTY,EMPTY]

                # write input wire
                updatedStartPosition = writeInputPathToTable(lookupTableForSupertile, programOutput, int(directionIn), 0)
                updatedStartPosition += 1 # to insert dividing EMPTY

                # write core
                lookupTableForSupertile[updatedStartPosition] = getInverterCore(programOutput)
                updatedStartPosition += 1

                # write output wire
                writeOutputPathToTable(lookupTableForSupertile, programOutput, int(programOutput[0][-1]), updatedStartPosition)

                # Add array entry
                lookupTableForFile[perfectHashFunction11(int(directionIn), int(directionOut))] = lookupTableForSupertile
    
    # Write array to file
    writeTableStart(outputFile, 30, 6, 'lookup_table_1in1out_INVERTER')
    writeTable(outputFile, lookupTableForFile)
    writeTableEnd(outputFile)

def generate1in0out(outputFile) :
    lookupTableForFile = []
    for i in range(6) :
        lookupTableForFile.append("")
    for directionIn in DIRECTIONS :# Represents the input wire
            # Prepare programm inputs
            gate = "INPUT"
            args = ("./supertile_layout_generator", "-r", gate, directionIn, "1" if directionIn == "0" else "0")

            # Execute programm and read output
            executed_binary = subprocess.Popen(args, stdout=subprocess.PIPE)
            executed_binary.wait()
            programOutput = executed_binary.stdout.read().decode().split(", ")
            
            # prepare lookup table entry for this gate
            lookupTableForSupertile = [EMPTY,EMPTY]

            # write input wires
            updatedStartPosition = writeInputPathToTable(lookupTableForSupertile, programOutput, int(directionIn), 0)

            # write core
            lookupTableForSupertile[updatedStartPosition] = ["7", directionIn]

            # Add array entry
            lookupTableForFile[perfectHashFunction10(int(directionIn))] = lookupTableForSupertile

    # Write array to file
    outputFile.write('\n//Trivial, so it\'s not actually used')
    writeTableStart(outputFile, 6, 2, 'lookup_table_1in0out')
    writeTable(outputFile, lookupTableForFile)
    writeTableEnd(outputFile)

def generate0in1out(outputFile) :
    lookupTableForFile = []
    for i in range(6) :
        lookupTableForFile.append("")
    for directionOut in DIRECTIONS :# Represents the input wire          
            # prepare lookup table entry for this gate
            lookupTableForSupertile = [EMPTY]

            # write output wire
            lookupTableForSupertile[0] = [directionOut,"-1"]

            # Add array entry
            lookupTableForFile[perfectHashFunction10(int(directionOut))] = lookupTableForSupertile

    # Write array to file
    outputFile.write('\n//Trivial, so it\'s not actually used')
    writeTableStart(outputFile, 6, 2, 'lookup_table_0in1out')
    writeTable(outputFile, lookupTableForFile)
    writeTableEnd(outputFile)

outputFile = open(r"supertile_lookup_tables.hpp", "w")
outputFile.write('#include <array>\n#include <cstdint>\n\nenum hex_direction_or_position {\n    NE = 0,\n    E = 1,\n    SE = 2,\n    SW = 3,\n    W = 4,\n    NW = 5,\n    X = 6,\n    CORE = 7\n};\n')

generate2in1out(outputFile)
generate1in2out(outputFile)
generate1in1outWIRE(outputFile)
generate1in1outINVERTER(outputFile)
generate1in0out(outputFile)
generate0in1out(outputFile)

outputFile.close()