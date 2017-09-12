import os
import shutil

import PIL.Image as Image
import PIL.ImageDraw as ImageDraw

def analysis(simulationName):
    print(f"{simulationName}: analysis setup")

    def tickCreatureList(tick, number=-1):
        L = []
        for i in datiCreature:
            if i[1] <= tick and i[12] >= tick:
                if number != -1:
                    L.append(i[number])
                else:
                    L.append(i)
        return sorted(L)

    def tempNumber(x):
        if x == "N" or x == "n":
            return 0

        elif x == "l":
            return 1

        elif x == "c":
            return 2

    print(f"{simulationName}: files and data initialization")
    print(f"        - importing files")
    try:
        simulationData = open(f"{simulationName}/simulationData.csv").readline().split(';')
        chunkData = open(f"./{simulationName}/chunkData.csv")
        creaturesData = open(f"./{simulationName}/creaturesData.csv")
    except FileNotFoundError:
        print("ERROR: Simulation not found")
        exit()

    # salviamo i dati della simulazione
    print(f"        - importing simulation data")
    width = int(simulationData[1])
    height = int(simulationData[2])
    lifetime = int(simulationData[3]) + 1
    chunkDim = int(simulationData[5])
    datiChunk = [[None for x in range(0, height, chunkDim)] for y in range(0, width, chunkDim)]

    # salviamo i dati delle creature
    print(f"        - importing creatures data")
    datiCreature = []
    for riga in creaturesData:
        listaDati = riga.split(";")
        for i in [0, 1, 6, 12]:
            listaDati[i] = int(listaDati[i])
        for i in [4, 5, 7, 9, 10, 11]:
            listaDati[i] = float(listaDati[i])
        listaDati[2] = (int(listaDati[2].split(",")[0]), int(listaDati[2].split(",")[1]))
        listaDati[14] = listaDati[14].split("/")
        for i in range(len(listaDati[14])):
            listaDati[14][i] = listaDati[14][i].split(",")
            try:
                for j in [0, 1]:
                    listaDati[14][i][j] = float(listaDati[14][i][j])
                for j in [2, 3]:
                    listaDati[14][i][j] = int(listaDati[14][i][j])
            except ValueError:
                listaDati[14] = [[]]
        datiCreature.append(listaDati)

    # salviamo i dati dei chunk
    print(f"        - importing chunk data")
    for riga in chunkData:
        listaDati = [0, 0, 0]
        riga = riga.split(';')
        listaDati[0] = float(riga[2])
        listaDati[1] = float(riga[3])
        listaDati[2] = float(riga[4])
        datiChunk[int(riga[0])][int(riga[1])] = listaDati

    # analisi caratteristiche
    print(f"{simulationName}: genes analysis")
    names = ["agility", "bigness", "fertility", "speed", "eatCoeff", "numControlGene"]
    j = 0
    for k in [4, 5, 7, 9, 10, 11]:
        f = open(f"{simulationName}/{names[j]}.csv", "w")
        for i in range(0, lifetime, 100):
            l = tickCreatureList(i, k)
            f.write(f"{i};{l[0]};{l[round(len(l)/4)]};{l[round(len(l)/2)]};{l[-round(len(l)/4)]};{l[-1]};{sum(l)/float(len(l))}\n")
        f.close()
        j += 1

    f = open(f"{simulationName}/population.csv", "w")
    for i in range(0, lifetime, 100):
        deaths = [0, 0, 0]
        born = 0
        for j in datiCreature:
            if j[1] >= i and j[1] < i + 100:
                born += 1
            if j[12] >= i and j[12] < i + 100:
                if j[13] == "s":
                    deaths[0] += 1
                elif j[13] == "t":
                    deaths[1] += 1
                elif j[13] == "a":
                    deaths[2] += 1
        f.write(f"{i};{born};{deaths[0]};{deaths[1]};{deaths[2]}\n")
    f.close()

    f = open(f"{simulationName}/chunkFoodMax.csv", "w")
    g = open(f"{simulationName}/chunkTemp.csv", "w")
    """
    foodMaxClass = [0, 0, 0, 0, 0, 0, 0, 0]
    tempClass = [0, 0, 0, 0, 0, 0, 0, 0]
    """
    foodMaxClass = []
    tempClass = []
    for i in range(8):
        foodMaxClass.append(0)
        tempClass.append(0)
    for i in datiChunk:
        for j in i:
            foodMax = min(j[0], 99)
            temperatura = min(j[2], 99)
            foodMaxClass[int(foodMax / 12.5)] += 1
            tempClass[int((temperatura + 100) / 25)] += 1
    foodMaxClass_string = f"{foodMaxClass[0]}"
    tempClass_string = f"{tempClass[0]}"
    for i in range(1,8):
        foodMaxClass_string += f";{foodMaxClass[i]}"
        tempClass_string += f";{tempClass[i]}"
    f.write(f"{foodMaxClass_string}\n")
    g.write(f"{tempClass_string}\n")
    f.close()

    # analisi disposizione
    print(f"{simulationName}: spreading and deaths analysis")
    fN = open(f"{simulationName}/spread_temperature_N.csv", "w")
    fc = open(f"{simulationName}/spread_temperature_c.csv", "w")
    fl = open(f"{simulationName}/spread_temperature_l.csv", "w")
    ff = open(f"{simulationName}/spread_foodmax.csv", "w")
    for i in range(0, lifetime, 100):
        l = tickCreatureList(i)
        numberCreatureTemp = [[0 for x in range(8)] for y in range(3)]
        correctCreatureTemp = [[0 for x in range(8)] for y in range(3)]
        numberCreatureFood = [0 for x in range(8)]
        correctCreatureFood = [0 for x in range(8)]
        for j in l:
            birth = max(j[1], 1)
            coord = (j[14][i - birth][0], j[14][i - birth][1])
            chunkCoord = (int(coord[0] / chunkDim), int(coord[1] / chunkDim))
            temperatura = min(datiChunk[chunkCoord[0]][chunkCoord[1]][2], 99)
            foodMax = min(datiChunk[chunkCoord[0]][chunkCoord[1]][0], 99)
            numberCreatureTemp[tempNumber(j[8])][int((temperatura + 100) / 25)] += 1
            numberCreatureFood[int(foodMax / 12.5)] += 1

        for j in range(8):
            correctCreatureFood[j] = numberCreatureFood[j] / foodMaxClass[j] * 100
            for k in range(3):
                correctCreatureTemp[k][j] = numberCreatureTemp[k][j] / tempClass[j] * 100
        fN_string = f"{i}"
        fl_string = f"{i}"
        fc_string = f"{i}"
        ff_string = f"{i}"
        for i in range(8):
            fN_string += f";{numberCreatureTemp[0][i]};{correctCreatureTemp[0][i]}"
            fl_string += f";{numberCreatureTemp[1][i]};{correctCreatureTemp[1][i]}"
            fc_string += f";{numberCreatureTemp[2][i]};{correctCreatureTemp[2][i]}"
            ff_string += f";{numberCreatureTemp[i]};{correctCreatureTemp[i]}"
        fN.write(f"{fN_string}\n")
        fl.write(f"{fl_string}\n")
        fc.write(f"{fc_string}\n")
        ff.write(f"{ff_string}\n")
    fN.close()
    fc.close()
    fl.close()
    ff.close()
    os.chdir(simulationName)
    for name in ["TempFrames", "FoodMaxFrames"]:
        try:
            os.makedirs(name)
        except FileExistsError:
            shutil.rmtree(name)
            os.makedirs(name)

    for tick in range(0, lifetime, 100):
        imageFood = Image.new("RGB", (width, height))
        drawFood = ImageDraw.Draw(imageFood)
        imageTemp = Image.new("RGB", (width, height))
        drawTemp = ImageDraw.Draw(imageTemp)

        for i in range(len(datiChunk)):
            for j in range(len(datiChunk[i])):
                drawFood.rectangle((i * chunkDim, j * chunkDim, (i + 1) * chunkDim, (j + 1) * chunkDim), fill=(0, int(datiChunk[i][j][0]), 0), outline="black")

        for i in tickCreatureList(tick):
            birth = max(i[1], 1)
            coord = (i[14][tick - birth][0], i[14][tick - birth][1])
            energy = i[14][tick - birth][2]
            drawFood.ellipse((coord[0] - energy / 20, coord[1] - energy / 20, coord[0] + energy / 20, coord[1] + energy / 20), fill=(255, 0, 0), outline="black")

        for i in range(len(datiChunk)):
            for j in range(len(datiChunk[i])):
                temperature = datiChunk[i][j][2]
                if temperature > 0:
                    drawTemp.rectangle((i * chunkDim, j * chunkDim, (i + 1) * chunkDim, (j + 1) * chunkDim), fill=(255, int(255 - (temperature / 100 * 255)), int(255 - (temperature / 100 * 255))), outline="black")
                else:
                    drawTemp.rectangle((i * chunkDim, j * chunkDim, (i + 1) * chunkDim, (j + 1) * chunkDim), fill=(int(255 + (temperature / 100 * 255)), int(255 + (temperature / 100 * 255)), 255), outline="black")

        for i in tickCreatureList(tick):
            birth = max(i[1], 1)
            coord = (i[14][tick - birth][0], i[14][tick - birth][1])
            energy = i[14][tick - birth][2]
            x = i[8]
            if x == "N" or x == "n":
                drawTemp.ellipse((coord[0] - energy / 20, coord[1] - energy / 20, coord[0] + energy / 20, coord[1] + energy / 20), fill=(255, 255, 255), outline="black")

            elif x == "l":
                drawTemp.ellipse((coord[0] - energy / 20, coord[1] - energy / 20, coord[0] + energy / 20, coord[1] + energy / 20), fill=(0, 0, 255), outline="black")

            elif x == "c":
                drawTemp.ellipse((coord[0] - energy / 20, coord[1] - energy / 20, coord[0] + energy / 20, coord[1] + energy / 20), fill=(255, 0, 0), outline="black")
        imageFood.save(f"FoodMaxFrames/FrameF{tick}.jpg", "JPEG")
        imageTemp.save(f"TempFrames/FrameT{tick}.jpg", "JPEG")
        del imageTemp, imageFood, drawFood, drawTemp
    os.chdir("..")
