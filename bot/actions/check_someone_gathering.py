someone_gathering_template_path = "assets/template/someone_gathering.png"


def check_someone_gathering(adb):
    loc = adb.find(someone_gathering_template_path)
    if loc is not None:
        print("Someome is gathering now!")
        return "someone_gathering"
    return "gatherable"
