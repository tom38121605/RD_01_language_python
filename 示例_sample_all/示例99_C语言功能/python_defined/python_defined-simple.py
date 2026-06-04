

DEFINES = \
{
    # "MODE_X": True,
    "MODE_XYZ": True,
}

def defined(macro_name):
    is_defined = macro_name in DEFINES
    return is_defined

if defined("MODE_X"):
    print("use x")

elif defined("MODE_XYZ"):
    print("use xyz")

