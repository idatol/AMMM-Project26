import re


def read_dat(path):
    with open(path) as f:
        text = f.read()

    # Remove comments: /* ... */ and // ...
    text = re.sub(r"/\*.*?\*/|//[^\n]*", "", text, flags=re.DOTALL)

    data = {}
    for statement in text.split(";"):
        statement = statement.strip()
        if statement == "":
            continue

        name, value = statement.split("=")
        name = name.strip()
        value = value.strip()

        if value.startswith("["):
            # OPL allows both spaces and commas between the numbers
            value = value.strip("[]").replace(",", " ").split()
            value = [int(i) for i in value]
        else:
            value = int(value)

        data[name] = value

    return data


if __name__ == "__main__":
    print(read_dat("project/project.1.dat"))
