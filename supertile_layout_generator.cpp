#include <iostream>
#include <getopt.h>
#include <string.h>

const char* helpMessage =
    "Program usage:\n"
    "    %s core-gate-type input-positions output-positions\n"
    "  Positional arguments:\n"
    "    core-gate-type        The name of the gate in the center. Example: OR\n"
    "    input-positions       The positions of the required input positions to the super-tile. Example: 05\n"
    "    output-positions      The positions of the required output positions from the super-tile. Example: 2\n"
    "  Optional arguments:\n"
    "    -h                    Prints (this) help message.\n"
    "    -l                    Prints a more detailed layout with the naming system.\n"
    "    -c                    Prints list with possible core gates.\n"
    "    -t                    Print out the time it took to calculate the layout, if a layout is generated.\n"
    "    -p                    Print the wire paths for better visualisation, this will HEAVILY impact the measured time for the layout calculation, which is show by -t\n"
    "    -r                    Prints a reduced output, usefull for further processing. The order of the gates is:\n"
    "                          [Core, 0, 1, 2, 3, 4, 5]\n"
    "  Example:\n"
    "    %s or 40 2 -t\n"
    "    (This generates a tile-layout with an or-gate in the middle and the two super-tile-inputs 4 and 0 and the super-tile-output 2,\n"
    "     while recording and displaying the time it took to calculate this layout)\n"
    "  Naming system for the tiles in a super tile:\n"
    "         5    0\n"
    "       4  Core  1\n"
    "         3    2\n"
    "    (For a more detailed layout add -l as option.)\n";

const char* layoutExplanation =
    "Supertile layout explanation:\n"
    "   (Tiles) in hexagons next to each other:       (Tiles) with the possible connections:\n"
    "\n"
    "           ˍ---¯¯¯-A-ˍ ˍ---¯¯¯---ˍ                              A                     \n"
    "          |           |           |                            /                      \n"
    "          |    (5)    B    (0)    A                         (5) -- B -- (0) -- A      \n"
    "          |           |           |                        /   \\       /   \\          \n"
    "     ˍ-A-¯ ¯-B-ˍ ˍ-C-¯ ¯-C-ˍ ˍ-B-¯ ¯---ˍ            A     B     C     C     B         \n"
    "    |           |           |           |            \\   /       \\   /        \\        \n"
    "    |    (4)    C   (Core)  C    (1)    |             (4) -- C --(Core)- C -- (1)     \n"
    "    |           |           |           |                \\       /   \\       /   \\    \n"
    "     ¯---ˍ ˍ-B-¯ ¯-C-ˍ ˍ-C-¯ ¯-B-ˍ ˍ-A-¯                  B     C     C     B     A   \n"
    "          |           |           |                        \\   /       \\   /          \n"
    "          A    (3)    B    (2)    |                    A -- (3) -- B -- (2)           \n"
    "          |           |           |                                    /              \n"
    "           ¯---ˍˍˍ---¯ ¯-A-ˍˍˍ---¯                                    A               \n"
    "\n"
    "  Connection naming:\n"
    "    A = Connections to the outside of the super tile.\n"
    "    B = Connections in between the tiles of the super tile for routing.\n"
    "    C = Connections to the core (which contains the logic gate) of the supertile\n";

//For wires the naming "inPositions" and "outPositions" may not necessarily be true, since they are uni-directional
struct gate {
    const char* name;
    int* inPositions;
    int* outPositions;
    int inPositionsSize;
    int outPositionsSize;
};

struct superTile {
    gate** wires; //They are listed clockwise, starting at position 0, see help message for further info (Length of this list is always 6)
    gate* core;
};

//up to 5 is probably overkill, but better be save then sorry
//"NaW" = "Not a Wire" (This is a placeholder for initialisation of the matrix)
enum wireType {
    NaW, in1, in2, in3, in4, in5, out1, out2, out3, out4, out5
};

//The numbers for each wire are the combination of thier parts
enum wire {
    empty = 0, //in case there is no wire needed in this part of the super tile
    wire01 = 1, wire02 = 2, wire03 = 4, wire04 = 8, wire05 = 16, wire12 = 32, wire13 = 64, wire14 = 128, wire15 = 256, wire23 = 512, wire24 = 1024, wire25 = 2048, wire34 = 4096, wire35 = 8192, wire45 = 16384, //standard wires
    wire14_23 = 640, wire25_34 = 6144, wire03_45 = 16388, wire14_05 = 144, wire25_01 = 2049, wire03_12 = 36, //double wires with one straight wire     TODO actually test these / construct them, currently it is just assumed they would work
    wire12_34 = 4128, wire23_45 = 16896, wire34_05 = 4112, wire45_01 =16385, wire05_12 = 48, wire01_23 = 513 //double wires with two bend wires        TODO actually test these / construct them, currently it is just assumed they would work
};

//Section for defining methods
void printHelpMessage(const char*);
void printLayoutExplanation();
void printCoreGateList();
int* extractPositions(char*, int);
superTile* solver2in1out(int*, int*, char*, bool);
    gate* getYCore(int*, int*);
    gate* getYCoreUpright(int*, int*);
    bool goClockwise(int, int, int);
    int mod(int, int);
    int* getWireTileConnections(wireType**, int);
    bool getWireTile(int*, int, gate*);
    bool giveWireGateName(wire, gate*);
superTile* solver1in1out(int*, int*, char*, bool);
superTile* solver1in0out(int*, bool);
void printLayout(superTile*);
    void setNormalisedString(const char*, char*);
    void setNormalisedNumbers(int*, int, char*);
void printReducedLayout(superTile*);
void printWirePaths(wireType**, gate*);
    char getWireTypeSynonymA(wireType);
    char getWireTypeSynonymB(wireType);
void freeGate(gate*);

//TODO generally replace int with to locally shortest required variant, like uint8_t DON'T FORGET TO CHANGE THE SIZEOF IN MALLOC FOR THAT!! (int am besten gar nicht vorkommen lassen)
//TODO maybe reduce the amount of times the full help message get's automatically printed
//TODO bei der benennung von gates / outergates / tiles / wires konsistent werden
//TODO im ganzen Programm sind viele checks die davon ausgehen das andere methode quatsch machen könnten, die könnte man für performance los werden
int main(int argc, char** argv)
{

    //For help message
    const char* programName = argv[0];

    bool trackTime = false;
    bool reducedOutput = false;
    bool printTheWirePaths = false;

    //Get optional Arguments
    int opt;
    bool exit = false;
    while ((opt = getopt(argc, argv, "hlctpr")) != -1) {
        switch (opt) {
            case 'h':
                printHelpMessage(programName);
                exit = true;
                break;
            case 'l':
                printLayoutExplanation();
                exit = true;
                break;
            case 'c':
                printCoreGateList();
                exit = true;
                break;
            case 't':
                trackTime = true;
                break;
            case 'r':
                reducedOutput = true;
                break;
            case 'p':
                printTheWirePaths = true;
                break;
            default:
                printf("Reffer to %s -h for further information.\n", programName);
                return EXIT_FAILURE;
        }
    }
    if (exit) {
        return EXIT_SUCCESS;
    }

    //Get positional Arguments
    int position = optind;
    if(position >= argc) {
        printf("Missing positional argument 'core-gate-type'! For more info, add optional argument -h.\n");
        return EXIT_FAILURE;
    }
    char* coreName = argv[position];

    position++;

    if(position >= argc) {
        printf("Missing positional argument 'input-positions'! For more info, add optional argument -h.\n");
        return EXIT_FAILURE;
    }
    int inPositionsSize;
    for(inPositionsSize = 0; argv[position][inPositionsSize] != 0; inPositionsSize++) {}
    int* inPositions = extractPositions(argv[position], inPositionsSize);

    position++;

    if(position >= argc) {
        printf("Missing positional argument 'output-positions'! For more info, add optional argument -h.\n");
        free(inPositions);
        return EXIT_FAILURE;
    }
    int outPositionsSize;
    for(outPositionsSize = 0; argv[position][outPositionsSize] != 0; outPositionsSize++) {}
    int* outPositions = extractPositions(argv[position], outPositionsSize);

    //Check if there already is a conflict in the given positions:
    for(int x = 0; x < inPositionsSize; x++) {
        for(int y = 0; y < outPositionsSize; y++) {
            if(inPositions[x] == outPositions[y]) {
                printf("Conflic between inputs and outputs, position %i is used by both. For more info, add optional argument -h.\n", inPositions[x]);
                free(inPositions);
                free(outPositions);
                return EXIT_FAILURE;
            }
        }
    }

    struct timespec start;
    struct timespec end;

    superTile* finishedLayout;
    //Check number of in/out and chose fitting method
    if(inPositionsSize == 2 && outPositionsSize == 1) {
        clock_gettime(CLOCK_MONOTONIC, &start); //Runtime measurement
        finishedLayout = solver2in1out(inPositions, outPositions, coreName, printTheWirePaths);
        clock_gettime(CLOCK_MONOTONIC, &end); //Runtime measurement

        if (finishedLayout == NULL) {
            free(inPositions);
            free(outPositions);
            return EXIT_FAILURE;
        }
    } else if (inPositionsSize == 1 && outPositionsSize == 1 && strcmp(coreName, "INPUT")) {
        clock_gettime(CLOCK_MONOTONIC, &start); //Runtime measurement
        finishedLayout = solver1in1out(inPositions, outPositions, coreName, printTheWirePaths);
        clock_gettime(CLOCK_MONOTONIC, &end); //Runtime measurement

        if (finishedLayout == NULL) {
            free(inPositions);
            free(outPositions);
            return EXIT_FAILURE;
        }
    } else if (inPositionsSize == 1 && !strcmp(coreName, "INPUT")) {
        clock_gettime(CLOCK_MONOTONIC, &start); //Runtime measurement
        finishedLayout = solver1in0out(inPositions, printTheWirePaths);
        clock_gettime(CLOCK_MONOTONIC, &end); //Runtime measurement

        if (finishedLayout == NULL) {
            free(inPositions);
            free(outPositions);
            return EXIT_FAILURE;
        }
    } else {
        printf("There has been no solver implemented for a core gate with %i inputs and %i outputs. For more info, add optional argument -h.\n", inPositionsSize, outPositionsSize);
        free(inPositions);
        free(outPositions);
        return EXIT_SUCCESS;
    }

    if (trackTime) {
        printf("Time:\n  This calculation took %f milliseconds.\n", (end.tv_sec - start.tv_sec + 1e-9 * (end.tv_nsec - start.tv_nsec))*1000);
    }

    //Print finished Layout to the console
    if(reducedOutput) {
        printReducedLayout(finishedLayout);
    } else {
        printLayout(finishedLayout);
    }
    
    //Free all used recources
    free(inPositions);
    free(outPositions);
    freeGate(finishedLayout->core);
    for (uint8_t x = 0; x < 6; x++) {
        freeGate(finishedLayout->wires[x]);
    }
    free(finishedLayout);
}

void printHelpMessage (const char* programName) {
    printf(helpMessage, programName, programName);
}

void printLayoutExplanation() {
    fputs(layoutExplanation, stdout);
}

//TODO change the gate list to lookup from file or move the list to the top and use it here.
void printCoreGateList() {
    printf("Core gate List:\n    OR\n    SAMPLE\n    WIRE\n    INPUT (if this core is chosen, the given output is ignored)\n");
}

int* extractPositions (char* positionsText, int textSize) {
    int* positions = (int*) malloc(sizeof(int) * textSize);
    for(int i = 0; i < textSize; i++) {
        positions[i] = positionsText[i] - 48; // Conversion between ascii and the corresponding number
    }
    return positions;
}

superTile* solver2in1out(int* inPositions, int* outPosition, char* coreName, bool printTheWirePaths) {
    /** Matrix structure: Each (triple) represents one tile, and the respective [tree numbers] represent the core-connection, the next-clockwise-tile-connection and the outwards-connection, see diagram:
     * 
     *         ˍ---¯ ¯[2]ˍ ˍ---¯ ¯---ˍ
     *        |       /   |           |
     *        |    (5) --[1]   (0) --[2]
     *        |       \   |   /   \   |
     *   ˍ[2]¯ ¯[1]ˍ ˍ[0]¯ ¯[0]ˍ ˍ[1]¯ ¯---ˍ
     *  |   \   /   |           |           |
     *  |    (4) --[0]   Core  [0]-- (1)    |
     *  |           |           |   /   \   |
     *   ¯---ˍ ˍ[1]¯ ¯[0]ˍ ˍ[0]¯ ¯[1]ˍ ˍ[2]¯
     *        |   \   /   |   \       |
     *       [2]-- (3)   [1]-- (2)    |
     *        |           |   /       |
     *         ¯---ˍ ˍ---¯ ¯[2]ˍ ˍ---¯
     */
    wireType** outerTiles = (wireType**) malloc(sizeof(wireType*)*6);
    for (int x = 0; x < 6; x++) {
        outerTiles[x] = (wireType*) malloc(sizeof(wireType)*3);
        for (int y = 0; y < 3; y++) {
            outerTiles[x][y] = NaW;
        }
    }

    gate* core;

    //TODO Liste von Cores hinzufügen und diese auch nutzen um Hilfsnachricht entsprechend an zu passen.
    //TODO This is a placeholder, in the future an actual lookup has to happen and it would be wise to check if the given core has to required amount of in/out connections
    if (!strcmp(coreName, "OR")) {
        core = getYCoreUpright(inPositions, outPosition);
        if (core == NULL) {
            printf("There is no core gate orientation that would generate a possible layout.\n");
            return NULL;
        }
        core->name = coreName;
        
        //TODO vvvvvv ############################### until this same sigen this has been copied from below, needs refactoring and cleanup ############################### vvvvvv
        //Connect output
        outerTiles[core->outPositions[0]][0] = out1;
        outerTiles[outPosition[0]][2] = out1;
        bool clockwiseOutput = goClockwise(core->outPositions[0], outPosition[0], (core->outPositions[0] + 1) % 6); //TODO eigene goClockwise methode schreiben, sonst muss man 'otherStart' wie hier mit etwas füllen das eigentlich algorithmisch unnötig ist weil der Output nie gegenüber liegen sollte
        if (core->outPositions[0] != outPosition[0]) {
           int currentPos = core->outPositions[0];
           if (clockwiseOutput) {
               while (currentPos != outPosition[0]) {
                   outerTiles[currentPos][1] = out1;
                   currentPos = (currentPos + 1) % 6;;
               }
           } else {
               do {
                   currentPos = mod((currentPos - 1), 6);
                   outerTiles[currentPos][1] = out1;
               } while (currentPos != outPosition[0]);
           }
        }

        //Connect inputs

        //Get the superTileConnections and the coreConnections in an order in which you can connect them without crossings
        //TODO optimierung durch sortierte Eingabe möglich?
        int coreIns[2];
        int superTileIns[2];
        int temp = 0;
        int pos = outPosition[0];
        //TODO beiden Suchen kombinieren
        while (temp < 2) { //core
            if (core->inPositions[0] == pos || core->inPositions[1] == pos) {
                coreIns[temp] = pos;
                temp++;
            }
            if (clockwiseOutput) {
                pos = (pos + 1 ) % 6;
            } else {
                pos = mod((pos - 1 ), 6);
            }
        }
        temp = 0;
        pos = outPosition[0];
        while (temp < 2) { //superTile
            if (inPositions[0] == pos || inPositions[1] == pos) {
                superTileIns[temp] = pos;
                temp++;
            }
            if (clockwiseOutput) {
                pos = (pos + 1 ) % 6;
            } else {
                pos = mod((pos - 1 ), 6);
            }
        }
        //Generate input path ...
        //number 1.
        outerTiles[coreIns[0]][0] = in1;
        outerTiles[superTileIns[0]][2] = in1;
        if (coreIns[0] != superTileIns[0]) {
            int currentPos = coreIns[0];
            if (goClockwise(coreIns[0], superTileIns[0], coreIns[1])) {
                while (currentPos != superTileIns[0]) {
                    outerTiles[currentPos][1] = in1;
                    currentPos = (currentPos + 1) % 6;
                }
            } else {
                do {
                    currentPos = mod((currentPos - 1), 6);
                    outerTiles[currentPos][1] = in1;
                } while (currentPos != superTileIns[0]);
            }
        }
        //number 2.
        outerTiles[coreIns[1]][0] = in2;
        outerTiles[superTileIns[1]][2] = in2;
        if (coreIns[1] != superTileIns[1]) {
            int currentPos = coreIns[1];
            if (goClockwise(coreIns[1], superTileIns[1], coreIns[0])) {
                while (currentPos != superTileIns[1]) {
                    outerTiles[currentPos][1] = in2;
                    currentPos = (currentPos + 1) % 6;
                }
            } else {
                do {
                    currentPos = mod((currentPos - 1), 6);
                    outerTiles[currentPos][1] = in2;
                } while (currentPos != superTileIns[1]);
            }
        }

        //TODO ^^^^^^ ############################### this has been copied from below, needs refactoring and cleanup ############################### ^^^^^^
    } else if (!strcmp(coreName, "SAMPLE")) {
        //Get best fitting core rotation
        core = getYCore(inPositions, outPosition);
        core->name = coreName;

        //Connect output
        outerTiles[core->outPositions[0]][0] = out1;
        outerTiles[outPosition[0]][2] = out1;
        bool clockwiseOutput = goClockwise(core->outPositions[0], outPosition[0], (core->outPositions[0] + 1) % 6); //TODO eigene goClockwise methode schreiben, sonst muss man 'otherStart' wie hier mit etwas füllen das eigentlich algorithmisch unnötig ist weil der Output nie gegenüber liegen sollte
        if (core->outPositions[0] != outPosition[0]) {
           int currentPos = core->outPositions[0];
           if (clockwiseOutput) {
               while (currentPos != outPosition[0]) {
                   outerTiles[currentPos][1] = out1;
                   currentPos = (currentPos + 1) % 6;;
               }
           } else {
               do {
                   currentPos = mod((currentPos - 1), 6);
                   outerTiles[currentPos][1] = out1;
               } while (currentPos != outPosition[0]);
           }
        }

        //Connect inputs

        //Get the superTileConnections and the coreConnections in an order in which you can connect them without crossings
        //TODO optimierung durch sortierte Eingabe möglich?
        int coreIns[2];
        int superTileIns[2];
        int temp = 0;
        int pos = outPosition[0];
        //TODO beiden Suchen kombinieren
        while (temp < 2) { //core
            if (core->inPositions[0] == pos || core->inPositions[1] == pos) {
                coreIns[temp] = pos;
                temp++;
            }
            if (clockwiseOutput) {
                pos = (pos + 1 ) % 6;
            } else {
                pos = mod((pos - 1 ), 6);
            }
        }
        temp = 0;
        pos = outPosition[0];
        while (temp < 2) { //superTile
            if (inPositions[0] == pos || inPositions[1] == pos) {
                superTileIns[temp] = pos;
                temp++;
            }
            if (clockwiseOutput) {
                pos = (pos + 1 ) % 6;
            } else {
                pos = mod((pos - 1 ), 6);
            }
        }
        //Generate input path ...
        //number 1.
        outerTiles[coreIns[0]][0] = in1;
        outerTiles[superTileIns[0]][2] = in1;
        if (coreIns[0] != superTileIns[0]) {
            int currentPos = coreIns[0];
            if (goClockwise(coreIns[0], superTileIns[0], coreIns[1])) {
                while (currentPos != superTileIns[0]) {
                    outerTiles[currentPos][1] = in1;
                    currentPos = (currentPos + 1) % 6;
                }
            } else {
                do {
                    currentPos = mod((currentPos - 1), 6);
                    outerTiles[currentPos][1] = in1;
                } while (currentPos != superTileIns[0]);
            }
        }
        //number 2.
        outerTiles[coreIns[1]][0] = in2;
        outerTiles[superTileIns[1]][2] = in2;
        if (coreIns[1] != superTileIns[1]) {
            int currentPos = coreIns[1];
            if (goClockwise(coreIns[1], superTileIns[1], coreIns[0])) {
                while (currentPos != superTileIns[1]) {
                    outerTiles[currentPos][1] = in2;
                    currentPos = (currentPos + 1) % 6;
                }
            } else {
                do {
                    currentPos = mod((currentPos - 1), 6);
                    outerTiles[currentPos][1] = in2;
                } while (currentPos != superTileIns[1]);
            }
        }
    } else {
        printf("The given core name has not been found or a gate with this name is not available with 2 inputs and 1 output.\n");
        return NULL;
    }
    
    superTile* super = (superTile*) malloc(sizeof(superTile));
    super->core = core;
    super->wires = (gate**) malloc(sizeof(gate*)*6);

    //Get the wire-gates which are required on the outside
    for (int currentGate = 0; currentGate < 6; currentGate++) {
        int* currentWirePositions = getWireTileConnections(outerTiles, currentGate);
        if (currentWirePositions == NULL) {
            for (int x = 0; x < 6; x++) {
                free(outerTiles[x]);
            }
            free(outerTiles);
            for (int x = 0; x < currentGate; x++) {
                free(super->wires[x]);
            }
            free(super);
            return NULL;
        }

        gate* wireGate = (gate*) malloc(sizeof(gate));
    
        if (getWireTile(currentWirePositions, currentGate, wireGate)) {
            printf("A wire gate is required that is not yet implemented.\n");
            for (int x = 0; x < 6; x++) {
                free(outerTiles[x]);
            }
            free(outerTiles);
            for (int x = 0; x < currentGate; x++) {
                free(super->wires[x]);
            }
            free(super);
            free(wireGate);
            free(currentWirePositions);
            return NULL;
        }
        free(currentWirePositions);

        super->wires[currentGate] = wireGate;
    }

    if (printTheWirePaths) {
        printWirePaths(outerTiles, core); //Can be use for debugging
    }
   
    for (int x = 0; x < 6; x++) {
        free(outerTiles[x]);
    }
    free(outerTiles);

    return super;
}

//Returns a Y-shaped core gate that assumes it can be mirrored along the horizontal and vertical axis
gate* getYCore(int* inPositions, int* outPosition) {
    //TODO optimize by grouping the core position setting together, and maybe creating a truth table OR decision tree and have a switch statement, this may be the ugliest code I have ever written
    //TODO other/additional optimization could be to sort the in/outPositions bevorhand to reduce the ammount of if-statements
    gate* core = (gate*) malloc(sizeof(gate));
    core->outPositions = (int*) malloc(sizeof(int)*1);
    core->outPositionsSize = 1;
    core->inPositions = (int*) malloc(sizeof(int)*2);
    core->inPositionsSize = 2;

    if (outPosition[0] == 5) {
        if (inPositions[0] == 0 && inPositions[1] == 1 || inPositions[1] == 0 && inPositions[0] == 1) {
            core->outPositions[0] = 3;
            core->inPositions[0] = 0;
            core->inPositions[1] = 5;
        } else {
            core->outPositions[0] = 5;
            core->inPositions[0] = 2;
            core->inPositions[1] = 3;
        }
    } else if(outPosition[0] == 0) {
        if (inPositions[0] == 4 && inPositions[1] == 5 || inPositions[1] == 4 && inPositions[0] == 5) {
            core->outPositions[0] = 2;
            core->inPositions[0] = 0;
            core->inPositions[1] = 5;
        } else {
            core->outPositions[0] = 0;
            core->inPositions[0] = 2;
            core->inPositions[1] = 3;
        }
    } else if (outPosition[0] == 2) {
        if (inPositions[0] == 3 && inPositions[1] == 4 || inPositions[1] == 3 && inPositions[0] == 4) {
            core->outPositions[0] = 0;
            core->inPositions[0] = 2;
            core->inPositions[1] = 3;
        } else {
            core->outPositions[0] = 2;
            core->inPositions[0] = 0;
            core->inPositions[1] = 5;
        }
    } else if (outPosition[0] == 3) {
        if (inPositions[0] == 1 && inPositions[1] == 2 || inPositions[1] == 1 && inPositions[0] == 2) {
            core->outPositions[0] = 5;
            core->inPositions[0] = 2;
            core->inPositions[1] = 3;
        } else {
            core->outPositions[0] = 3;
            core->inPositions[0] = 0;
            core->inPositions[1] = 5;
        }
    } else if (outPosition[0] == 1) {
        if (inPositions[0] == 4) {
            if (inPositions[1] == 0 || inPositions[1] == 5) {
                core->outPositions[0] = 2;
                core->inPositions[0] = 0;
                core->inPositions[1] = 5;
            } else { //inPositions[1] == 2 || inPositions[1] == 3
                core->outPositions[0] = 0;
                core->inPositions[0] = 2;
                core->inPositions[1] = 3;
            }
        } else if (inPositions[1] == 4) {
            if (inPositions[0] == 0 || inPositions[0] == 5) {
                core->outPositions[0] = 2;
                core->inPositions[0] = 0;
                core->inPositions[1] = 5;
            } else { //inPositions[1] == 2 || inPositions[1] == 3
                core->outPositions[0] = 0;
                core->inPositions[0] = 2;
                core->inPositions[1] = 3;
            }
        } else if (inPositions[0] != 0 && inPositions[1] != 0) {
            core->outPositions[0] = 0;
            core->inPositions[0] = 2;
            core->inPositions[1] = 3;
        } else if (inPositions[0] != 2 && inPositions[1] != 2) {
            core->outPositions[0] = 2;
            core->inPositions[0] = 0;
            core->inPositions[1] = 5;
        } else {
            //This option and the same orientation, just mirrored by the horizontal axis would be ok
            core->outPositions[0] = 2;
            core->inPositions[0] = 0;
            core->inPositions[1] = 5;
        }
    } else { // outPosition[0] == 4
        if (inPositions[0] == 1) {
            if (inPositions[1] == 0 || inPositions[1] == 5) {
                core->outPositions[0] = 3;
                core->inPositions[0] = 0;
                core->inPositions[1] = 5;
            } else { //inPositions[1] == 2 || inPositions[1] == 3
                core->outPositions[0] = 5;
                core->inPositions[0] = 2;
                core->inPositions[1] = 3;
            }
        } else if (inPositions[1] == 1) {
            if (inPositions[0] == 0 || inPositions[0] == 5) {
                core->outPositions[0] = 3;
                core->inPositions[0] = 0;
                core->inPositions[1] = 5;
            } else { //inPositions[1] == 2 || inPositions[1] == 3
                core->outPositions[0] = 5;
                core->inPositions[0] = 2;
                core->inPositions[1] = 3;
            }
        } else if (inPositions[0] != 5 && inPositions[1] != 5) {
            core->outPositions[0] = 5;
            core->inPositions[0] = 2;
            core->inPositions[1] = 3;
        } else if (inPositions[0] != 3 && inPositions[1] != 3) {
            core->outPositions[0] = 3;
            core->inPositions[0] = 0;
            core->inPositions[1] = 5;
        } else {
            //This option and the same orientation, just mirrored by the horizontal axis would be ok
            core->outPositions[0] = 3;
            core->inPositions[0] = 0;
            core->inPositions[1] = 5;
        }
    }

    return core;
}

gate* getYCoreUpright(int* inPositions, int* outPosition) {
    //TODO this is a modified clone of the method above, both can be reduced by:
    //TODO optimize by grouping the core position setting together, and maybe creating a truth table OR decision tree and have a switch statement, this may be the ugliest code I have ever written
    //TODO other/additional optimization could be to sort the in/outPositions bevorhand to reduce the ammount of if-statements
    gate* core = (gate*) malloc(sizeof(gate));
    core->outPositions = (int*) malloc(sizeof(int)*1);
    core->outPositionsSize = 1;
    core->inPositions = (int*) malloc(sizeof(int)*2);
    core->inPositionsSize = 2;

    if (outPosition[0] == 5) {
        if (inPositions[0] == 0 && inPositions[1] == 1 || inPositions[1] == 0 && inPositions[0] == 1) {
            core->outPositions[0] = 3;
            core->inPositions[0] = 0;
            core->inPositions[1] = 5;
        } else {
            freeGate(core);
            return NULL;
        }
    } else if(outPosition[0] == 0) {
        if (inPositions[0] == 4 && inPositions[1] == 5 || inPositions[1] == 4 && inPositions[0] == 5) {
            core->outPositions[0] = 2;
            core->inPositions[0] = 0;
            core->inPositions[1] = 5;
        } else {
            freeGate(core);
            return NULL;
        }
    } else if (outPosition[0] == 2) {
        if (inPositions[0] == 3 && inPositions[1] == 4 || inPositions[1] == 3 && inPositions[0] == 4) {
            freeGate(core);
            return NULL;
        } else {
            core->outPositions[0] = 2;
            core->inPositions[0] = 0;
            core->inPositions[1] = 5;
        }
    } else if (outPosition[0] == 3) {
        if (inPositions[0] == 1 && inPositions[1] == 2 || inPositions[1] == 1 && inPositions[0] == 2) {
            freeGate(core);
            return NULL;
        } else {
            core->outPositions[0] = 3;
            core->inPositions[0] = 0;
            core->inPositions[1] = 5;
        }
    } else if (outPosition[0] == 1) {
        if (inPositions[0] == 4) {
            if (inPositions[1] == 0 || inPositions[1] == 5) {
                core->outPositions[0] = 2;
                core->inPositions[0] = 0;
                core->inPositions[1] = 5;
            } else { //inPositions[1] == 2 || inPositions[1] == 3
                freeGate(core);
                return NULL;
            }
        } else if (inPositions[1] == 4) {
            if (inPositions[0] == 0 || inPositions[0] == 5) {
                core->outPositions[0] = 2;
                core->inPositions[0] = 0;
                core->inPositions[1] = 5;
            } else { //inPositions[1] == 2 || inPositions[1] == 3
                freeGate(core);
                return NULL;
            }
        } else {
            //This option and the same orientation, just mirrored by the horizontal axis would be ok
            core->outPositions[0] = 2;
            core->inPositions[0] = 0;
            core->inPositions[1] = 5;
        }
    } else { // outPosition[0] == 4
        if (inPositions[0] == 1) {
            if (inPositions[1] == 0 || inPositions[1] == 5) {
                core->outPositions[0] = 3;
                core->inPositions[0] = 0;
                core->inPositions[1] = 5;
            } else { //inPositions[1] == 2 || inPositions[1] == 3
                freeGate(core);
                return NULL;
            }
        } else if (inPositions[1] == 1) {
            if (inPositions[0] == 0 || inPositions[0] == 5) {
                core->outPositions[0] = 3;
                core->inPositions[0] = 0;
                core->inPositions[1] = 5;
            } else { //inPositions[1] == 2 || inPositions[1] == 3
                freeGate(core);
                return NULL;
            }
        } else {
            //This option and the same orientation, just mirrored by the horizontal axis would be ok
            core->outPositions[0] = 3;
            core->inPositions[0] = 0;
            core->inPositions[1] = 5;
        }
    }

    return core;
}


superTile* solver1in1out(int* inPosition, int* outPosition, char* coreName, bool printTheWirePaths) {
    wireType** outerTiles = (wireType**) malloc(sizeof(wireType*)*6);
    for (int x = 0; x < 6; x++) {
        outerTiles[x] = (wireType*) malloc(sizeof(wireType)*3);
        for (int y = 0; y < 3; y++) {
            outerTiles[x][y] = NaW;
        }
    }

    gate* core;

    if (!strcmp(coreName, "WIRE")) {
        //Get best fitting core rotation
        core = (gate*) malloc(sizeof(gate));
        core->outPositions = (int*) malloc(sizeof(int)*1);
        core->outPositionsSize = 1;
        core->inPositions = (int*) malloc(sizeof(int)*1);
        core->inPositionsSize = 1;

        //core->name = coreName;
        int* inOutPositions = (int*) malloc(sizeof(int)*4);
        inOutPositions[0] = inPosition[0];
        inOutPositions[1] = outPosition[0];
        inOutPositions[2] = 42;
        
        getWireTile(inOutPositions, 5, core);
        free(inOutPositions);

        //Connect output
        outerTiles[core->outPositions[0]][0] = out1;
        outerTiles[outPosition[0]][2] = out1;

        //Connect input
        outerTiles[core->inPositions[0]][0] = in1;
        outerTiles[inPosition[0]][2] = in1;
    } else {
        printf("The given core name has not been found or a gate with this name is not available with 1 inputs and 1 output.\n");
        return NULL;
    }

        

    superTile* super = (superTile*) malloc(sizeof(superTile));
    super->core = core;
    super->wires = (gate**) malloc(sizeof(gate*)*6);

    //Get the wire-gates which are required on the outside
    for (int currentGate = 0; currentGate < 6; currentGate++) {
        int* currentWirePositions = getWireTileConnections(outerTiles, currentGate);
        if (currentWirePositions == NULL) {
            for (int x = 0; x < 6; x++) {
                free(outerTiles[x]);
            }
            free(outerTiles);
            for (int x = 0; x < currentGate; x++) {
                free(super->wires[x]);
            }
            free(super);
            return NULL;
        }

        gate* wireGate = (gate*) malloc(sizeof(gate));
        if(getWireTile(currentWirePositions, currentGate, wireGate)){
            printf("A wire gate is required that is not yet implemented.\n");
            for (int x = 0; x < 6; x++) {
                free(outerTiles[x]);
            }
            free(outerTiles);
            for (int x = 0; x < currentGate; x++) {
                free(super->wires[x]);
            }
            free(super);
            free(wireGate);
            free(currentWirePositions);
            return NULL;
        }
        free(currentWirePositions);
        //TODO combine the methods getWireTile() and giveWireGateName() (Besser gesagt man verschiebt giveWireGateName() in getWireTile()), there is no reason they should be seperate

        super->wires[currentGate] = wireGate;
    }
    
    if (printTheWirePaths) {
        printWirePaths(outerTiles, core); // can be used for debugging
    }
    
    for (int x = 0; x < 6; x++) {
        free(outerTiles[x]);
    }
    free(outerTiles);

    return super;
}

superTile* solver1in0out(int* inPosition, bool printTheWirePaths) {
    wireType** outerTiles = (wireType**) malloc(sizeof(wireType*)*6);
    for (int x = 0; x < 6; x++) {
        outerTiles[x] = (wireType*) malloc(sizeof(wireType)*3);
        for (int y = 0; y < 3; y++) {
            outerTiles[x][y] = NaW;
        }
    }

    gate* core;

    //Get best fitting core rotation
    core = (gate*) malloc(sizeof(gate));
    core->outPositions = (int*) malloc(sizeof(int)*1);
    core->outPositionsSize = 1;
    core->inPositions = (int*) malloc(sizeof(int)*1);
    core->inPositionsSize = 1;

    //core->name = coreName;
    int* inOutPositions = (int*) malloc(sizeof(int)*4);
    inOutPositions[0] = inPosition[0];
    inOutPositions[1] = (inPosition[0] + 3) % 6; //to trick the method into giving us a "straight" wire
    inOutPositions[2] = 42;
    
    getWireTile(inOutPositions, 5, core);
    free(inOutPositions);

    //Connect input
    outerTiles[core->inPositions[0]][0] = in1;
    outerTiles[inPosition[0]][2] = in1;

    superTile* super = (superTile*) malloc(sizeof(superTile));
    super->core = core;
    super->wires = (gate**) malloc(sizeof(gate*)*6);

    //Get the wire-gates which are required on the outside
    for (int currentGate = 0; currentGate < 6; currentGate++) {
        int* currentWirePositions = getWireTileConnections(outerTiles, currentGate);
        if (currentWirePositions == NULL) {
            for (int x = 0; x < 6; x++) {
                free(outerTiles[x]);
            }
            free(outerTiles);
            for (int x = 0; x < currentGate; x++) {
                free(super->wires[x]);
            }
            free(super);
            return NULL;
        }

        gate* wireGate = (gate*) malloc(sizeof(gate));
        if(getWireTile(currentWirePositions, currentGate, wireGate)){
            printf("A wire gate is required that is not yet implemented.\n");
            for (int x = 0; x < 6; x++) {
                free(outerTiles[x]);
            }
            free(outerTiles);
            for (int x = 0; x < currentGate; x++) {
                free(super->wires[x]);
            }
            free(super);
            free(wireGate);
            free(currentWirePositions);
            return NULL;
        }
        free(currentWirePositions);
        //TODO combine the methods getWireTile() and giveWireGateName() (Besser gesagt man verschiebt giveWireGateName() in getWireTile()), there is no reason they should be seperate

        super->wires[currentGate] = wireGate;
    }
    
    if (printTheWirePaths) {
        printWirePaths(outerTiles, core); // can be used for debugging
    }
    
    for (int x = 0; x < 6; x++) {
        free(outerTiles[x]);
    }
    free(outerTiles);

    return super;
}

//TODO Check truthtable and maybe even add it here for better understanding, or use it in the code ?!
//The coreOutput information is required so that the path doesn't cross it in edge-case-inputs like "./main SAMPLE 02 1"
bool goClockwise(int start, int end, int otherStart) {
    //start == end should never happen, method is not constructed for that. Maybe fix that? But shouldn't be neccessary
    if (start > end) {
        if (start - end > 3) {
            return true;
        } else if (start - end == 3 && otherStart != (start + 1) % 6) { //This was written for classical Y shaped gates, this can either be optimized for them or the whole Method can be generalized so that it works with other gates (then you have to check "(start + 2) % 6" also)
            return true;
        } else {
            return false;
        }
    } else {
        if (end - start > 3) {
            return false;
        } else if (end - start == 3 && otherStart == (start + 1) % 6) { //This was written for classical Y shaped gates, this can either be optimized for them or the whole Method can be generalized so that it works with other gates (then you have to check "(start + 2) % 6" also)
            return false;
        } else {
            return true;
        }
    }
}

//Modulus that can handle negative numbers
int mod(int k, int n) {
    return ((k %= n) < 0) ? k+n : k;
}

//Returns NULL when error happens
int* getWireTileConnections(wireType** outerTiles, int tile) {
    //get Positions for each wire (the positions 0 to 3 numbered clockwise, starting with 0 for the position of the connections to another supertile)
    //                            (this makes the calculations in getWireTile() easier)
    wireType firstType = NaW;
    int firstPosition[2];
    int firstCount = 0;
    wireType secondType = NaW;
    int secondPosition[2];
    int secondCount = 0;

    if (outerTiles[mod(tile - 1, 6)][1] != NaW) {
        firstType = outerTiles[mod(tile - 1, 6)][1];
        firstPosition[0] = 3;
        firstCount = 1;
    }
    if (outerTiles[tile][0] != NaW) {
        if (firstCount == 0) {
            firstType = outerTiles[tile][0];
            firstPosition[0] = 2;
            firstCount = 1;
        } else if (outerTiles[tile][0] == firstType) {
            firstPosition[1] = 2;
            firstCount = 2;
        } else {
            secondType = outerTiles[tile][0];
            secondPosition[0] = 2;
            secondCount = 1;
        }
    }
    if (outerTiles[tile][1] != NaW) {
        if (firstCount == 0) {
            firstType = outerTiles[tile][1];
            firstPosition[0] = 1;
            firstCount = 1;
        } else if (outerTiles[tile][1] == firstType && firstCount < 2) {
            firstPosition[firstCount] = 1;
            firstCount++;
        } else if (secondCount == 0) {
            secondType = outerTiles[tile][1];
            secondPosition[0] = 1;
            secondCount = 1;
        } else if (outerTiles[tile][1] == secondType) {
            secondPosition[1] = 1;
            secondCount = 2;
        } else {
            printf("ERROR Third wire in a tile or tile with wire with more then 3 connections found, this means the supertile layout generation was faulty.\n");
            return NULL;
        }
    }
    if (outerTiles[tile][2] != NaW) {
        if (firstCount == 0) {
            firstCount = 1; //Nothing more needed here, is just here to throw the error in the following check.
        } else if (outerTiles[tile][2] == firstType && firstCount < 2) {
            firstPosition[firstCount] = 0;
            firstCount++;
        }  else if (secondCount == 0) {
            secondCount = 1; //Nothing more needed here, is just here to throw the error in the following check.
        } else if (outerTiles[tile][2] == secondType && secondCount < 2) {
            secondPosition[secondCount] = 0;
            secondCount++;
        } else {
            printf("ERROR Third wire in a tile or tile with wire with more then 3 connections found, this means the supertile layout generation was faulty.\n");
            return NULL;
        }
    }

    //Check if there are two connections for each wire
    if (firstCount == 1 || secondCount == 1) {
        printf("ERROR impossible tile with a wire with just one connections was found.\n");
        return NULL;
    }

    //Check if a wire has three or more connections
    if (firstCount > 2 || secondCount > 2) {
        printf("ERROR impossible tile with a wire with three ore more connections was found.\n");
        return NULL;
    }

    int* connectionPositions = (int*) malloc(sizeof(int)*4);
    if (firstCount == 0) {
        connectionPositions[0] = 42; //Represents empty connectionsPositons array and by extension, an empty tile (42 was chosen because it is the answer the Ultimate Question of Life, the Universe, and Everything.)
    } else if (secondCount == 0) {
        connectionPositions[0] = firstPosition[0];
        connectionPositions[1] = firstPosition[1];
        connectionPositions[2] = 42;
    } else {
        connectionPositions[0] = firstPosition[0];
        connectionPositions[1] = firstPosition[1];
        connectionPositions[2] = secondPosition[0];
        connectionPositions[3] = secondPosition[1];
    }
    
    return connectionPositions;
}

//This method also sets the in/out connections in the gate it is given, returns true when error happend
bool getWireTile(int* connectionPositions, int tile, gate* wireGate) {
    wire name;
    if (connectionPositions[0] == 42) { // => Empty array
        name = empty;
    } else {
        //Getting the "true" positions of the tile in question
        int trueFirstA = (connectionPositions[0] + (tile + 1)) % 6;
        int trueFirstB = (connectionPositions[1] + (tile + 1)) % 6;
        int trueFirstCombi = trueFirstA * 10 + trueFirstB;

        wire firstWire = empty;
        switch (trueFirstCombi) //TODO maybe make this switch it's own method to have cleaner code
                                //TODO maybe sort the wire bevorehand to have less cases and more optimal code ?!
        {
        case 01:
        case 10:
            firstWire = wire01;
            break;
        case 02:
        case 20:
            firstWire = wire02;
            break;
        case 03:
        case 30:
            firstWire = wire03;
            break;
        case 04:
        case 40:
            firstWire = wire04;
            break;
        case 05:
        case 50:
            firstWire = wire05;
            break;
        case 12:
        case 21:
            firstWire = wire12;
            break;
        case 13:
        case 31:
            firstWire = wire13;
            break;
        case 14:
        case 41:
            firstWire = wire14;
            break;
        case 15:
        case 51:
            firstWire = wire15;
            break;
        case 23:
        case 32:
            firstWire = wire23;
            break;
        case 24:
        case 42:
            firstWire = wire24;
            break;
        case 25:
        case 52:
            firstWire = wire25;
            break;
        case 34:
        case 43:
            firstWire = wire34;
            break;
        case 35:
        case 53:
            firstWire = wire35;
            break;
        case 45:
        case 54:
            firstWire = wire45;
            break;
        default:
            //TODO have error here, this should be impossible
            break;
        }

        if (connectionPositions[2] == 42) {
            wireGate->inPositions = (int*) malloc(sizeof(int)*1);
            wireGate->inPositionsSize = 1;
            wireGate->outPositions = (int*) malloc(sizeof(int)*1);
            wireGate->outPositionsSize = 1;
            wireGate->inPositions[0] = trueFirstA;
            wireGate->outPositions[0] = trueFirstB;
            name = firstWire;
        } else {
            //Getting the "true" positions of the tile in question
            int trueSecondA = (connectionPositions[2] + (tile + 1)) % 6;
            int trueSecondB = (connectionPositions[3] + (tile + 1)) % 6;
            int trueSecondCombi = trueSecondA * 10 + trueSecondB;

            wire secondWire = empty; //TODO empty should be removable, but 
            switch (trueSecondCombi) //TODO maybe makes this switch it's own method to have cleaner code
                                     //TODO maybe sort the wire bevorehand to have less cases and more optimal code ?!
            {
            case 01:
            case 10:
                secondWire = wire01;
                break;
            case 02:
            case 20:
                secondWire = wire02;
                break;
            case 03:
            case 30:
                secondWire = wire03;
                break;
            case 04:
            case 40:
                secondWire = wire04;
                break;
            case 05:
            case 50:
                secondWire = wire05;
                break;
            case 12:
            case 21:
                secondWire = wire12;
                break;
            case 13:
            case 31:
                secondWire = wire13;
                break;
            case 14:
            case 41:
                secondWire = wire14;
                break;
            case 15:
            case 51:
                secondWire = wire15;
                break;
            case 23:
            case 32:
                secondWire = wire23;
                break;
            case 24:
            case 42:
                secondWire = wire24;
                break;
            case 25:
            case 52:
                secondWire = wire25;
                break;
            case 34:
            case 43:
                secondWire = wire34;
                break;
            case 35:
            case 53:
                secondWire = wire35;
                break;
            case 45:
            case 54:
                secondWire = wire45;
                break;
            default:
                //TODO have error here, this should be impossible
                break;
            }

            wireGate->inPositions = (int*) malloc(sizeof(int)*2);
            wireGate->inPositionsSize = 2;
            wireGate->outPositions = (int*) malloc(sizeof(int)*2);
            wireGate->outPositionsSize = 2;
            wireGate->inPositions[0] = trueFirstA;
            wireGate->outPositions[0] = trueFirstB;
            wireGate->inPositions[1] = trueSecondA;
            wireGate->outPositions[1] = trueSecondB;
            //Try to combine the two wires
            name = (wire) (firstWire + secondWire);
        }
    }

    if (!giveWireGateName(name, wireGate)) {
        return true;
    }

    return false; //represents a successfull execution
}

//Returns true if a wiregate with this name is implemented, false otherwise (Not all wires in this function have been implemented so far, but for testing it was assumend that they would be possible)
bool giveWireGateName(wire wireName, gate* wireGate) {
    switch (wireName)
    {
    case empty:
        wireGate->name = "empty";
        return true;
    case wire01:
        wireGate->name = "wire01";
        return true; 
    case wire02:
        wireGate->name = "wire02";
        return true;
    case wire03:
        wireGate->name = "wire03";
        return true;
    case wire04:
        wireGate->name = "wire04";
        return true;
    case wire05:
        wireGate->name = "wire05";
        return true;
    case wire12:
        wireGate->name = "wire12";
        return true;
    case wire13:
        wireGate->name = "wire13";
        return true;
    case wire14:
        wireGate->name = "wire14";
        return true;
    case wire15:
        wireGate->name = "wire15";
        return true;
    case wire23:
        wireGate->name = "wire23";
        return true;
    case wire24:
        wireGate->name = "wire24";
        return true;
    case wire25:
        wireGate->name = "wire25";
        return true;
    case wire34:
        wireGate->name = "wire34";
        return true;
    case wire35:
        wireGate->name = "wire35";
        return true;
    case wire45:
        wireGate->name = "wire45";
        return true;
    case wire14_23:
        wireGate->name = "wire14_23";
        return true;
    case wire25_34:
        wireGate->name = "wire25_34";
        return true;
    case wire03_45:
        wireGate->name = "wire03_45";
        return true;
    case wire14_05:
        wireGate->name = "wire14_05";
        return true;
    case wire25_01:
        wireGate->name = "wire25_01";
        return true;
    case wire03_12:
        wireGate->name = "wire03_12";
        return true;
    case wire12_34:
        wireGate->name = "wire12_34";
        return true;
    case wire23_45:
        wireGate->name = "wire23_45";
        return true;
    case wire34_05:
        wireGate->name = "wire34_05";
        return true;
    case wire45_01:
        wireGate->name = "wire45_01";
        return true;
    case wire05_12:
        wireGate->name = "wire05_12";
        return true;
    case wire01_23:
        wireGate->name = "wire01_23";
        return true;
    default:
        return false;
    }
}

//Mainly used for debugging
void printWirePaths(wireType** outerTiles, gate* core) {
    printf("Wire Paths:\n\n");
    printf("         ˍ---¯¯¯-%c-ˍ ˍ---¯¯¯---ˍ             The paths are not depicted directly, but at each position where a path corsses\n", getWireTypeSynonymA(outerTiles[5][2]));
    printf("        |           |           |            the border of a tile, a corresponding character is displayed.\n");
    printf("        |    (5)    %c    (0)    %c            (So to see the paths you have to trace a line along each type of character.)\n", getWireTypeSynonymB(outerTiles[5][1]), getWireTypeSynonymB(outerTiles[0][2]));
    printf("        |           |           |            \n");
    printf("   ˍ-%c-¯ ¯-%c-ˍ ˍ-%c-¯ ¯-%c-ˍ ˍ-%c-¯ ¯---ˍ       The characters meaning:\n", getWireTypeSynonymA(outerTiles[4][2]), getWireTypeSynonymA(outerTiles[4][1]), getWireTypeSynonymA(outerTiles[5][0]), getWireTypeSynonymA(outerTiles[0][0]), getWireTypeSynonymA(outerTiles[0][1]));
    printf("  |           |           |           |      I -> first input wire\n");
    printf("  |    (4)    %c   (Core)  %c    (1)    |      i -> second input wire\n", getWireTypeSynonymB(outerTiles[4][0]), getWireTypeSynonymB(outerTiles[1][0]));
    printf("  |           |           |           |      O -> first output wire\n");
    printf("   ¯---ˍ ˍ-%c-¯ ¯-%c-ˍ ˍ-%c-¯ ¯-%c-ˍ ˍ-%c-¯       o -> second output wire (not used so far)\n", getWireTypeSynonymA(outerTiles[3][1]), getWireTypeSynonymA(outerTiles[3][0]), getWireTypeSynonymA(outerTiles[2][0]), getWireTypeSynonymA(outerTiles[1][1]), getWireTypeSynonymA(outerTiles[1][2]));
    printf("        |           |           |          \n");
    printf("        %c    (3)    %c    (2)    |        \n", getWireTypeSynonymB(outerTiles[3][2]), getWireTypeSynonymB(outerTiles[2][1]));
    printf("        |           |           |\n");
    printf("         ¯---ˍˍˍ---¯ ¯-%c-ˍˍˍ---¯\n\n", getWireTypeSynonymA(outerTiles[2][2]));
}

char getWireTypeSynonymA(wireType wire) {
    switch (wire)
    {
    case out1:
        return 'O';
    case out2:
        return 'o';
    case in1:
        return 'I';
    case in2:
        return 'i';
    default:
        return '-';
    }
}

char getWireTypeSynonymB(wireType wire) {
    switch (wire)
    {
    case out1:
        return 'O';
    case out2:
        return 'o';
    case in1:
        return 'I';
    case in2:
        return 'i';
    default:
        return '|';
    }
}

void printLayout(superTile* finishedLayout) {
    char* name = (char*) malloc(sizeof(char)*10);
    char* inputs = (char*) malloc(sizeof(char)*10);
    char* outputs = (char*) malloc(sizeof(char)*10);

    printf("Finished Layout:\n\n");
    printf("         ˍ---¯¯¯---ˍ ˍ---¯¯¯---ˍ             Used gates:\n");
    printf("        |           |           |\n");
    printf("        |    (5)    |    (0)    |              Position  |   Name    |  Inputs   |  Outputs  \n");
    printf("        |           |           |            ------------|-----------|-----------|-----------\n");
    setNormalisedString(finishedLayout->core->name, name);
    setNormalisedNumbers(finishedLayout->core->inPositions, finishedLayout->core->inPositionsSize, inputs);
    setNormalisedNumbers(finishedLayout->core->outPositions, finishedLayout->core->outPositionsSize, outputs);
    printf("   ˍ---¯ ¯---ˍ ˍ---¯ ¯---ˍ ˍ---¯ ¯---ˍ        (Core)     | %s| %s| %s\n", name, inputs, outputs);
    setNormalisedString(finishedLayout->wires[0]->name, name);
    setNormalisedNumbers(finishedLayout->wires[0]->inPositions, finishedLayout->wires[0]->inPositionsSize, inputs);
    setNormalisedNumbers(finishedLayout->wires[0]->outPositions, finishedLayout->wires[0]->outPositionsSize, outputs);
    printf("  |           |           |           |       (0)        | %s| %s| %s\n", name, inputs, outputs);
    setNormalisedString(finishedLayout->wires[1]->name, name);
    setNormalisedNumbers(finishedLayout->wires[1]->inPositions, finishedLayout->wires[1]->inPositionsSize, inputs);
    setNormalisedNumbers(finishedLayout->wires[1]->outPositions, finishedLayout->wires[1]->outPositionsSize, outputs);
    printf("  |    (4)    |   (Core)  |    (1)    |       (1)        | %s| %s| %s\n", name, inputs, outputs);
    setNormalisedString(finishedLayout->wires[2]->name, name);
    setNormalisedNumbers(finishedLayout->wires[2]->inPositions, finishedLayout->wires[2]->inPositionsSize, inputs);
    setNormalisedNumbers(finishedLayout->wires[2]->outPositions, finishedLayout->wires[2]->outPositionsSize, outputs);
    printf("  |           |           |           |       (2)        | %s| %s| %s\n", name, inputs, outputs);
    setNormalisedString(finishedLayout->wires[3]->name, name);
    setNormalisedNumbers(finishedLayout->wires[3]->inPositions, finishedLayout->wires[3]->inPositionsSize, inputs);
    setNormalisedNumbers(finishedLayout->wires[3]->outPositions, finishedLayout->wires[3]->outPositionsSize, outputs);
    printf("   ¯---ˍ ˍ---¯ ¯---ˍ ˍ---¯ ¯---ˍ ˍ---¯        (3)        | %s| %s| %s\n", name, inputs, outputs);
    setNormalisedString(finishedLayout->wires[4]->name, name);
    setNormalisedNumbers(finishedLayout->wires[4]->inPositions, finishedLayout->wires[4]->inPositionsSize, inputs);
    setNormalisedNumbers(finishedLayout->wires[4]->outPositions, finishedLayout->wires[4]->outPositionsSize, outputs);
    printf("        |           |           |             (4)        | %s| %s| %s\n", name, inputs, outputs);
    setNormalisedString(finishedLayout->wires[5]->name, name);
    setNormalisedNumbers(finishedLayout->wires[5]->inPositions, finishedLayout->wires[5]->inPositionsSize, inputs);
    setNormalisedNumbers(finishedLayout->wires[5]->outPositions, finishedLayout->wires[5]->outPositionsSize, outputs);
    printf("        |    (3)    |    (2)    |             (5)        | %s| %s| %s\n", name, inputs, outputs);
    printf("        |           |           |\n");
    printf("         ¯---ˍˍˍ---¯ ¯---ˍˍˍ---¯\n\n");

    free(name);
    free(inputs);
    free(outputs);
}

void setNormalisedString(const char* name, char* normalised) {
    int x;
    for (x = 0; x < strlen(name); x++) {
        normalised[x] = name[x];
    }
    for (x; x < 10; x++) {
        normalised[x] = ' ';
    }
}

void setNormalisedNumbers(int* positions, int positionsSize, char* normalised) {
    int x;
    for (x = 0; x < positionsSize * 2; x = x + 2) {
        normalised[x] = (char) (positions[x/2] + 48);
        normalised[x+1] = ' ';
    }
    for (x; x < 10; x++) {
        normalised[x] = ' ';
    }
}

/** The core naming system is defined such that the numbers 1-4 represent to following core input/output layouts:
*    \ /      \ /      \          /
* 1:  O    2:  O    3:  O    4:  O
*    /          \      / \      / \
*/
void printReducedLayout(superTile* layout) {
    if (layout->core->outPositionsSize > 1) {
        printf("Core orientation output still has to be implemented for coregates with more then one output");
        printf("%s, %s, %s, %s, %s, %s, %s", layout->core->name, layout->wires[0]->name, layout->wires[1]->name, layout->wires[2]->name, layout->wires[3]->name, layout->wires[4]->name, layout->wires[5]->name);
    } else {
        std::string coreName = layout->core->name;
        if (std::string::npos == (coreName.find("wire")) && std::string::npos == (coreName.find("WIRE"))) {
            switch (layout->core->outPositions[0]) {
                case 3:
                    coreName += "_3";
                    break;
                case 2:
                    coreName += "_2";
                    break;
                case 5:
                    coreName += "_5";
                    break;
                case 0:
                    coreName += "_0";
                    break;
                default:
                    coreName += "_Unknown core orientation";
                    break;
            }
        }
        printf("%s, %s, %s, %s, %s, %s, %s", coreName.c_str(), layout->wires[0]->name, layout->wires[1]->name, layout->wires[2]->name, layout->wires[3]->name, layout->wires[4]->name, layout->wires[5]->name);
    }
}

void freeGate(gate* toFree) {
    free(toFree->inPositions);
    free(toFree->outPositions);
    free(toFree);
}