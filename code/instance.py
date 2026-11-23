def read_dat(path):
    data = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line == "":
                continue

            # TODO 1: del linja i navn og verdi ved "="
            name, value = line.split("=")
            # TODO 2: fjern mellomrom rundt begge, og ";" fra verdien
            name = name.strip()
            value = value.strip().rstrip(";")
            # TODO 3: hvis verdien starter med "[", er det en liste:
            #         fjern [ ], del opp, gjør hver bit om til int
            #         ellers: gjør verdien om til én int
            if value.startswith("["):
                value = value.strip("[]")          # "1 9 1 3 4 5"
                value = value.split()              # ["1", "9", "1", "3", "4", "5"]
                value = [int(i) for i in value]    # [1, 9, 1, 3, 4, 5]
            else:
                value = int(value)
            # TODO 4: lagre i data[navn]
            data[name] = value

    return data


if __name__ == "__main__":
    print(read_dat("project/project.1.dat"))
